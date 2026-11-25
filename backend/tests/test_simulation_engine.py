"""
Sprint 2 Acceptance Verification Test Suite (AC-01 to AC-10)
Role: QA Automation & Acceptance Verification Lead (Soumya)
Project: RE:Flow — Team Photon

Purpose:
Independently verify acceptance criteria AC-01 through AC-10 for the Sprint 2
disruption simulation pipeline, ensuring correct business logic, robust input
validation, exact order breach classification, and valid API integration.
"""

from __future__ import annotations

import copy
import pytest
from fastapi.testclient import TestClient

from backend.app.data.loader import load_scenario_dataset
from backend.app.graph.builder import build_graph
from backend.app.main import app
from backend.app.models.disruption import DisruptionEvent, DisruptionType
from backend.app.models.stockout import BreachedOrder, StockoutPredictionResult
from backend.app.services.simulation_service import simulation_service
from backend.app.simulation.engine import run_disruption_simulation
from backend.app.simulation.events import create_disruption_event
from backend.app.simulation.intervention import calculate_intervention_window
from backend.app.simulation.inventory import simulate_inventory_depletion
from backend.app.simulation.ripple import propagate_ripple_effect
from backend.app.simulation.stockout import predict_stockout_and_orders


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scenario_data():
    """Load pristine canonical scenario dataset."""
    return load_scenario_dataset()


@pytest.fixture
def fresh_graph(scenario_data):
    """Provide a fresh NetworkX DiGraph instance for testing."""
    return build_graph(copy.deepcopy(scenario_data))


@pytest.fixture
def api_client():
    """Provide a FastAPI test client for API integration tests."""
    with TestClient(app) as client:
        yield client


# ===========================================================================
# AC-01: Disruption Event Creation
# ===========================================================================

def test_ac01_create_valid_8hr_disruption_event():
    """Verify an 8-hour supplier disruption event is created with valid attributes."""
    event = create_disruption_event(
        supplier_id="SUP-01",
        disruption_type=DisruptionType.SUPPLIER_DELAY,
        delay_duration_hours=8.0,
        description="Official 8-hour benchmark delay on primary electronics supplier",
    )

    assert event.supplier_id == "SUP-01", "Event supplier ID must match input 'SUP-01'"
    assert event.disruption_type == DisruptionType.SUPPLIER_DELAY, "Disruption type must be SUPPLIER_DELAY"
    assert event.delay_duration_hours == 8.0, "Delay duration must be exactly 8.0 hours"
    assert event.event_id is not None and len(event.event_id) > 0, "Event must have a generated unique event_id"
    assert event.created_at is not None, "Event must carry a timestamp"


def test_ac01_reject_unknown_supplier():
    """Verify creating a disruption event for an unconfigured supplier raises ValueError."""
    with pytest.raises(ValueError, match="Unknown supplier ID"):
        create_disruption_event(
            supplier_id="SUP-UNKNOWN-99",
            delay_duration_hours=8.0,
        )


def test_ac01_reject_negative_delay_duration():
    """Verify creating a disruption event with negative delay duration is rejected."""
    with pytest.raises((ValueError, Exception)):
        create_disruption_event(
            supplier_id="SUP-01",
            delay_duration_hours=-5.0,
        )


# ===========================================================================
# AC-02: Correct Supplier Association
# ===========================================================================

def test_ac02_event_strictly_associated_with_target_supplier():
    """Verify disruption events remain strictly bound to their assigned supplier."""
    event_sup01 = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    event_sup02 = create_disruption_event("SUP-02", delay_duration_hours=6.0)

    assert event_sup01.supplier_id == "SUP-01", "Event 1 must strictly associate with SUP-01"
    assert event_sup02.supplier_id == "SUP-02", "Event 2 must strictly associate with SUP-02"
    assert event_sup01.supplier_id != event_sup02.supplier_id, "Events must not cross-contaminate supplier identity"


# ===========================================================================
# AC-03: Downstream Dependency Identification
# ===========================================================================

