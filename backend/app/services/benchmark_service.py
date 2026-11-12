from __future__ import annotations

from typing import Any

from backend.app.graph.traversal import trace_downstream_with_metrics
from backend.app.services.graph_service import GraphService, service_instance


class BenchmarkService:
    """Service managing downstream tracing latency benchmarks and SLA validation."""

    def __init__(self, graph_service: GraphService | None = None) -> None:
        self.graph_service = graph_service or service_instance

    def run_tracing_benchmark(
        self,
        node_id: str = "SUP-01",
        threshold_param: str | float = "10.0",
    ) -> tuple[dict[str, Any], int]:
        """Benchmark downstream reachability traversal against the SLA threshold."""
        try:
            threshold_ms = float(threshold_param)
            if threshold_ms <= 0:
                return {
                    "error": "threshold_ms must be a positive number",
                    "under_threshold": False,
                }, 400
        except (ValueError, TypeError):
            return {
                "error": f"Invalid threshold_ms value: '{threshold_param}'. Expected numeric value.",
                "under_threshold": False,
            }, 400

        graph = self.graph_service.get_graph()
        metrics = trace_downstream_with_metrics(graph, node_id, threshold_ms=threshold_ms)
        return metrics, 200

    def run_construction_benchmark(self, iterations: int = 100) -> dict[str, Any]:
        """Run micro-benchmark measuring graph construction latency."""
        from backend.app.benchmarks.benchmark_graph import run_graph_construction_benchmark

        return run_graph_construction_benchmark(iterations=iterations)


# Module-level singleton
benchmark_service = BenchmarkService()
