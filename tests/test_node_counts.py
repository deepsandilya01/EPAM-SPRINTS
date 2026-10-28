"""
Unit Tests — Node and Category Counts Validation
─────────────────────────────────────────────────
Validates exact entity counts against the Sprint 1 baseline specification:
- 19 Total nodes
- 2 Suppliers (SUP-01, SUP-02)
- 5 Parts (PART-01 through PART-05)
- 2 Products (PROD-01, PROD-02)
- 10 Customer Orders (ORD-01 through ORD-10)
"""

import pytest
from graph_validation import (
    BaselineCounts,
    ValidationPolicy,
    validate_raw_graph_data,
    validate_networkx_graph,
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
    from graph_validation.tracing import trace_downstream_with_metrics
    descendants = trace_downstream_with_metrics(canonical_graph, "PART-05")["downstream_node_ids"]
    to_remove = set(descendants) | {"PART-05"}
    canonical_graph.remove_nodes_from(list(to_remove))

    rep_baseline = validate_networkx_graph(canonical_graph, policy=ValidationPolicy(check_baseline_counts=True))
    assert rep_baseline.valid is False
    assert any(e.code == "ERR_BASELINE_COUNT_MISMATCH" for e in rep_baseline.errors)

    rep_integrity = validate_networkx_graph(canonical_graph, policy=ValidationPolicy(check_baseline_counts=False))
    assert rep_integrity.valid is True
    assert len(rep_integrity.errors) == 0

