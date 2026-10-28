"""
Unit Tests — Duplicate Node Identifier Detection
─────────────────────────────────────────────────
Verifies that duplicate node identifiers in the raw JSON records are detected
BEFORE NetworkX graph construction, preventing silent identifier collisions.
"""

import copy
import pytest
import networkx as nx
from graph_validation import ValidationPolicy, validate_raw_graph_data


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