def test_ac03_downstream_dependency_identification(fresh_graph):
    """Verify BFS traversal discovers downstream dependencies without duplicates or cycles."""
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(fresh_graph, event)

    assert impact.disrupted_supplier == "SUP-01", "Summary must record the origin supplier"
    assert len(impact.affected_parts) > 0, "Downstream parts must be discovered"
    assert len(impact.affected_products) > 0, "Downstream products must be discovered"
    assert len(impact.affected_orders) > 0, "Downstream orders must be discovered"

    # Ensure no node is counted or recorded twice (no duplicate IDs)
    assert len(impact.affected_parts) == len(set(impact.affected_parts)), "affected_parts must have unique IDs"
    assert len(impact.affected_products) == len(set(impact.affected_products)), "affected_products must have unique IDs"
    assert len(impact.affected_orders) == len(set(impact.affected_orders)), "affected_orders must have unique IDs"

    # Disrupted supplier root must not be categorized as its own downstream entity
    assert "SUP-01" not in impact.affected_parts
    assert "SUP-01" not in impact.affected_products
    assert "SUP-01" not in impact.affected_orders


# ===========================================================================
# AC-04: Affected BOM Parts
# ===========================================================================

def test_ac04_affected_bom_parts_identified(fresh_graph):
    """Verify downstream BOM parts are correctly identified and unrelated parts are excluded."""
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(fresh_graph, event)

    # In canonical dataset, SUP-01 supplies PART-01, PART-02, and PART-05
    assert "PART-01" in impact.affected_parts, "PART-01 must be identified as affected"
    assert "PART-02" in impact.affected_parts, "PART-02 must be identified as affected"
    assert "PART-05" in impact.affected_parts, "PART-05 must be identified as affected"

    # SUP-02 specific parts must NOT be in SUP-01's downstream impact
    assert "PART-03" not in impact.affected_parts, "PART-03 is supplied exclusively by SUP-02"
    assert "PART-04" not in impact.affected_parts, "PART-04 is supplied exclusively by SUP-02"


# ===========================================================================
# AC-05: Affected Finished Products
# ===========================================================================

def test_ac05_affected_finished_products_identified(fresh_graph):
    """Verify downstream finished assemblies are correctly identified."""
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(fresh_graph, event)

    # In canonical dataset, PART-01 and PART-02 feed PROD-01
    assert "PROD-01" in impact.affected_products, "PROD-01 must be identified as affected"


# ===========================================================================
# AC-06: Exactly Two Affected Customer Orders (Benchmark Anchor)
# ===========================================================================

def test_ac06_exactly_two_orders_breached_in_benchmark():
    """
    CRITICAL BENCHMARK ANCHOR:
    Verify exactly two customer orders (ORD-01 and ORD-02) fail when SUP-01
    experiences an 8-hour delay with a 5-hour recovery lead time.
    """
    result = simulation_service.simulate_benchmark()
    stockout = result["stockout"]

    # Verify count independently
    assert stockout["total_breached"] == 2, (
        f"Benchmark requires total_breached == 2, but received {stockout['total_breached']}"
    )

    breached_order_ids = [order["order_id"] for order in stockout["breached_orders"]]

    # Verify exact set of failing orders
    assert set(breached_order_ids) == {"ORD-01", "ORD-02"}, (
        f"Expected failing orders to be exactly {{'ORD-01', 'ORD-02'}}, but got {breached_order_ids}"
    )

    # Verify no duplicate IDs
    assert len(breached_order_ids) == len(set(breached_order_ids)), "Breached orders list contains duplicates"

    # Verify safe orders are strictly NOT marked as breached
    safe_orders = ["ORD-03", "ORD-04", "ORD-05", "ORD-06", "ORD-07", "ORD-08", "ORD-09", "ORD-10"]
    for safe_id in safe_orders:
        assert safe_id not in breached_order_ids, f"Safe order '{safe_id}' was incorrectly classified as breached"


def test_ac06_order_matching_detects_deadline_boundary_changes(fresh_graph):
    """
    Defect detection test:
    Verify that predict_stockout_and_orders accurately classifies orders based on
    recovery_threshold = stockout_hour + recovery_lead_time_hours (8.0 + 5.0 = 13.0h).
    """
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(fresh_graph, event)

    # 10 units stock, 1.25 burn => stockout at 8.0h
    depletion = simulate_inventory_depletion("PART-05", 10.0, 1.25, 8.0, 72)

    # Custom synthetic deadlines to verify boundary sensitivity:
    # Order A: deadline 12.0h (<= 13.0h) => FAILS
    # Order B: deadline 13.0h (== 13.0h) => FAILS (boundary condition)
    # Order C: deadline 13.1h (> 13.0h)  => PASSES
    synthetic_deadlines = {
        "ORD-01": 12.0,
        "ORD-02": 13.0,
        "ORD-03": 13.1,
    }

    res = predict_stockout_and_orders(
        depletion=depletion,
        impact=impact,
        order_deadlines=synthetic_deadlines,
        recovery_lead_time_hours=5.0,
    )

    breached_ids = {o.order_id for o in res.breached_orders}
    assert breached_ids == {"ORD-01", "ORD-02"}, "Expected ORD-01 and ORD-02 to breach, ORD-03 to survive"
    assert res.total_breached == 2


