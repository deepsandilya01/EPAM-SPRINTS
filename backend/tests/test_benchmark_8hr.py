"""
Official 8-Hour Disruption Benchmark End-to-End Integration Verification Suite
Role: QA Automation & Acceptance Verification Lead (Soumya)
Project: RE:Flow — Team Photon

Purpose:
End-to-end integration verification of the canonical 8-hour supplier disruption scenario:
  - Supplier: SUP-01 with 8.0-hour delay
  - Critical part: PART-05 (10.0 units initial stock, 1.25 units/hr burn -> stocks out at 8.0h)
  - Recovery lead time: 5.0 hours (recovery threshold = 8.0 + 5.0 = 13.0h)
  - Exactly 2 failing customer orders: ORD-01 (10h) and ORD-02 (12h)
  - Intervention window: ΔT = 8.0 - 0.0 - 5.0 = +3.0 hours (FEASIBLE)
  - Performance SLA: Pipeline latency < 25 ms
"""

from __future__ import annotations

import copy
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.data.loader import load_scenario_dataset
from backend.app.graph.builder import build_graph
from backend.app.main import app
from backend.app.models.disruption import DisruptionEvent, DisruptionType
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
def benchmark_dataset():
    """Load canonical benchmark scenario dataset."""
    return load_scenario_dataset()


@pytest.fixture
def pristine_graph(benchmark_dataset):
    """Build a pristine NetworkX graph instance from canonical data."""
    return build_graph(copy.deepcopy(benchmark_dataset))


@pytest.fixture
def test_client():
    """FastAPI TestClient for benchmark API verification."""
    with TestClient(app) as client:
        yield client


# ===========================================================================
# 1. Pipeline Handshake Integration Test
# ===========================================================================

def test_benchmark_data_handshake_across_all_five_stages(pristine_graph, benchmark_dataset):
    """
    Verify strict step-by-step data handover across all 5 simulation stages:
    Stage 1: events.py      -> produces DisruptionEvent
    Stage 2: ripple.py      -> consumes Event + Graph, produces RippleImpactSummary
    Stage 3: inventory.py   -> consumes Part + Rates, produces InventoryDepletionTimeline
    Stage 4: stockout.py    -> consumes Depletion + Impact + Deadlines, produces StockoutPredictionResult
    Stage 5: intervention.py-> consumes StockoutResult, produces InterventionWindowResult
    """
    # Stage 1: Disruption Event
    event = create_disruption_event(
        supplier_id="SUP-01",
        disruption_type=DisruptionType.SUPPLIER_DELAY,
        delay_duration_hours=8.0,
        description="Benchmark 8-hour supplier delay",
    )
    assert event.supplier_id == "SUP-01"
    assert event.delay_duration_hours == 8.0

    # Stage 2: Ripple Propagation (BFS Traversal)
    impact = propagate_ripple_effect(pristine_graph, event)
    assert impact.disrupted_supplier == "SUP-01"
    assert "PART-05" in impact.affected_parts
    assert "PROD-01" in impact.affected_products
    assert "ORD-01" in impact.affected_orders
    assert "ORD-02" in impact.affected_orders

    # Stage 3: Inventory Depletion (Critical Part: PART-05)
    # PART-05 initial stock = 10.0 units, hourly consumption = 1.25 units/hr
    depletion = simulate_inventory_depletion(
        part_id="PART-05",
        initial_stock=10.0,
        hourly_consumption=1.25,
        delay_duration_hours=8.0,
        simulation_horizon_hours=72,
    )
    assert depletion.part_id == "PART-05"
    assert depletion.stockout_hour == 8.0
    assert len(depletion.timeline) == 73

    # Stage 4: Stockout Prediction & Order Breach
    # Extract order deadlines from benchmark dataset
    order_deadlines = {}
    for ord_node in benchmark_dataset.get("nodes", {}).get("orders", []):
        oid = ord_node.get("id") or ord_node.get("order_id")
        dl = ord_node.get("delivery_deadline_hours") or ord_node.get("deadline_hours")
        if oid and dl is not None:
            order_deadlines[oid] = float(dl)

    recovery_lead_time = 5.0
    stockout_result = predict_stockout_and_orders(
        depletion=depletion,
        impact=impact,
        order_deadlines=order_deadlines,
        recovery_lead_time_hours=recovery_lead_time,
    )
    assert stockout_result.stockout_hour == 8.0
    assert stockout_result.total_breached == 2
    breached_ids = [b.order_id for b in stockout_result.breached_orders]
    assert set(breached_ids) == {"ORD-01", "ORD-02"}

    # Stage 5: Intervention Window
    intervention = calculate_intervention_window(
        stockout_result=stockout_result,
        current_hour=0.0,
        recovery_lead_time_hours=recovery_lead_time,
    )
    # ΔT = 8.0 - 0.0 - 5.0 = +3.0 hours
    assert intervention.delta_t_hours == 3.0
    assert intervention.is_feasible is True
    assert intervention.status == "FEASIBLE"
    assert set(intervention.affected_order_ids) == {"ORD-01", "ORD-02"}


# ===========================================================================
# 2. Engine Orchestration & Graph Immutability Integration Test
# ===========================================================================

