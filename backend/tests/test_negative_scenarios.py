"""
Negative and Edge-Case Tests — EPAM Sprint 1 Phase 5 Validation.
Explicitly validates failure modes, rejection scenarios, boundary conditions,
unsupported methods, and graph state invariants under invalid inputs.
"""

from __future__ import annotations

import copy

import pytest

from graph_validation import (
    AcyclicityPolicy,
    ValidationPolicy,
    trace_downstream_with_metrics,
    validate_raw_graph_data,
)

# ============================================================================
# Section A: Graph Data Validation Failures & Rejections
# ============================================================================

@pytest.mark.unit
def test_missing_required_entity_fields(raw_data, baseline_policy):
    """Removing essential fields (e.g. 'id' or 'label') must be rejected."""
    # Delete id from a part
    del raw_data["nodes"]["parts"][0]["id"]
    report = validate_raw_graph_data(raw_data, policy=baseline_policy)
    assert report.valid is False
    assert any("id" in err.message.lower() or err.code == "ERR_MISSING_NODE_ID" for err in report.errors)


@pytest.mark.unit
def test_duplicate_edges_handling(raw_data, integrity_policy):
    """Duplicate edges between same nodes in raw data."""
    dup_edge = copy.deepcopy(raw_data["edges"]["supplies"][0])
    raw_data["edges"]["supplies"].append(dup_edge)
    # The validator reports either duplicate or gracefully handles count
    _ = validate_raw_graph_data(raw_data, policy=integrity_policy)
    # Edge count will be 22 instead of 21, so baseline check would catch it
    baseline_rep = validate_raw_graph_data(raw_data, policy=ValidationPolicy(check_baseline_counts=True))
    assert baseline_rep.valid is False


@pytest.mark.unit
def test_edge_referencing_nonexistent_target_node(raw_data, integrity_policy):
    """An edge pointing to a ghost node ID must be rejected."""
    ghost_edge = {
        "source": "SUP-01",
        "target": "GHOST-NODE-999",
        "relation": "supplies",
    }
    raw_data["edges"]["supplies"].append(ghost_edge)
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(err.code == "ERR_NONEXISTENT_TARGET_NODE" for err in report.errors)


@pytest.mark.unit
def test_edge_referencing_nonexistent_source_node(raw_data, integrity_policy):
    """An edge originating from a ghost node ID must be rejected."""
    ghost_edge = {
        "source": "GHOST-SUPPLIER-00",
        "target": "PART-01",
        "relation": "supplies",
    }
    raw_data["edges"]["supplies"].append(ghost_edge)
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(err.code == "ERR_NONEXISTENT_SOURCE_NODE" for err in report.errors)


@pytest.mark.unit
def test_self_loop_rejection(raw_data, integrity_policy):
    """Self-loop edge (source == target) must be detected and rejected."""
    self_loop = {
        "source": "PART-01",
        "target": "PART-01",
        "relation": "used_in",
    }
    raw_data["edges"]["used_in"].append(self_loop)
    report = validate_raw_graph_data(
        raw_data,
        policy=ValidationPolicy(check_baseline_counts=False, acyclicity_policy=AcyclicityPolicy.REQUIRE_DAG),
    )
    assert report.valid is False
    assert any("cycle" in err.code.lower() or "cycle" in err.message.lower() for err in report.errors)


@pytest.mark.unit
def test_reverse_tier_progression_rejected(raw_data, integrity_policy):
    """Edge moving backwards (e.g. Order -> Supplier) violates 4-tier flow."""
    backward_edge = {
        "source": "ORD-01",
        "target": "SUP-01",
        "relation": "fulfills",
    }
    raw_data["edges"]["fulfills"].append(backward_edge)
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(err.code == "ERR_INVALID_EDGE_DIRECTION" for err in report.errors)


# ============================================================================
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
# ============================================================================

@pytest.mark.integration
def test_graph_consistency_after_rejected_operations(app_client):
    """Failed operations (404, 400, 405) must leave the graph intact (19 nodes, 21 edges)."""
    app_client.post("/api/reset")

    # Fire sequence of invalid requests
    app_client.delete("/api/node/NON_EXISTENT")
    app_client.get("/api/downstream/NON_EXISTENT")
    app_client.post("/api/graph")
    app_client.post("/api/undo")
    app_client.get("/api/validation?mode=illegal")

    # Verify baseline graph is completely intact
    res = app_client.get("/api/graph")
    graph_data = res.get_json()
    assert len(graph_data["nodes"]) == 19
    assert len(graph_data["edges"]) == 21

    # Verify baseline validation still passes 100%
    val_res = app_client.get("/api/validation?mode=baseline")
    assert val_res.status_code == 200
    assert val_res.get_json()["valid"] is True


@pytest.mark.integration
def test_repeated_undo_operations(app_client):
    """
    Multiple deletes followed by multiple undos:
    1. Delete PART-01
    2. Delete PART-02
    3. Undo once -> restores PART-02
    4. Undo twice -> restores PART-01
    5. Undo third time -> fails with 400 (stack exhausted)
    """
    app_client.post("/api/reset")

    del1 = app_client.delete("/api/node/PART-01")
    assert del1.status_code == 200
    del2 = app_client.delete("/api/node/PART-02")
    assert del2.status_code == 200

    # Undo 1
    undo1 = app_client.post("/api/undo")
    assert undo1.status_code == 200
    assert undo1.get_json()["restored_node_id"] == "PART-02"

    # Undo 2
    undo2 = app_client.post("/api/undo")
    assert undo2.status_code == 200
    assert undo2.get_json()["restored_node_id"] == "PART-01"

    # Undo 3 (stack is now empty)
    undo3 = app_client.post("/api/undo")
    assert undo3.status_code == 400
    assert "nothing to undo" in undo3.get_json()["error"].lower()

    # Graph is back to 19 nodes
    graph_res = app_client.get("/api/graph")
    assert len(graph_res.get_json()["nodes"]) == 19


# ============================================================================
# Section D: Tracing Algorithm Edge Cases
# ============================================================================

@pytest.mark.unit
def test_trace_leaf_node_has_zero_downstream(canonical_graph):
    """Tracing an Order node (leaf tier) returns 0 visited downstream nodes."""
    res = trace_downstream_with_metrics(canonical_graph, "ORD-01", threshold_ms=10.0)
    assert res["source_exists"] is True
    assert res["visited_count"] == 0
    assert res["downstream_node_ids"] == []
    assert res["under_threshold"] is True


@pytest.mark.unit
def test_trace_nonexistent_node(canonical_graph):
    """Tracing a node that doesn't exist returns source_exists=False without error."""
    res = trace_downstream_with_metrics(canonical_graph, "SUP-999", threshold_ms=10.0)
    assert res["source_exists"] is False
    assert res["visited_count"] == 0
    assert res["under_threshold"] is True