# ===========================================================================
# AC-07: Inventory Depletion Calculation
# ===========================================================================

def test_ac07_inventory_depletion_timeline_benchmark_progression():
    """
    Verify discrete-time hourly inventory depletion for official benchmark values:
    Initial Stock: 40 units, Hourly Consumption: 5 units/hr, Delay: 8 hours, Horizon: 72 hours.
    Stock progression: Hour 0: 40, Hour 1: 35, Hour 2: 30, ... Hour 8: 0.
    """
    initial_stock = 40.0
    hourly_consumption = 5.0
    delay_hours = 8.0
    horizon_hours = 72

    timeline_result = simulate_inventory_depletion(
        part_id="TEST-PART",
        initial_stock=initial_stock,
        hourly_consumption=hourly_consumption,
        delay_duration_hours=delay_hours,
        simulation_horizon_hours=horizon_hours,
    )

    # Exactly 73 entries for hours 0 through 72 inclusive
    assert len(timeline_result.timeline) == 73, (
        f"Timeline must contain exactly 73 entries, got {len(timeline_result.timeline)}"
    )

    # Verify each hour's stock value and supply_blocked status independently
    for point in timeline_result.timeline:
        expected_stock = max(0.0, initial_stock - point.hour * hourly_consumption)
        assert point.stock_units == expected_stock, (
            f"Hour {point.hour}: expected stock {expected_stock}, got {point.stock_units}"
        )
        assert point.stock_units >= 0.0, f"Stock at hour {point.hour} dropped below zero: {point.stock_units}"

        # Supply is blocked for hours 0..7 (< 8.0) and unblocked from hour 8 onward
        expected_blocked = point.hour < delay_hours
        assert point.supply_blocked == expected_blocked, (
            f"Hour {point.hour}: expected supply_blocked={expected_blocked}, got {point.supply_blocked}"
        )


def test_ac07_rejects_negative_inventory_parameters():
    """Verify input validation catches negative stock or consumption rates."""
    with pytest.raises(ValueError, match="initial_stock must be non-negative"):
        simulate_inventory_depletion("P-01", -10.0, 5.0, 8.0)

    with pytest.raises(ValueError, match="hourly_consumption must be non-negative"):
        simulate_inventory_depletion("P-01", 40.0, -2.0, 8.0)


# ===========================================================================
# AC-08: Stockout Time Prediction
# ===========================================================================

def test_ac08_stockout_hour_prediction():
    """Verify exact stockout hour prediction across benchmark and edge cases."""
    # Benchmark 1: 40 units at 5.0 units/hr => stocks out at hour 8.0
    tl1 = simulate_inventory_depletion("P-BENCH", 40.0, 5.0, 8.0, 72)
    assert tl1.stockout_hour == 8.0, f"Expected stockout at hour 8.0, got {tl1.stockout_hour}"

    # Benchmark 2 (Critical Part in scenario dataset): PART-05 has 10 units at 1.25 units/hr => 8.0h
    tl2 = simulate_inventory_depletion("PART-05", 10.0, 1.25, 8.0, 72)
    assert tl2.stockout_hour == 8.0, f"Expected PART-05 stockout at hour 8.0, got {tl2.stockout_hour}"

    # Edge Case: Abundant stock (no stockout within horizon)
    tl_no_stockout = simulate_inventory_depletion("P-ABUNDANT", 500.0, 1.0, 8.0, 72)
    assert tl_no_stockout.stockout_hour is None, "Should predict None when stockout does not occur within horizon"

    # Edge Case: Fast consumption
    tl_fast = simulate_inventory_depletion("P-FAST", 15.0, 5.0, 8.0, 72)
    assert tl_fast.stockout_hour == 3.0, f"Expected stockout at hour 3.0, got {tl_fast.stockout_hour}"


# ===========================================================================
# AC-09: Intervention Window Calculation
# ===========================================================================