def test_benchmark_full_engine_pipeline_and_graph_immutability(pristine_graph, benchmark_dataset):
    """
    Verify full engine execution via run_disruption_simulation():
    - Graph is never mutated (node and edge counts identical before and after).
    - Pipeline completes well under the 25ms SLA.
    - All benchmark oracle values match.
    """
    initial_node_count = pristine_graph.number_of_nodes()
    initial_edge_count = pristine_graph.number_of_edges()

    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)

    start_time = time.perf_counter()
    result = run_disruption_simulation(
        event=event,
        graph=pristine_graph,
        scenario=benchmark_dataset,
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # 1. Immutability verification
    assert pristine_graph.number_of_nodes() == initial_node_count, "Graph nodes were mutated during simulation"
    assert pristine_graph.number_of_edges() == initial_edge_count, "Graph edges were mutated during simulation"

    # 2. Performance SLA verification
    assert elapsed_ms < 25.0, f"Full engine run took {elapsed_ms:.2f}ms, exceeding 25ms SLA"
    assert result["pipeline_elapsed_ms"] < 25.0
    assert result["under_25ms"] is True

    # 3. Benchmark Oracle verification
    assert result["status"] == "success"
    assert result["critical_part"]["part_id"] == "PART-05"
    assert result["stockout"]["stockout_hour"] == 8.0
    assert result["stockout"]["total_breached"] == 2

    failing_ids = [o["order_id"] for o in result["stockout"]["breached_orders"]]
    assert set(failing_ids) == {"ORD-01", "ORD-02"}
    assert result["intervention"]["delta_t_hours"] == 3.0
    assert result["intervention"]["status"] == "FEASIBLE"
    assert result["intervention"]["is_feasible"] is True


# ===========================================================================
# 3. Service Layer and API Endpoints Benchmark Consistency
# ===========================================================================

def test_benchmark_service_and_api_consistency(test_client):
    """
    Verify that the Service layer and both API endpoints return identical,
    deterministic benchmark results:
      - simulation_service.simulate_benchmark()
      - GET /api/v1/simulation/benchmark
      - POST /api/v1/simulation/disrupt
    """
    # 1. Service Layer
    svc_result = simulation_service.simulate_benchmark()
    assert svc_result["stockout"]["total_breached"] == 2
    assert svc_result["intervention"]["delta_t_hours"] == 3.0
    assert svc_result["intervention"]["status"] == "FEASIBLE"

    # 2. GET Benchmark Endpoint
    get_res = test_client.get("/api/v1/simulation/benchmark")
    assert get_res.status_code == 200, f"GET benchmark returned {get_res.status_code}"
    get_data = get_res.json()
    assert get_data["stockout"]["total_breached"] == 2
    assert get_data["intervention"]["delta_t_hours"] == 3.0
    assert get_data["intervention"]["status"] == "FEASIBLE"

    # 3. POST Disrupt Endpoint with benchmark parameters
    post_res = test_client.post(
        "/api/v1/simulation/disrupt",
        json={
            "supplier_id": "SUP-01",
            "disruption_type": "SUPPLIER_DELAY",
            "delay_duration_hours": 8.0,
            "description": "Canonical 8-hour supplier delay",
        },
    )
    assert post_res.status_code == 200, f"POST disrupt returned {post_res.status_code}"
    post_data = post_res.json()
    assert post_data["stockout"]["total_breached"] == 2
    assert post_data["intervention"]["delta_t_hours"] == 3.0
    assert post_data["intervention"]["status"] == "FEASIBLE"

    # 4. Consistency check between GET and POST responses
    assert get_data["stockout"]["total_breached"] == post_data["stockout"]["total_breached"]
    assert get_data["intervention"]["delta_t_hours"] == post_data["intervention"]["delta_t_hours"]
    assert get_data["critical_part"]["part_id"] == post_data["critical_part"]["part_id"]


# ===========================================================================
# 4. Negative & Contrast Verification (Different Supplier Isolation)
# ===========================================================================

def test_supplier_isolation_and_distinct_impact_profiles(pristine_graph, benchmark_dataset):
    """
    Verify supplier isolation and distinct impact profiles:
    - SUP-01 disruption reaches PROD-01 subtree (breaches ORD-01 and ORD-02),
      and does NOT breach ORD-07 (which depends on PROD-02).
    - SUP-02 disruption reaches PROD-02 subtree (breaches ORD-07),
      producing a distinct set of failing orders.
    """
    # SUP-01 benchmark disruption
    event_sup01 = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    result_sup01 = run_disruption_simulation(
        event=event_sup01,
        graph=pristine_graph,
        scenario=benchmark_dataset,
    )
    breached_sup01 = [o["order_id"] for o in result_sup01["stockout"]["breached_orders"]]

    # SUP-02 disruption
    event_sup02 = create_disruption_event("SUP-02", delay_duration_hours=6.0)
    result_sup02 = run_disruption_simulation(
        event=event_sup02,
        graph=pristine_graph,
        scenario=benchmark_dataset,
    )
    breached_sup02 = [o["order_id"] for o in result_sup02["stockout"]["breached_orders"]]

    # SUP-01 must breach exactly 2 orders (ORD-01, ORD-02) and never breach ORD-07
    assert set(breached_sup01) == {"ORD-01", "ORD-02"}
    assert "ORD-07" not in breached_sup01, "SUP-01 cannot breach ORD-07 (PROD-02 branch)"

    # SUP-02 uniquely breaches ORD-07 (PROD-02 fulfills ORD-07 with deadline 14h)
    assert "ORD-07" in breached_sup02, "SUP-02 must breach ORD-07"
    assert result_sup02["stockout"]["total_breached"] == 3
    assert set(breached_sup01) != set(breached_sup02), "Different suppliers must yield distinct impact profiles"
