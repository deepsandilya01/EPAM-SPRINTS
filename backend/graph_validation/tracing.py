"""
High-resolution downstream reachability tracing and performance measurement.
Measures pure graph traversal latency with a monotonic timer to verify the <10ms SLA.
"""

from __future__ import annotations

import time
from typing import Any
import networkx as nx
def trace_downstream_with_metrics(
    graph: nx.DiGraph,
    source_node_id: str,
    threshold_ms: float = 10.0
) -> dict[str, Any]:
    """
    Trace all reachable downstream nodes from source_node_id using BFS (nx.descendants).
    Times purely the graph traversal operation (ignoring JSON serialization or network I/O).
    """
    if not isinstance(graph, (nx.DiGraph, nx.MultiDiGraph)):
        raise TypeError(f"Expected a directed NetworkX graph, got {type(graph).__name__}")

    source_exists = source_node_id in graph

    if not source_exists:
        return {
            "source_node_id": source_node_id,
            "source_exists": False,
            "downstream_node_ids": [],
            "visited_count": 0,
            "graph_node_count": graph.number_of_nodes(),
            "graph_edge_count": graph.number_of_edges(),
            "elapsed_ns": 0,
            "elapsed_ms": 0.0,
            "threshold_ms": float(threshold_ms),
            "under_threshold": True,
            "status": "PASS",
            "message": f"Node '{source_node_id}' does not exist in graph.",
            "algorithm": "NetworkX BFS descendants",
            "time_complexity": "O(V + E)",
        }

    # Measure pure traversal latency using high-resolution monotonic timer
    t0 = time.perf_counter_ns()
    descendants = nx.descendants(graph, source_node_id)
    t1 = time.perf_counter_ns()

    elapsed_ns = t1 - t0
    elapsed_ms = elapsed_ns / 1_000_000.0
    under_threshold = elapsed_ms <= threshold_ms

    return {
        "source_node_id": source_node_id,
        "source_exists": True,
        "downstream_node_ids": sorted(descendants),
        "visited_count": len(descendants),
        "graph_node_count": graph.number_of_nodes(),
        "graph_edge_count": graph.number_of_edges(),
        "elapsed_ns": elapsed_ns,
        "elapsed_ms": round(elapsed_ms, 6),
        "threshold_ms": float(threshold_ms),
        "under_threshold": under_threshold,
        "status": "PASS" if under_threshold else "FAIL",
        "algorithm": "NetworkX BFS descendants",
        "time_complexity": "O(V + E)",
    }
