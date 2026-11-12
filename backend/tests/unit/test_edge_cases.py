from __future__ import annotations

import copy
import json

import pytest

from backend.app.validation import (
    AcyclicityPolicy,
    ValidationPolicy,
    trace_downstream_with_metrics,
    validate_raw_graph_data,
)


@pytest.mark.unit
@pytest.mark.parametrize("bad_payload", [
    None,
    "plain text not json",
    [1, 2, 3],
    12345,
    True,
])
def test_non_dict_top_level_payload(bad_payload):
    """Passing a non-dict must return a valid ValidationReport with valid=False."""
    report = validate_raw_graph_data(bad_payload)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_TOP_LEVEL_TYPE" for e in report.errors)
    serialized = json.dumps(report.to_dict())
    assert isinstance(serialized, str)


@pytest.mark.unit
def test_empty_graph_payload():
    """An empty dictionary payload must fail safely without uncaught exceptions."""
    report = validate_raw_graph_data({})
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_NODES_KEY" for e in report.errors)
    assert any(e.code == "ERR_MISSING_EDGES_KEY" for e in report.errors)


@pytest.mark.unit
def test_empty_nodes_and_edges():
    """Graph with empty node/edge maps must fail baseline counts, pass integrity if empty permitted."""
    empty_graph = {"nodes": {}, "edges": {}}
    rep_baseline = validate_raw_graph_data(empty_graph, policy=ValidationPolicy(check_baseline_counts=True))
    assert rep_baseline.valid is False
    assert any(e.code == "ERR_BASELINE_NODE_COUNT_MISMATCH" for e in rep_baseline.errors)

    rep_integrity = validate_raw_graph_data(empty_graph, policy=ValidationPolicy(check_baseline_counts=False))
    assert rep_integrity.valid is True


@pytest.mark.unit
def test_node_category_as_wrong_type(raw_data, integrity_policy):
    """Category that is a string instead of a list must fail gracefully."""
    raw_data["nodes"]["suppliers"] = "not_a_list"
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_CATEGORY_TYPE" for e in report.errors)


@pytest.mark.unit
def test_report_json_serializability(raw_data, baseline_policy):
    """Every field in the generated ValidationReport must be strictly JSON-serializable."""
    report = validate_raw_graph_data(raw_data, policy=baseline_policy)
    report_dict = report.to_dict()
    dumped = json.dumps(report_dict, indent=2)
    assert len(dumped) > 100
    reloaded = json.loads(dumped)
    assert reloaded["valid"] is True
    assert reloaded["summary"]["node_count"] == 19





@pytest.mark.unit
def test_missing_top_level_nodes(raw_data, integrity_policy):
    """Missing 'nodes' dictionary must trigger critical schema error."""
    del raw_data["nodes"]
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_NODES_KEY" for e in report.errors)


@pytest.mark.unit
def test_missing_top_level_edges(raw_data, integrity_policy):
    """Missing 'edges' dictionary must trigger critical schema error."""
    del raw_data["edges"]
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_EDGES_KEY" for e in report.errors)


@pytest.mark.unit
def test_missing_node_id_field(raw_data, integrity_policy):
    """A node record lacking an 'id' attribute must fail validation."""
    del raw_data["nodes"]["suppliers"][0]["id"]
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_NODE_ID" for e in report.errors)


@pytest.mark.unit
@pytest.mark.parametrize("invalid_id", ["", "   ", None, 12345])
def test_empty_or_invalid_node_id(raw_data, integrity_policy, invalid_id):
    """Empty or non-string node ID must fail validation."""
    raw_data["nodes"]["parts"][0]["id"] = invalid_id
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code in ("ERR_EMPTY_NODE_ID", "ERR_MISSING_NODE_ID") for e in report.errors)


@pytest.mark.unit
def test_missing_node_label(raw_data, integrity_policy):
    """A node missing its required 'label' must fail validation."""
    del raw_data["nodes"]["products"][0]["label"]
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_NODE_LABEL" for e in report.errors)


@pytest.mark.unit
def test_negative_part_stock_detected(raw_data, integrity_policy):
    """A part with negative stock_on_hand must fail numeric validation."""
    raw_data["nodes"]["parts"][0]["stock_on_hand"] = -50
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_PART_NUMERIC_FIELD" for e in report.errors)


@pytest.mark.unit
def test_invalid_order_quantity_detected(raw_data, integrity_policy):
    """An order with zero or negative quantity must fail validation."""
    raw_data["nodes"]["orders"][0]["quantity"] = 0
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_ORDER_QUANTITY" for e in report.errors)






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
