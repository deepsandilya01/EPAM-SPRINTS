"""
Unit Tests — Malformed Input & Defensive Parsing
Validates graceful handling of non-dictionary payloads, wrong data types,
empty graphs, and JSON serializability of reports.
"""

import json

import pytest

from graph_validation import ValidationPolicy, validate_raw_graph_data


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

