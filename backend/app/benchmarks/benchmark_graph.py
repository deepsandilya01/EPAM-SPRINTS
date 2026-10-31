from __future__ import annotations

import pathlib
import platform
import sys
import time
from typing import Any

from backend.app.benchmarks.benchmark_results import BenchmarkResultAggregator
from backend.app.data.loader import load_scenario_dataset
from backend.app.graph.builder import build_graph


def run_graph_construction_benchmark(
    iterations: int = 100,
    dataset_path: str | pathlib.Path | None = None,
) -> dict[str, Any]:
    """
    Measure NetworkX DiGraph construction latency over multiple iterations.
    """
    raw_data = load_scenario_dataset(dataset_path)
    aggregator = BenchmarkResultAggregator(
        operation_name="Graph Construction (build_graph)",
        sla_threshold_ms=50.0,
    )

    # Warmup run
    build_graph(raw_data)

    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        G = build_graph(raw_data)
        t1 = time.perf_counter_ns()
        aggregator.record((t1 - t0) / 1_000_000.0)

    stats = aggregator.compute_statistics()
    stats["environment"] = {
        "python_version": sys.version.split()[0],
        "system": platform.system(),
        "release": platform.release(),
    }
    stats["node_count"] = G.number_of_nodes()
    stats["edge_count"] = G.number_of_edges()
    return stats
