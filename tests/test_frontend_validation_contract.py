"""
Unit & Contract Tests — Frontend Validation Response Contract
─────────────────────────────────────────────────────────────
Verifies that the validation and benchmark API endpoints return the exact JSON
shape, field types, and vocabulary required by the D3.js frontend UI panel.
"""

import pytest


@pytest.mark.unit
def test_validation_api_response_contract(app_client):
    """Ensure /api/validation schema matches the frontend rendering expectations."""
    res = app_client.get("/api/validation")
    assert res.status_code == 200
    data = res.get_json()

    # Top-level contract
    assert isinstance(data.get("valid"), bool)
    assert isinstance(data.get("graph_name"), str)
    assert isinstance(data.get("mode"), str)
    assert isinstance(data.get("summary"), dict)
    assert isinstance(data.get("checks"), list)
    assert isinstance(data.get("errors"), list)
    assert isinstance(data.get("warnings"), list)
    assert isinstance(data.get("policy"), dict)
    assert isinstance(data.get("timestamp"), str)

    # Summary counts contract
    s = data["summary"]
    for key in ("node_count", "edge_count", "supplier_count", "part_count", "product_count", "order_count"):
        assert key in s, f"Missing key in summary: {key}"
        assert isinstance(s[key], int), f"Field {key} must be an integer"
        assert s[key] >= 0

    # Checks array vocabulary contract
    allowed_statuses = {"PASS", "FAIL", "WARN", "SKIP"}
    for check in data["checks"]:
        assert "check_id" in check and isinstance(check["check_id"], str)
        assert "status" in check and check["status"] in allowed_statuses
        assert "message" in check and isinstance(check["message"], str)

    # Errors array contract
    for err in data["errors"]:
        assert "code" in err and isinstance(err["code"], str)
        assert "message" in err and isinstance(err["message"], str)
        assert "severity" in err and isinstance(err["severity"], str)


@pytest.mark.unit
def test_benchmark_api_response_contract(app_client):
    """Ensure /api/benchmark/tracing schema matches the frontend panel requirements."""
    res = app_client.get("/api/benchmark/tracing?node_id=SUP-01")
    assert res.status_code == 200
    data = res.get_json()

    assert "source_node_id" in data and isinstance(data["source_node_id"], str)
    assert "source_exists" in data and isinstance(data["source_exists"], bool)
    assert "downstream_node_ids" in data and isinstance(data["downstream_node_ids"], list)
    assert "visited_count" in data and isinstance(data["visited_count"], int)
    assert "elapsed_ms" in data and isinstance(data["elapsed_ms"], (int, float))
    assert "threshold_ms" in data and isinstance(data["threshold_ms"], (int, float))
    assert "under_threshold" in data and isinstance(data["under_threshold"], bool)
    assert "status" in data and data["status"] in ("PASS", "FAIL")
    assert "time_complexity" in data and isinstance(data["time_complexity"], str)

