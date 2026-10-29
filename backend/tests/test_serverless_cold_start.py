"""
Serverless Lifecycle & Cold Start Tests — EPAM Sprint 1 Pre-Deployment Audit.
Formally tests and validates the behavior of in-memory graph state across:
1. Warm serverless instances (sequential requests on the same execution context).
2. Cold starts (fresh execution context spun up from cold state).
3. Multi-instance isolation (mutations in one container not shared with another).
"""

from __future__ import annotations

import importlib

import pytest


@pytest.mark.integration
def test_warm_instance_sequential_requests(app_client):
    """
    On a warm serverless container instance, in-memory state persists
    across back-to-back requests within the same process.
    """
    # Reset to baseline
    app_client.post("/api/reset")
    initial_graph = app_client.get("/api/graph").get_json()
    assert len(initial_graph["nodes"]) == 19

    # Delete PART-01
    del_res = app_client.delete("/api/node/PART-01")
    assert del_res.status_code == 200
    del_data = del_res.get_json()
    assert "PART-01" in del_data["deleted"]

    # Immediate follow-up GET on same warm instance reflects deletion
    followup_graph = app_client.get("/api/graph").get_json()
    assert len(followup_graph["nodes"]) < 19

    # Immediate undo on same warm instance restores baseline
    undo_res = app_client.post("/api/undo")
    assert undo_res.status_code == 200
    assert undo_res.get_json()["restored_node_id"] == "PART-01"

    restored_graph = app_client.get("/api/graph").get_json()
    assert len(restored_graph["nodes"]) == 19


@pytest.mark.integration
def test_cold_start_simulation_demonstrates_in_memory_reset(monkeypatch):
    """
    Formally demonstrates the serverless cold-start reality:
    When a serverless container terminates or a cold start occurs,
    a fresh instance is initialized with the canonical baseline dataset (19 nodes),
    and the in-memory UNDO_STACK is empty.
    """
    import backend.app as app_module

    # 1. Container 1 receives a delete request
    client1 = app_module.app.test_client()
    client1.post("/api/reset")
    del_res = client1.delete("/api/node/PART-05")
    assert del_res.status_code == 200
    assert len(client1.get("/api/graph").get_json()["nodes"]) < 19

    # 2. Simulate Cold Start: Fresh module / container instantiation
    # (In Vercel/Lambda, a new microVM/process initializes global variables from scratch)
    reloaded_module = importlib.reload(app_module)
    client2 = reloaded_module.app.test_client()

    # 3. Evidence 1: Fresh instance starts at baseline 19 nodes, NOT Container 1's mutated state
    cold_graph = client2.get("/api/graph").get_json()
    assert len(cold_graph["nodes"]) == 19, (
        "Serverless cold start re-initializes graph from JSON file, resetting in-memory mutations"
    )

    # 4. Evidence 2: UNDO_STACK on Container 2 is empty; calling undo fails with 400
    undo_cold = client2.post("/api/undo")
    assert undo_cold.status_code == 400
    assert "nothing to undo" in undo_cold.get_json()["error"].lower(), (
        "Serverless cold start has an empty undo stack; cannot undo mutations from previous instances"
    )


@pytest.mark.integration
def test_cross_instance_concurrent_isolation():
    """
    Simulate two concurrent serverless container instances running in parallel.
    Proves that mutations on Container A do not corrupt or alter Container B.
    """
    from backend.app import _build_graph, _load_raw_data

    raw = _load_raw_data()
    container_a_graph = _build_graph(raw)
    container_b_graph = _build_graph(raw)

    # Mutation on Container A
    container_a_graph.remove_node("PART-01")
    assert "PART-01" not in container_a_graph
    assert container_a_graph.number_of_nodes() == 18

    # Container B remains untouched at 19 nodes
    assert "PART-01" in container_b_graph
    assert container_b_graph.number_of_nodes() == 19
