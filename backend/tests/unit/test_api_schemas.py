"""
Unit tests for RE:Flow API Schemas (Sprint 1 API serialization contracts).
Tests cover:
- Graph Response Schemas (nodes, edges, summary, full graph response)
- Traversal Request and Response Schemas (node_id validation, direction enums, serialization)
- Validation Request and Response Schemas (error items, warning items, audit response contracts)
- JSON serialization and model dumping compatible with Flask jsonify()
"""

import pytest
from pydantic import ValidationError

from backend.app.schemas.graph import (
    EdgeResponseSchema,
    GraphFilterParamsSchema,
    GraphResponseSchema,
    NodeResponseSchema,
)
from backend.app.schemas.traversal import (
    TraversalDirection,
    TraversalRequestSchema,
    TraversalResponseSchema,
)
from backend.app.schemas.validation import (
    ValidationRequestSchema,
    ValidationResponseSchema,
)


class TestGraphSchemas:
    def test_node_response_schema_valid(self):
        node_data = {
            "id": "SUP-01",
            "name": "Apex Components",
            "tier": "supplier",
            "label": "Apex Components",
            "attributes": {"location": "Pune", "note": "Primary electronics vendor"},
        }
        schema = NodeResponseSchema.model_validate(node_data)
        assert schema.id == "SUP-01"
        assert schema.name == "Apex Components"
        assert schema.tier == "supplier"
        assert schema.attributes["location"] == "Pune"

        dump = schema.model_dump()
        assert dump["id"] == "SUP-01"

    def test_edge_response_schema_valid(self):
        edge_data = {
            "source": "SUP-01",
            "target": "PART-01",
            "relation": "SUPPLIES",
            "attributes": {"lead_time_hours": 24, "max_capacity_units_per_day": 100},
        }
        schema = EdgeResponseSchema.model_validate(edge_data)
        assert schema.source == "SUP-01"
        assert schema.target == "PART-01"
        assert schema.relation == "SUPPLIES"
        assert schema.attributes["lead_time_hours"] == 24

    def test_graph_summary_and_full_response_schema(self):
        graph_payload = {
            "summary": {
                "total_nodes": 2,
                "total_edges": 1,
                "node_counts": {"suppliers": 1, "parts": 1},
                "edge_counts": {"supplies": 1},
            },
            "nodes": [
                {"id": "SUP-01", "name": "Apex Components", "tier": "supplier"},
                {"id": "PART-01", "name": "Control Board", "tier": "part"},
            ],
            "edges": [
                {"source": "SUP-01", "target": "PART-01", "relation": "SUPPLIES"},
            ],
            "metadata": {"project": "RE:Flow"},
        }
        schema = GraphResponseSchema.model_validate(graph_payload)
        assert schema.summary.total_nodes == 2
        assert schema.summary.total_edges == 1
        assert len(schema.nodes) == 2
        assert len(schema.edges) == 1

        dump = schema.model_dump()
        assert dump["summary"]["total_nodes"] == 2

    def test_graph_filter_params_schema(self):
        params = GraphFilterParamsSchema(tier="supplier", relation="SUPPLIES")
        assert params.tier == "supplier"
        assert params.relation == "SUPPLIES"


class TestTraversalSchemas:
    def test_traversal_request_valid_defaults(self):
        req = TraversalRequestSchema(node_id="SUP-01")
        assert req.node_id == "SUP-01"
        assert req.direction == TraversalDirection.DOWNSTREAM
        assert req.max_depth is None

    def test_traversal_request_custom_options(self):
        req = TraversalRequestSchema(
            node_id="PART-01",
            direction=TraversalDirection.UPSTREAM,
            max_depth=3,
        )
        assert req.node_id == "PART-01"
        assert req.direction == TraversalDirection.UPSTREAM
        assert req.max_depth == 3

    def test_traversal_request_empty_id_rejected(self):
        with pytest.raises(ValidationError):
            TraversalRequestSchema(node_id="")
        with pytest.raises(ValidationError):
            TraversalRequestSchema(node_id="   ")

    def test_traversal_request_invalid_direction_rejected(self):
        with pytest.raises(ValidationError):
            TraversalRequestSchema(node_id="SUP-01", direction="sideways")

    def test_traversal_response_schema_canonical_format(self):
        resp_data = {
            "source_node": "SUP-01",
            "direction": "downstream",
            "visited_nodes": ["PART-01", "PROD-01", "ORD-01"],
            "total_nodes": 3,
        }
        resp = TraversalResponseSchema.model_validate(resp_data)
        assert resp.source_node == "SUP-01"
        assert resp.direction == "downstream"
        assert resp.visited_nodes == ["PART-01", "PROD-01", "ORD-01"]
        assert resp.total_nodes == 3

        dump = resp.model_dump()
        assert dump["source_node"] == "SUP-01"
        assert dump["total_nodes"] == 3

    def test_traversal_response_schema_extended_fields(self):
        resp_data = {
            "source_node": "SUP-01",
            "direction": "downstream",
            "visited_nodes": ["PART-01", "PROD-01", "ORD-01"],
            "total_nodes": 3,
            "paths": [["SUP-01", "PART-01", "PROD-01", "ORD-01"]],
            "blast_radius_by_tier": {
                "part": ["PART-01"],
                "product": ["PROD-01"],
                "order": ["ORD-01"],
            },
            "execution_time_ms": 0.42,
        }
        resp = TraversalResponseSchema.model_validate(resp_data)
        assert resp.execution_time_ms == 0.42
        assert len(resp.paths) == 1
        assert "order" in resp.blast_radius_by_tier


class TestValidationSchemas:
    def test_validation_request_defaults(self):
        req = ValidationRequestSchema()
        assert req.mode == "baseline"
        assert req.strict is True

    def test_validation_response_clean_pass(self):
        val_data = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "total_rules": 6,
            "passed_rules": 6,
            "failed_rules": 0,
        }
        resp = ValidationResponseSchema.model_validate(val_data)
        assert resp.is_valid is True
        assert len(resp.errors) == 0
        assert len(resp.warnings) == 0

        dump = resp.model_dump()
        assert dump["is_valid"] is True

    def test_validation_response_with_errors_and_warnings(self):
        val_data = {
            "is_valid": False,
            "errors": [
                {
                    "code": "CYCLE_DETECTED",
                    "message": "Cycle detected between PART-01 and PROD-01",
                    "entity_id": "PART-01",
                    "severity": "critical",
                }
            ],
            "warnings": [
                {
                    "code": "LOW_INVENTORY",
                    "message": "Stock is below safety threshold",
                    "entity_id": "PART-05",
                    "severity": "warning",
                }
            ],
            "total_rules": 6,
            "passed_rules": 4,
            "failed_rules": 2,
            "rules": [
                {
                    "rule_name": "acyclicity",
                    "passed": False,
                    "severity": "critical",
                    "message": "Topological cycle check failed",
                    "violations": [{"cycle": ["PART-01", "PROD-01", "PART-01"]}],
                }
            ],
        }
        resp = ValidationResponseSchema.model_validate(val_data)
        assert resp.is_valid is False
        assert len(resp.errors) == 1
        assert resp.errors[0].code == "CYCLE_DETECTED"
        assert len(resp.warnings) == 1
        assert resp.warnings[0].code == "LOW_INVENTORY"
        assert len(resp.rules) == 1
        assert resp.rules[0].rule_name == "acyclicity"
