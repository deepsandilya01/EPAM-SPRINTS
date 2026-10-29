"""
Team Photon — Downstream Tracing with Microsecond/Nanosecond Metrics
───────────────────────────────────────────────────────────────────
High-resolution monotonic downstream graph traversal timing and verification.
"""

import time
from typing import Any

import networkx as nx


def trace_downstream_with_metrics(
    graph: nx.DiGraph,
    source_node_id: str,
    threshold_ms: float = 10.0
) -> dict[str, Any]:
    """
    Perform a directed downstream reachability traversal from source_node_id
    and measure pure traversal execution latency using a monotonic high-resolution timer.

    Strict Measurement Rules:
    - Measures strictly the graph traversal operation (NetworkX BFS reachability).
    - Excludes graph loading, JSON parsing, API request parsing, and frontend rendering.
    - Accurately captures elapsed time in nanoseconds and milliseconds.
    - Evaluates against the configured threshold (default: 10.0 ms).

    Args:
        graph: The directed NetworkX graph instance.
        source_node_id: Identifier of the root entity to trace from.
        threshold_ms: Maximum permissible traversal latency in milliseconds (default: 10.0 ms).

    Returns:
        A dictionary with structured metrics including:
        - source_node_id (str)
        - source_exists (bool)
        - downstream_node_ids (List[str])
        - visited_count (int)
        - graph_node_count (int)
        - graph_edge_count (int)
        - elapsed_ns (int)
        - elapsed_ms (float)
        - threshold_ms (float)
        - under_threshold (bool)
        - status (str: "PASS" | "FAIL")
        - algorithm (str)
        - time_complexity (str)
    """
    if not isinstance(graph, (nx.DiGraph, nx.MultiDiGraph)):
        raise TypeError(f"Expected a directed NetworkX graph (DiGraph), got {type(graph).__name__}")

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

    # High-resolution monotonic timer for pure traversal
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
