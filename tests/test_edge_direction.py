"""
Unit Tests — Edge Direction and Tier Flow Validation
────────────────────────────────────────────────────
Enforces strict supply-chain dependency direction:
Supplier -> Part -> Finished Product -> Customer Order
"""

import pytest

from graph_validation import validate_raw_graph_data


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
