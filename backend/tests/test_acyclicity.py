"""
Unit Tests — Conditional Acyclicity and DAG Validation
Tests acyclicity enforcement according to the three required policy modes:
1. REQUIRE_DAG: Must fail and report cycle path when cycles exist.
2. ALLOW_CYCLES: Must not fail merely because cycles exist.
3. UNSPECIFIED: Must report policy undefined warning rather than silently assuming.
"""

import networkx as nx
import pytest

from graph_validation import (
    AcyclicityPolicy,
    ValidationPolicy,
    validate_networkx_graph,
)


@pytest.mark.unit
def test_canonical_graph_is_acyclic(canonical_graph, baseline_policy):
    """Canonical graph must be a verified Directed Acyclic Graph."""
    assert nx.is_directed_acyclic_graph(canonical_graph) is True
    report = validate_networkx_graph(canonical_graph, policy=baseline_policy)
    assert report.valid is True
    check = next(c for c in report.checks if c.check_id == "GRAPH_ACYCLICITY")
    assert check.status == "PASS"


@pytest.mark.unit
def test_cyclic_graph_fails_when_dag_required(raw_data):
    """Adding a back-edge to create a cycle must fail when policy is REQUIRE_DAG."""
    G = nx.DiGraph()
    for cat in raw_data["nodes"]:
        for n in raw_data["nodes"][cat]:
            G.add_node(n["id"], **n)
    for edge_type in raw_data["edges"]:
        for e in raw_data["edges"][edge_type]:
            attrs = {k: v for k, v in e.items() if k not in ("source", "target")}
            G.add_edge(e["source"], e["target"], **attrs)

    # Add cycle edge: PROD-01 -> PART-01
    G.add_edge("PROD-01", "PART-01", relation="USED_IN")

    policy = ValidationPolicy(check_baseline_counts=False, acyclicity_policy=AcyclicityPolicy.REQUIRE_DAG)
    report = validate_networkx_graph(G, policy=policy)
    assert report.valid is False
    assert any(e.code == "ERR_CYCLE_DETECTED" for e in report.errors)
    cycle_err = next(e for e in report.errors if e.code == "ERR_CYCLE_DETECTED")
    assert "PART-01" in cycle_err.message
    assert "PROD-01" in cycle_err.message


@pytest.mark.unit
def test_cyclic_graph_permitted_when_policy_allows_cycles(canonical_graph):
    """When policy allows cycles, the presence of a cycle must not reject the graph."""
    canonical_graph.add_edge("PROD-01", "PART-01", relation="USED_IN")
    assert nx.is_directed_acyclic_graph(canonical_graph) is False

    policy = ValidationPolicy(
        check_baseline_counts=False,
        acyclicity_policy=AcyclicityPolicy.ALLOW_CYCLES,
    )
    report = validate_networkx_graph(canonical_graph, policy=policy)
    assert not any(e.code == "ERR_CYCLE_DETECTED" for e in report.errors)
    check = next(c for c in report.checks if c.check_id == "GRAPH_ACYCLICITY")
    assert check.status == "SKIP"


@pytest.mark.unit
def test_unspecified_acyclicity_policy_reports_warning(canonical_graph):
    """When acyclicity policy is unspecified, report must generate a warning rather than silent assumption."""
    policy = ValidationPolicy(
        check_baseline_counts=False,
        acyclicity_policy=AcyclicityPolicy.UNSPECIFIED,
    )
    report = validate_networkx_graph(canonical_graph, policy=policy)
    check = next(c for c in report.checks if c.check_id == "GRAPH_ACYCLICITY")
    assert check.status == "WARN"
    assert any(w.code == "WARN_ACYCLICITY_POLICY_UNDEFINED" for w in report.warnings)

