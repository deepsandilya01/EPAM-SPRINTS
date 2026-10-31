from __future__ import annotations

import importlib

import pytest


@pytest.mark.integration
def test_root_serves_html(app_client):
    """GET / should serve the interactive frontend HTML."""
    res = app_client.get("/")
    assert res.status_code == 200
    assert b"Photon Sprint 1" in res.data
    assert b"Supply-Chain Graph" in res.data


@pytest.mark.integration
def test_api_graph_returns_canonical_counts(app_client):
    """GET /api/graph must return 19 nodes and 21 edges."""
    res = app_client.get("/api/graph")
    assert res.status_code == 200
    data = res.get_json()
    assert "nodes" in data and "edges" in data
    assert len(data["nodes"]) == 19
    assert len(data["edges"]) == 21


@pytest.mark.integration
def test_api_validation_endpoint(app_client):
    """GET /api/validation must return a complete validation report."""
    res = app_client.get("/api/validation")
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["mode"] == "baseline"
    assert data["summary"]["node_count"] == 19
    assert data["summary"]["edge_count"] == 21
    assert data["summary"]["supplier_count"] == 2
    assert data["summary"]["part_count"] == 5
    assert data["summary"]["product_count"] == 2
    assert data["summary"]["order_count"] == 10
    assert len(data["checks"]) >= 4
    assert all(c["status"] == "PASS" for c in data["checks"])


@pytest.mark.integration
def test_api_validation_strict_mode(app_client):
    """Strict mode parameter returns 200 when valid."""
    res = app_client.get("/api/validation?strict=true")
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True


@pytest.mark.integration
def test_api_benchmark_tracing_endpoint(app_client):
    """GET /api/benchmark/tracing must measure traversal and pass 10 ms threshold."""
    res = app_client.get("/api/benchmark/tracing?node_id=SUP-01&threshold_ms=10.0")
    assert res.status_code == 200
    data = res.get_json()
    assert data["source_node_id"] == "SUP-01"
    assert data["source_exists"] is True
    assert data["visited_count"] == 10
    assert data["elapsed_ms"] < 10.0
    assert data["under_threshold"] is True
    assert data["status"] == "PASS"


@pytest.mark.integration
def test_api_benchmark_tracing_unknown_node(app_client):
    """GET /api/benchmark/tracing handles unknown node without 500 error."""
    res = app_client.get("/api/benchmark/tracing?node_id=SUP-999")
    assert res.status_code == 200
    data = res.get_json()
    assert data["source_exists"] is False
    assert data["visited_count"] == 0
    assert data["under_threshold"] is True


@pytest.mark.integration
def test_api_downstream_reachability_integration(app_client):
    """GET /api/downstream/<node_id> retains original response contract."""
    res1 = app_client.get("/api/downstream/SUP-01")
    assert res1.status_code == 200
    d1 = res1.get_json()
    assert d1["root"] == "SUP-01"
    assert len(d1["downstream"]) == 10

    res2 = app_client.get("/api/downstream/SUP-02")
    assert res2.status_code == 200
    d2 = res2.get_json()
    assert d2["root"] == "SUP-02"
    assert len(d2["downstream"]) == 15


@pytest.mark.integration
def test_api_impact_preview_integration(app_client):
    """GET /api/impact/<node_id> returns preview without mutating graph."""
    res = app_client.get("/api/impact/PART-05")
    assert res.status_code == 200
    d = res.get_json()
    assert d["node"]["id"] == "PART-05"
    assert d["total_nodes_affected"] > 1
    assert "time_complexity" in d

    # Ensure graph is untouched
    graph_res = app_client.get("/api/graph")
    assert len(graph_res.get_json()["nodes"]) == 19


