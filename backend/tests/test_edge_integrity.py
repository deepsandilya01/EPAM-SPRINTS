"""
Unit Tests — Edge Integrity & Relationship Validation
Validates relationship categories, exact edge counts, endpoint existence,
and relation attributes.
"""

import pytest

from graph_validation import validate_raw_graph_data


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
