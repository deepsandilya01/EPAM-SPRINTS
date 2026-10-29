"""
Unit Tests — Reporting Utilities
─────────────────────────────────
Validates console formatting and JSON persistence of ValidationReport objects.
"""

import json
import pytest
from graph_validation import (
    format_console_report,
    save_json_report,
    validate_raw_graph_data,
)


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