@pytest.mark.integration
def test_deletion_and_validation_lifecycle(app_client):
    """
    Test full lifecycle:
    1. Baseline validation passes.
    2. Node is deleted.
    3. Structural integrity passes, but baseline mode detects count deviation.
    4. Undo restores node; baseline validation passes again.
    """
    # 1. Baseline initially valid
    r1 = app_client.get("/api/validation?mode=baseline")
    assert r1.status_code == 200
    assert r1.get_json()["valid"] is True

    # 2. Delete PART-05
    del_res = app_client.delete("/api/node/PART-05")
    assert del_res.status_code == 200
    del_data = del_res.get_json()
    assert del_data["deleted_node_id"] == "PART-05"

    # 3. Validation: integrity mode passes
    r_integ = app_client.get("/api/validation?mode=integrity")
    assert r_integ.status_code == 200
    assert r_integ.get_json()["valid"] is True

    # Baseline mode fails because counts are < 19
    r_base = app_client.get("/api/validation?mode=baseline&strict=true")
    assert r_base.status_code == 422
    assert r_base.get_json()["valid"] is False

    # 4. Undo restoration
    undo_res = app_client.post("/api/undo")
    assert undo_res.status_code == 200
    assert undo_res.get_json()["restored_node_id"] == "PART-05"

    # Baseline mode passes again
    r_restored = app_client.get("/api/validation?mode=baseline")
    assert r_restored.status_code == 200
    assert r_restored.get_json()["valid"] is True
    assert r_restored.get_json()["summary"]["node_count"] == 19


@pytest.mark.integration
def test_reset_endpoint(app_client):
    """POST /api/reset restores the canonical 19-node graph."""
    # Delete a node first
    app_client.delete("/api/node/PART-01")
    assert len(app_client.get("/api/graph").get_json()["nodes"]) < 19

    # Reset
    reset_res = app_client.post("/api/reset")
    assert reset_res.status_code == 200
    assert reset_res.get_json()["node_count"] == 19

    # Graph is restored
    val_res = app_client.get("/api/validation")
    assert val_res.status_code == 200
    assert val_res.get_json()["valid"] is True


@pytest.mark.integration
def test_vercel_serverless_entrypoint():
    """Verify api/index.py exports a functional WSGI Flask application."""
    from backend.app.main import app as vercel_app

    client = vercel_app.test_client()
    res = client.get("/api/graph")
    assert res.status_code == 200
    data = res.get_json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 19




@pytest.mark.unit
def test_validation_api_response_contract(app_client):
    """Ensure /api/validation schema matches the frontend rendering expectations."""
    res = app_client.get("/api/validation")
    assert res.status_code == 200
    data = res.get_json()

    # Top-level contract
    assert isinstance(data.get("valid"), bool)
    assert isinstance(data.get("graph_name"), str)
    assert isinstance(data.get("mode"), str)
    assert isinstance(data.get("summary"), dict)
    assert isinstance(data.get("checks"), list)
    assert isinstance(data.get("errors"), list)
    assert isinstance(data.get("warnings"), list)
    assert isinstance(data.get("policy"), dict)
    assert isinstance(data.get("timestamp"), str)

    # Summary counts contract
    s = data["summary"]
    for key in ("node_count", "edge_count", "supplier_count", "part_count", "product_count", "order_count"):
        assert key in s, f"Missing key in summary: {key}"
        assert isinstance(s[key], int), f"Field {key} must be an integer"
        assert s[key] >= 0

    # Checks array vocabulary contract
    allowed_statuses = {"PASS", "FAIL", "WARN", "SKIP"}
    for check in data["checks"]:
        assert "check_id" in check and isinstance(check["check_id"], str)
        assert "status" in check and check["status"] in allowed_statuses
        assert "message" in check and isinstance(check["message"], str)

    # Errors array contract
    for err in data["errors"]:
        assert "code" in err and isinstance(err["code"], str)
        assert "message" in err and isinstance(err["message"], str)
        assert "severity" in err and isinstance(err["severity"], str)


