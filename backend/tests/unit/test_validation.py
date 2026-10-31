from __future__ import annotations

import copy
import json

import networkx as nx
import pytest

from backend.app.validation import (
    AcyclicityPolicy,
    ValidationPolicy,
    format_console_report,
    save_json_report,
    validate_networkx_graph,
    validate_raw_graph_data,
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






@pytest.mark.unit
def test_duplicate_node_id_within_same_category(raw_data, integrity_policy):
    """Detect duplicate node ID when two parts share the ID 'PART-01'."""
    dup_part = copy.deepcopy(raw_data["nodes"]["parts"][0])
    dup_part["label"] = "Duplicate Control Board"
    raw_data["nodes"]["parts"].append(dup_part)

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_DUPLICATE_NODE_ID" for e in report.errors)
    dup_err = next(e for e in report.errors if e.code == "ERR_DUPLICATE_NODE_ID")
    assert dup_err.entity_id == "PART-01"


@pytest.mark.unit
def test_duplicate_node_id_across_different_categories(raw_data, integrity_policy):
    """Detect duplicate node ID when an order is given the same ID as a supplier ('SUP-01')."""
    dup_order = {
        "id": "SUP-01",  # Collision with supplier SUP-01!
        "kind": "order",
        "label": "Conflicting Order",
        "order_id": "ORD-99",
        "customer": "Rogue Customer",
        "product_id": "PROD-01",
        "quantity": 10,
        "deadline": "2026-12-01",
    }
    raw_data["nodes"]["orders"].append(dup_order)

    report = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert report.valid is False
    assert any(e.code == "ERR_DUPLICATE_NODE_ID" for e in report.errors)
    dup_err = next(e for e in report.errors if e.code == "ERR_DUPLICATE_NODE_ID")
    assert dup_err.entity_id == "SUP-01"


@pytest.mark.unit
def test_networkx_silent_collapse_proof(raw_data):
    """
    Explicit proof test: Show that a naive NetworkX DiGraph constructor
    silently collapses duplicate IDs to 1 node, whereas validate_raw_graph_data
    catches and rejects the collision.
    """
    dup_part = copy.deepcopy(raw_data["nodes"]["parts"][0])
    raw_data["nodes"]["parts"].append(dup_part)

    # 1. Naive NetworkX construction collapses to 19 nodes!
    naive_g = nx.DiGraph()
    for cat in raw_data["nodes"]:
        for n in raw_data["nodes"][cat]:
            naive_g.add_node(n["id"], **n)

    # Naive graph has 19 nodes despite 20 records in raw JSON!
    assert naive_g.number_of_nodes() == 19

    # 2. Raw validator detects the collision before construction
    report = validate_raw_graph_data(raw_data, policy=ValidationPolicy(check_baseline_counts=False))
    assert report.valid is False
    assert any(e.code == "ERR_DUPLICATE_NODE_ID" for e in report.errors)






@pytest.mark.unit
def test_format_console_report_baseline(raw_data, baseline_policy):
    """Verify format_console_report formats baseline report cleanly."""
    rep = validate_raw_graph_data(raw_data, policy=baseline_policy)
    text = format_console_report(rep)
    assert "TEAM PHOTON" in text
    assert "[PASS]" in text
    assert "Total Nodes" in text
    assert "Total Edges" in text
    assert "VALIDATION CHECKS:" in text


@pytest.mark.unit
def test_format_console_report_with_errors(raw_data, integrity_policy):
    """Verify format_console_report includes error and warning sections when issues exist."""
    raw_data["nodes"]["parts"].append(dict(raw_data["nodes"]["parts"][0]))
    raw_data["edges"]["supplies"][0]["source"] = "PART-01"
    raw_data["edges"]["supplies"][0]["target"] = "SUP-01"

    rep = validate_raw_graph_data(raw_data, policy=integrity_policy)
    assert rep.valid is False
    text = format_console_report(rep)
    assert "[FAIL]" in text
    assert "ERRORS" in text
    assert "ERR_DUPLICATE_NODE_ID" in text
    assert "ERR_INVALID_EDGE_DIRECTION" in text


@pytest.mark.unit
def test_save_json_report_to_disk(raw_data, baseline_policy, tmp_path):
    """Verify save_json_report safely writes report JSON to disk."""
    rep = validate_raw_graph_data(raw_data, policy=baseline_policy)
    target_file = tmp_path / "subdir" / "test_report.json"
    saved_path = save_json_report(rep, target_file)

    assert saved_path.exists()
    with open(saved_path, encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["valid"] is True
    assert loaded["summary"]["node_count"] == 19
