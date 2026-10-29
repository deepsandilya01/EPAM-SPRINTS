"""
Unit Tests — Missing Entities, Missing IDs, and Attribute Validation
Ensures missing top-level structures, missing node fields, and empty identifiers
are detected and reported with helpful diagnostic metadata.
"""

import pytest

from graph_validation import validate_raw_graph_data


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