@pytest.mark.unit
def test_benchmark_api_response_contract(app_client):
    """Ensure /api/benchmark/tracing schema matches the frontend panel requirements."""
    res = app_client.get("/api/benchmark/tracing?node_id=SUP-01")
    assert res.status_code == 200
    data = res.get_json()

    assert "source_node_id" in data and isinstance(data["source_node_id"], str)
    assert "source_exists" in data and isinstance(data["source_exists"], bool)
    assert "downstream_node_ids" in data and isinstance(data["downstream_node_ids"], list)
    assert "visited_count" in data and isinstance(data["visited_count"], int)
    assert "elapsed_ms" in data and isinstance(data["elapsed_ms"], (int, float))
    assert "threshold_ms" in data and isinstance(data["threshold_ms"], (int, float))
    assert "under_threshold" in data and isinstance(data["under_threshold"], bool)
    assert "status" in data and data["status"] in ("PASS", "FAIL")
    assert "time_complexity" in data and isinstance(data["time_complexity"], str)






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
# Section B: API Rejection, HTTP Methods, and Parameter Error Handling
# ============================================================================

@pytest.mark.integration
def test_api_downstream_nonexistent_node(app_client):
    """GET /api/downstream/<unknown_id> returns 404."""
    res = app_client.get("/api/downstream/UNKNOWN-NODE-999")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data
    assert "UNKNOWN-NODE-999" in data["error"]


@pytest.mark.integration
def test_api_impact_nonexistent_node(app_client):
    """GET /api/impact/<unknown_id> returns 404."""
    res = app_client.get("/api/impact/UNKNOWN-NODE-999")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data


@pytest.mark.integration
def test_api_delete_nonexistent_node(app_client):
    """DELETE /api/node/<unknown_id> returns 404."""
    res = app_client.delete("/api/node/UNKNOWN-NODE-999")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data


@pytest.mark.integration
def test_api_undo_empty_stack(app_client):
    """POST /api/undo when stack is empty returns 400 Bad Request."""
    # Ensure graph is reset and undo stack is empty
    app_client.post("/api/reset")
    res = app_client.post("/api/undo")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert "nothing to undo" in data["error"].lower()


@pytest.mark.integration
def test_api_validation_invalid_mode_param(app_client):
    """GET /api/validation?mode=INVALID_MODE returns 400."""
    res = app_client.get("/api/validation?mode=INVALID_MODE")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert data["valid"] is False


@pytest.mark.integration
def test_api_benchmark_invalid_threshold(app_client):
    """GET /api/benchmark/tracing with non-numeric or <=0 threshold returns 400."""
    # Non-numeric
    res1 = app_client.get("/api/benchmark/tracing?threshold_ms=abc")
    assert res1.status_code == 400
    assert "error" in res1.get_json()

    # Zero or negative
    res2 = app_client.get("/api/benchmark/tracing?threshold_ms=-2.5")
    assert res2.status_code == 400
    assert "error" in res2.get_json()


@pytest.mark.integration
def test_api_unsupported_http_methods(app_client):
    """Calling endpoints with unsupported HTTP methods returns 405 JSON."""
    # POST to a GET-only endpoint
    res1 = app_client.post("/api/graph")
    assert res1.status_code == 405
    data1 = res1.get_json()
    assert data1["status"] == 405
    assert "Method not allowed" in data1["error"]

    # GET to a POST-only endpoint
    res2 = app_client.get("/api/undo")
    assert res2.status_code == 405
    data2 = res2.get_json()
    assert data2["status"] == 405


@pytest.mark.integration
def test_api_nonexistent_route_404_json(app_client):
    """Calling an unknown /api/ route returns 404 JSON, not HTML."""
    res = app_client.get("/api/nonexistent/route")
    assert res.status_code == 404
    data = res.get_json()
    assert data is not None
    assert data["status"] == 404
    assert "Resource not found" in data["error"]


# ============================================================================
# Section C: Graph State Consistency and Boundary Conditions
