"""
Test Suite: Sprint 2 Disruption Simulation & Intervention Engine
Acceptance Criteria Verification: AC-01 to AC-10
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.disruption import DisruptionEvent, DisruptionType
from backend.app.services.simulation_service import simulation_service
from backend.app.simulation.engine import run_disruption_simulation
from backend.app.simulation.events import create_disruption_event
from backend.app.simulation.inventory import simulate_inventory_depletion
from backend.app.simulation.ripple import propagate_ripple_effect


@pytest.fixture
def client():
    return TestClient(app)


# AC-01: 8-hour delay can be introduced
def test_ac01_disruption_event_creation():
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    assert event.delay_duration_hours == 8.0
    assert event.event_id is not None


# AC-02: Disruption associated with correct supplier
def test_ac02_event_associated_with_supplier():
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    assert event.supplier_id == "SUP-01"


# AC-03: Downstream dependencies identified
def test_ac03_downstream_traversal():
    graph = simulation_service.get_graph()
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(graph, event)
    assert len(impact.affected_parts) > 0
    assert len(impact.affected_products) > 0
    assert len(impact.affected_orders) > 0


# AC-04: Affected BOM parts identified
def test_ac04_affected_bom_parts():
    graph = simulation_service.get_graph()
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(graph, event)
    assert "PART-01" in impact.affected_parts or "P-01" in impact.affected_parts
    assert "PART-05" in impact.affected_parts or "P-05" in impact.affected_parts


# AC-05: Affected finished products identified
def test_ac05_affected_finished_products():
    graph = simulation_service.get_graph()
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    impact = propagate_ripple_effect(graph, event)
    assert "PROD-01" in impact.affected_products


# AC-06: Exactly 2 customer orders impacted (Benchmark Anchor)
def test_ac06_exactly_two_orders_impacted():
    result = simulation_service.simulate_benchmark()
    assert result["stockout"]["total_breached"] == 2
    ids = [o["order_id"] for o in result["stockout"]["breached_orders"]]
    assert "ORD-01" in ids
    assert "ORD-02" in ids


# AC-07: Inventory depletion calculated (73 points for 72h horizon)
def test_ac07_inventory_depletion_timeline():
    tl = simulate_inventory_depletion("PART-05", 10.0, 1.25, 8.0, 72)
    assert len(tl.timeline) == 73  # hour 0 to 72 inclusive


# AC-08: Stockout timestamp predicted (T_stockout == 8.0)
def test_ac08_stockout_timestamp_predicted():
    tl = simulate_inventory_depletion("PART-05", 10.0, 1.25, 8.0, 72)
    assert tl.stockout_hour == 8.0


# AC-09: Intervention window formula verified (ΔT == +3.0h, FEASIBLE)
def test_ac09_intervention_window_formula():
    result = simulation_service.simulate_benchmark()
    assert result["intervention"]["delta_t_hours"] == 3.0
    assert result["intervention"]["is_feasible"] is True
    assert result["intervention"]["status"] == "FEASIBLE"
    assert "ORD-01" in result["intervention"]["affected_order_ids"]
    assert "ORD-02" in result["intervention"]["affected_order_ids"]


# AC-10: Results available via FastAPI endpoint & under 25ms SLA
def test_ac10_fastapi_endpoint_returns_results(client):
    response = client.post(
        "/api/v1/simulation/disrupt",
        json={
            "supplier_id": "SUP-01",
            "disruption_type": "SUPPLIER_DELAY",
            "delay_duration_hours": 8.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "event" in data
    assert "impact" in data
    assert "stockout" in data
    assert "intervention" in data
    assert data["stockout"]["total_breached"] == 2
    assert data["intervention"]["delta_t_hours"] == 3.0
    assert data["execution_time_ms"] < 25.0
