from __future__ import annotations

import time
from typing import Any

import networkx as nx


def get_downstream(G: nx.DiGraph, start: str) -> set[str]:
    """Find all reachable nodes downstream using BFS traversal."""
    if start not in G:
        return set()
    return set(nx.descendants(G, start))


# Compatibility alias
_downstream = get_downstream


def bfs_downstream_traversal(
    graph: nx.DiGraph,
    start_node_id: str,
    max_depth: int | None = None,
) -> dict[str, Any]:
    """
    Execute breadth-first search downstream traversal from start_node_id.

    Returns dictionary containing reachable node IDs, traversal depth,
    and directed paths.
    """
    if start_node_id not in graph:
        return {
            "root": start_node_id,
            "downstream_nodes": [],
            "total_impacted": 0,
            "depth": 0,
            "paths": [],
        }

    visited: list[str] = []
    queue: list[tuple[str, int, list[str]]] = [(start_node_id, 0, [start_node_id])]
    seen: set[str] = {start_node_id}
    max_reached_depth = 0
    all_paths: list[list[str]] = []

    while queue:
        current, depth, path = queue.pop(0)
        if current != start_node_id and current not in visited:
            visited.append(current)
            all_paths.append(path)
            if depth > max_reached_depth:
                max_reached_depth = depth

        if max_depth is not None and depth >= max_depth:
            continue

        for successor in graph.successors(current):
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, depth + 1, path + [successor]))

    return {
        "root": start_node_id,
        "downstream_nodes": visited,
        "total_impacted": len(visited),
        "depth": max_reached_depth,
        "paths": all_paths,
    }


def trace_downstream_with_metrics(
    graph: nx.DiGraph,
    source_node_id: str,
    threshold_ms: float = 10.0,
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
