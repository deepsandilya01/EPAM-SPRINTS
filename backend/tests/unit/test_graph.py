from __future__ import annotations

import pytest

from backend.app.validation import (
    BaselineCounts,
    ValidationPolicy,
    validate_networkx_graph,
    validate_raw_graph_data,
)


@pytest.mark.unit
def test_canonical_graph_node_counts(raw_data, baseline_policy):
    """Verify that pristine canonical JSON meets all baseline count requirements."""
    report = validate_raw_graph_data(raw_data, policy=baseline_policy)
    assert report.valid is True
    assert len(report.errors) == 0

    s = report.summary
    assert s["node_count"] == 19
    assert s["supplier_count"] == 2
    assert s["part_count"] == 5
    assert s["product_count"] == 2
    assert s["order_count"] == 10
    assert s["edge_count"] == 21
    assert s["supplies_count"] == 6
    assert s["used_in_count"] == 5
    assert s["fulfills_count"] == 10


@pytest.mark.unit
@pytest.mark.parametrize("category,expected_count", [
    ("suppliers", 2),
    ("parts", 5),
    ("products", 2),
    ("orders", 10),
])
def test_exact_node_category_counts(raw_data, category, expected_count):
    """Verify each node category contains the exact expected count."""
    assert len(raw_data["nodes"][category]) == expected_count


@pytest.mark.unit
@pytest.mark.parametrize("category", ["suppliers", "parts", "products", "orders"])
def test_missing_node_in_category_fails_baseline(raw_data, baseline_policy, category):
    """Removing any node must trigger baseline count mismatch in baseline mode."""
    removed = raw_data["nodes"][category].pop(0)

    # Clean up edges touching the removed node to avoid foreign key errors
    for et in raw_data["edges"]:
        raw_data["edges"][et] = [
            e for e in raw_data["edges"][et]
            if e.get("source") != removed["id"] and e.get("target") != removed["id"]
        ]

    report = validate_raw_graph_data(raw_data, policy=baseline_policy)
    assert report.valid is False
    assert any(e.code == "ERR_BASELINE_NODE_COUNT_MISMATCH" for e in report.errors)


@pytest.mark.unit
def test_configurable_baseline_counts(raw_data):
    """Future approved graph changes can adjust expected counts via BaselineCounts."""
    new_supplier = {
        "id": "SUP-03",
        "kind": "supplier",
        "label": "Delta Electronics",
        "supplier_id": "SUP-03",
        "name": "Delta Electronics",
        "location": "Chennai",
        "note": "Backup supplier",
    }
    raw_data["nodes"]["suppliers"].append(new_supplier)

    raw_data["edges"]["supplies"].append({
        "relation": "SUPPLIES",
        "source": "SUP-03",
        "target": "PART-01",
        "lead_time_hours": 12,
        "max_capacity_units_per_day": 90,
    })

    default_policy = ValidationPolicy(check_baseline_counts=True)
    rep_default = validate_raw_graph_data(raw_data, policy=default_policy)
    assert rep_default.valid is False
    assert any(e.code == "ERR_BASELINE_NODE_COUNT_MISMATCH" for e in rep_default.errors)

    custom_counts = BaselineCounts(
        total_nodes=20,
        suppliers=3,
        parts=5,
        products=2,
        orders=10,
        total_edges=22,
        supplies=7,
        used_in=5,
        fulfills=10,
    )
    custom_policy = ValidationPolicy(check_baseline_counts=True, baseline_counts=custom_counts)
    rep_custom = validate_raw_graph_data(raw_data, policy=custom_policy)
    assert rep_custom.valid is True


@pytest.mark.unit
def test_post_deletion_graph_passes_integrity_mode(canonical_graph):
    """
    After deleting a node, live graph fails baseline counts (as expected),
    but must pass structural integrity validation.
    """
    from backend.app.graph.traversal import trace_downstream_with_metrics
    descendants = trace_downstream_with_metrics(canonical_graph, "PART-05")["downstream_node_ids"]
    to_remove = set(descendants) | {"PART-05"}
    canonical_graph.remove_nodes_from(list(to_remove))

    rep_baseline = validate_networkx_graph(canonical_graph, policy=ValidationPolicy(check_baseline_counts=True))
    assert rep_baseline.valid is False
    assert any(e.code == "ERR_BASELINE_COUNT_MISMATCH" for e in rep_baseline.errors)

    rep_integrity = validate_networkx_graph(canonical_graph, policy=ValidationPolicy(check_baseline_counts=False))
    assert rep_integrity.valid is True
    assert len(rep_integrity.errors) == 0





@pytest.mark.unit
def test_canonical_edge_counts(raw_data, baseline_policy):
    """Verify exact edge counts: 21 total, 6 supplies, 5 used_in, 10 fulfills."""
    report = validate_raw_graph_data(raw_data, policy=baseline_policy)
    assert report.valid is True
    s = report.summary
    assert s["edge_count"] == 21
    assert s["supplies_count"] == 6
    assert s["used_in_count"] == 5
    assert s["fulfills_count"] == 10


