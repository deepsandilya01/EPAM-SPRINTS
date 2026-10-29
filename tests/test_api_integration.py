"""
Integration Tests — Flask API Endpoints & State Isolation
──────────────────────────────────────────────────────────
Verifies integration of graph validation, benchmark endpoints, and regression
protection for existing downstream tracing, deletion impact, undo, and reset.
"""

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

