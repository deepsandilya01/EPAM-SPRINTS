"""
Unit Tests — Exact Supplier Reachability & Tracing Metrics
Asserts the exact expected downstream reachable descendants for both canonical
suppliers (SUP-01 and SUP-02), handles unknown IDs, and verifies traversal metrics.
"""

import pytest

from graph_validation import trace_downstream_with_metrics

# Ground-truth sets derived from canonical photon_sprint1_graph_data.json:
# SUP-01 supplies: PART-01, PART-02, PART-05
# PART-01 -> PROD-01, PART-02 -> PROD-01, PART-05 -> PROD-01
# PROD-01 fulfills: ORD-01, ORD-02, ORD-03, ORD-04, ORD-05, ORD-06
EXPECTED_SUP_01_DESCENDANTS = {
    "PART-01", "PART-02", "PART-05",
    "PROD-01",
    "ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05", "ORD-06",
}

# SUP-02 supplies: PART-03, PART-04, PART-05
# PART-03 -> PROD-02, PART-04 -> PROD-02
# PART-05 -> PROD-01 (Shared BOM component!)
# PROD-02 fulfills: ORD-07, ORD-08, ORD-09, ORD-10
# PROD-01 fulfills: ORD-01, ORD-02, ORD-03, ORD-04, ORD-05, ORD-06
EXPECTED_SUP_02_DESCENDANTS = {
    "PART-03", "PART-04", "PART-05",
    "PROD-01", "PROD-02",
    "ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05", "ORD-06",
    "ORD-07", "ORD-08", "ORD-09", "ORD-10",
}


@pytest.mark.unit
def test_exact_supplier_01_reachability(canonical_graph):
    """Verify SUP-01 reaches exactly the 10 ground-truth downstream nodes."""
    res = trace_downstream_with_metrics(canonical_graph, "SUP-01")
    assert res["source_exists"] is True
    assert res["source_node_id"] == "SUP-01"
    assert "SUP-01" not in res["downstream_node_ids"]  # Root excluded

    actual_set = set(res["downstream_node_ids"])
    assert actual_set == EXPECTED_SUP_01_DESCENDANTS
    assert len(actual_set) == 10
    assert res["visited_count"] == 10


@pytest.mark.unit
def test_exact_supplier_02_reachability(canonical_graph):
    """Verify SUP-02 reaches exactly the 15 ground-truth downstream nodes."""
    res = trace_downstream_with_metrics(canonical_graph, "SUP-02")
    assert res["source_exists"] is True
    assert res["source_node_id"] == "SUP-02"
    assert "SUP-02" not in res["downstream_node_ids"]  # Root excluded

    actual_set = set(res["downstream_node_ids"])
    assert actual_set == EXPECTED_SUP_02_DESCENDANTS
    assert len(actual_set) == 15
    assert res["visited_count"] == 15


@pytest.mark.unit
def test_unknown_supplier_reachability_handled_gracefully(canonical_graph):
    """Nonexistent node ID must return empty downstream list without crashing."""
    res = trace_downstream_with_metrics(canonical_graph, "SUP-NONEXISTENT")
    assert res["source_exists"] is False
    assert res["downstream_node_ids"] == []
    assert res["visited_count"] == 0
    assert res["under_threshold"] is True
    assert res["status"] == "PASS"


@pytest.mark.unit
def test_metrics_structure_and_resolution(canonical_graph):
    """Verify nanosecond and millisecond resolution metrics are present and non-negative."""
    res = trace_downstream_with_metrics(canonical_graph, "SUP-01", threshold_ms=10.0)
    assert res["elapsed_ns"] >= 0
    assert res["elapsed_ms"] >= 0.0
    assert res["threshold_ms"] == 10.0
    assert isinstance(res["under_threshold"], bool)
    assert res["status"] in ("PASS", "FAIL")


@pytest.mark.unit
def test_cyclic_graph_does_not_cause_infinite_loop(canonical_graph):
    """Even if cycles exist, NetworkX descendants traversal terminates safely without infinite loop."""
    # Introduce cycle: PROD-01 -> SUP-01
    canonical_graph.add_edge("PROD-01", "SUP-01", relation="SUPPLIES")
    res = trace_downstream_with_metrics(canonical_graph, "SUP-01")
    assert isinstance(res["downstream_node_ids"], list)
    assert res["status"] == "PASS"