@pytest.mark.unit
@pytest.mark.parametrize("edge_type,expected_count", [
    ("supplies", 6),
    ("used_in", 5),
    ("fulfills", 10),
])
def test_exact_edge_category_counts(raw_data, edge_type, expected_count):
    """Verify each edge category in JSON matches canonical count."""
    assert len(raw_data["edges"][edge_type]) == expected_count


@pytest.mark.unit
def test_missing_edge_source_detected(raw_data, integrity_policy):
    """Edge missing 'source' must be detected and report fatal error."""
    # Delete 'source' from first supplies edge
    del raw_data["edges"]["supplies"][0]["source"]
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_EDGE_SOURCE" for e in report.errors)


@pytest.mark.unit
def test_missing_edge_target_detected(raw_data, integrity_policy):
    """Edge missing 'target' must be detected and report fatal error."""
    del raw_data["edges"]["used_in"][0]["target"]
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MISSING_EDGE_TARGET" for e in report.errors)


@pytest.mark.unit
def test_nonexistent_source_reference_detected(raw_data, integrity_policy):
    """Edge pointing from nonexistent source node must fail reference validation."""
    raw_data["edges"]["supplies"][0]["source"] = "SUP-99_NONEXISTENT"
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_NONEXISTENT_SOURCE_NODE" for e in report.errors)
    err = next(e for e in report.errors if e.code == "ERR_NONEXISTENT_SOURCE_NODE")
    assert err.actual == "SUP-99_NONEXISTENT"


@pytest.mark.unit
def test_nonexistent_target_reference_detected(raw_data, integrity_policy):
    """Edge pointing to nonexistent target node must fail reference validation."""
    raw_data["edges"]["fulfills"][0]["target"] = "ORD-99_NONEXISTENT"
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_NONEXISTENT_TARGET_NODE" for e in report.errors)
    err = next(e for e in report.errors if e.code == "ERR_NONEXISTENT_TARGET_NODE")
    assert err.actual == "ORD-99_NONEXISTENT"


@pytest.mark.unit
def test_invalid_relation_name_detected(raw_data, integrity_policy):
    """Edge with wrong relation string (e.g. 'SHIPS_TO' instead of 'SUPPLIES') must fail."""
    raw_data["edges"]["supplies"][0]["relation"] = "SHIPS_TO"
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_RELATION_NAME" for e in report.errors)


@pytest.mark.unit
def test_malformed_edge_item_detected(raw_data, integrity_policy):
    """An edge record that is a string or list rather than a dict must fail."""
    raw_data["edges"]["used_in"].append("not_a_dictionary_edge")
    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_MALFORMED_EDGE_RECORD" for e in report.errors)





@pytest.mark.unit
def test_all_canonical_edges_follow_valid_direction(raw_data, baseline_policy):
    """Pristine graph must pass all directional checks with zero errors."""
    report = validate_raw_graph_data(raw_data, policy=baseline_policy)
    assert report.valid is True
    dir_check = next(c for c in report.checks if c.check_id == "EDGE_DIRECTIONS")
    assert dir_check.status == "PASS"


@pytest.mark.unit
def test_reversed_supplies_edge_detected(raw_data, integrity_policy):
    """Reversing supplies edge (PART -> SUP) must trigger direction error."""
    # Reverse first supplies edge: source: PART-01, target: SUP-01
    raw_data["edges"]["supplies"][0]["source"] = "PART-01"
    raw_data["edges"]["supplies"][0]["target"] = "SUP-01"

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in report.errors)


@pytest.mark.unit
def test_reversed_used_in_edge_detected(raw_data, integrity_policy):
    """Reversing used_in edge (PROD -> PART) must trigger direction error."""
    raw_data["edges"]["used_in"][0]["source"] = "PROD-01"
    raw_data["edges"]["used_in"][0]["target"] = "PART-01"

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in report.errors)


@pytest.mark.unit
def test_reversed_fulfills_edge_detected(raw_data, integrity_policy):
    """Reversing fulfills edge (ORD -> PROD) must trigger direction error."""
    raw_data["edges"]["fulfills"][0]["source"] = "ORD-01"
    raw_data["edges"]["fulfills"][0]["target"] = "PROD-01"

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in report.errors)


@pytest.mark.unit
def test_invalid_tier_jump_supplies_to_product(raw_data, integrity_policy):
    """A supplies edge connecting Supplier directly to Finished Product must fail direction check."""
    raw_data["edges"]["supplies"][0]["source"] = "SUP-01"
    raw_data["edges"]["supplies"][0]["target"] = "PROD-01"

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in report.errors)


@pytest.mark.unit
def test_invalid_tier_jump_part_to_order(raw_data, integrity_policy):
    """A fulfills edge connecting Part directly to Customer Order must fail direction check."""
    raw_data["edges"]["fulfills"][0]["source"] = "PART-01"
    raw_data["edges"]["fulfills"][0]["target"] = "ORD-01"

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in report.errors)