def test_ac09_intervention_window_three_operational_states():
    """
    Verify the three operational business conditions of the intervention window formula:
    ΔT = T_stockout - T_current - t_recovery

    1. ΔT > 0 => FEASIBLE
    2. ΔT = 0 => CRITICAL
    3. ΔT < 0 => BREACHED
    """
    stockout_mock = StockoutPredictionResult(
        part_id="PART-05",
        stockout_hour=8.0,
        no_stockout=False,
        breached_orders=[
            BreachedOrder(order_id="ORD-01", delivery_deadline_hours=10.0, will_fail=True),
            BreachedOrder(order_id="ORD-02", delivery_deadline_hours=12.0, will_fail=True),
        ],
        total_breached=2,
    )

    # State 1: Benchmark positive window (ΔT = 8.0 - 0.0 - 5.0 = +3.0h)
    feasible_res = calculate_intervention_window(stockout_mock, current_hour=0.0, recovery_lead_time_hours=5.0)
    assert feasible_res.delta_t_hours == 3.0, "Expected ΔT == +3.0 hours"
    assert feasible_res.status == "FEASIBLE", "Status must be FEASIBLE"
    assert feasible_res.is_feasible is True, "is_feasible must be True"
    assert set(feasible_res.affected_order_ids) == {"ORD-01", "ORD-02"}

    # State 2: Boundary zero window (ΔT = 8.0 - 3.0 - 5.0 = 0.0h)
    critical_res = calculate_intervention_window(stockout_mock, current_hour=3.0, recovery_lead_time_hours=5.0)
    assert critical_res.delta_t_hours == 0.0, "Expected ΔT == 0.0 hours"
    assert critical_res.status == "CRITICAL", "Status must be CRITICAL"
    assert critical_res.is_feasible is True, "is_feasible must remain True at ΔT == 0"

    # State 3: Negative window (ΔT = 8.0 - 4.0 - 5.0 = -1.0h)
    breached_res = calculate_intervention_window(stockout_mock, current_hour=4.0, recovery_lead_time_hours=5.0)
    assert breached_res.delta_t_hours == -1.0, "Expected ΔT == -1.0 hours"
    assert breached_res.status == "BREACHED", "Status must be BREACHED"
    assert breached_res.is_feasible is False, "is_feasible must be False for negative ΔT"


# ===========================================================================
# AC-10: FastAPI Endpoint Integration
# ===========================================================================

def test_ac10_fastapi_disrupt_endpoint_success(api_client):
    """
    Verify POST /api/v1/simulation/disrupt executes successfully, returns
    HTTP 200, valid response structure, and satisfies performance SLA (< 25ms).
    """
    response = api_client.post(
        "/api/v1/simulation/disrupt",
        json={
            "supplier_id": "SUP-01",
            "disruption_type": "SUPPLIER_DELAY",
            "delay_duration_hours": 8.0,
            "description": "Integration test for AC-10",
        },
    )

    assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["status"] == "success", "Response status must be 'success'"
    assert "event" in data, "Response must include 'event' payload"
    assert "impact" in data, "Response must include 'impact' payload"
    assert "stockout" in data, "Response must include 'stockout' payload"
    assert "intervention" in data, "Response must include 'intervention' payload"
    assert "execution_time_ms" in data, "Response must include 'execution_time_ms'"

    # Verify business results from API
    assert data["stockout"]["total_breached"] == 2, "API must return total_breached == 2"
    assert data["intervention"]["delta_t_hours"] == 3.0, "API must return delta_t_hours == 3.0"
    assert data["intervention"]["status"] == "FEASIBLE", "API must return status == 'FEASIBLE'"
    assert data["execution_time_ms"] < 25.0, (
        f"Pipeline execution time must be under 25ms SLA, took {data['execution_time_ms']}ms"
    )


def test_ac10_fastapi_disrupt_endpoint_validation_errors(api_client):
    """Verify POST /api/v1/simulation/disrupt handles invalid payloads with HTTP 422."""
    # Unknown supplier
    bad_supplier_resp = api_client.post(
        "/api/v1/simulation/disrupt",
        json={
            "supplier_id": "SUP-INVALID-99",
            "disruption_type": "SUPPLIER_DELAY",
            "delay_duration_hours": 8.0,
        },
    )
    assert bad_supplier_resp.status_code in (400, 422), (
        f"Expected HTTP 400 or 422 for invalid supplier, got {bad_supplier_resp.status_code}"
    )

    # Negative delay duration
    negative_delay_resp = api_client.post(
        "/api/v1/simulation/disrupt",
        json={
            "supplier_id": "SUP-01",
            "disruption_type": "SUPPLIER_DELAY",
            "delay_duration_hours": -8.0,
        },
    )
    assert negative_delay_resp.status_code == 422, (
        f"Expected HTTP 422 for negative delay, got {negative_delay_resp.status_code}"
    )
