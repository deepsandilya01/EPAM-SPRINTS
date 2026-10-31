from __future__ import annotations

from typing import Any

from backend.app.services.graph_service import GraphService, service_instance
from backend.app.validation import (
    AcyclicityPolicy,
    ValidationPolicy,
    validate_networkx_graph,
    validate_raw_graph_data,
)


class ValidationService:
    """Service executing graph and raw dataset integrity validations."""

    def __init__(self, graph_service: GraphService | None = None) -> None:
        self.graph_service = graph_service or service_instance

    def validate_graph(
        self,
        mode_param: str | None = None,
        strict: bool = False,
    ) -> tuple[dict[str, Any], int]:
        """Validate live in-memory graph under baseline or integrity policies."""
        graph = self.graph_service.get_graph()

        if mode_param:
            mode_clean = mode_param.strip().lower()
            if mode_clean not in ("baseline", "integrity"):
                return {
                    "error": f"Invalid mode '{mode_param}'. Allowed modes: baseline, integrity",
                    "valid": False,
                }, 400
            is_baseline = mode_clean == "baseline"
            mode = "baseline" if is_baseline else "integrity"
        else:
            # Auto-detect mode based on node/edge counts
            is_baseline = graph.number_of_nodes() == 19 and graph.number_of_edges() == 21
            mode = "baseline" if is_baseline else "integrity"

        policy = ValidationPolicy(
            check_baseline_counts=is_baseline,
            acyclicity_policy=AcyclicityPolicy.REQUIRE_DAG,
        )
        report = validate_networkx_graph(graph, policy=policy)
        report.mode = mode

        status_code = 200
        if strict and not report.valid:
            status_code = 422

        return report.to_dict(), status_code

    def validate_raw_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Validate raw dictionary dataset before graph construction."""
        report = validate_raw_graph_data(raw_data)
        return report.to_dict()


# Module-level singleton
validation_service = ValidationService()
