from __future__ import annotations

import copy
from typing import Any

import networkx as nx


def graph_to_json(G: nx.DiGraph) -> dict[str, list[dict[str, Any]]]:
    """Format graph into nodes and edges lists for JSON serialization and UI."""
    nodes = [{**attrs, "id": nid} for nid, attrs in G.nodes(data=True)]
    edges = [{"source": src, "target": tgt, **attrs} for src, tgt, attrs in G.edges(data=True)]
    return {"nodes": nodes, "edges": edges, "links": edges}


def snapshot_graph(G: nx.DiGraph) -> dict[str, Any]:
    """Take a deep copy of current graph state before a mutation."""
    return {
        "nodes": {n: copy.deepcopy(d) for n, d in G.nodes(data=True)},
        "edges": [(u, v, copy.deepcopy(d)) for u, v, d in G.edges(data=True)],
    }


def restore_graph(G: nx.DiGraph, snap: dict[str, Any]) -> None:
    """Restore nodes and edges from a previous snapshot."""
    G.clear()
    for nid, attrs in snap["nodes"].items():
        G.add_node(nid, **attrs)
    for u, v, attrs in snap["edges"]:
        G.add_edge(u, v, **attrs)


def get_nodes_by_tier(graph: nx.DiGraph, tier: str) -> list[dict[str, Any]]:
    """Return all nodes belonging to a specific tier/kind."""
    tier_lower = tier.lower().strip()
    return [
        {**attrs, "id": nid}
        for nid, attrs in graph.nodes(data=True)
        if attrs.get("kind", "").lower() == tier_lower
        or attrs.get("tier", "").lower() == tier_lower
    ]


def get_node_details(graph: nx.DiGraph, node_id: str) -> dict[str, Any] | None:
    """Return dictionary of attributes for a specific node ID, or None if missing."""
    if node_id not in graph:
        return None
    return {**dict(graph.nodes[node_id]), "id": node_id}


def get_subgraph(graph: nx.DiGraph, node_ids: set[str] | list[str]) -> nx.DiGraph:
    """Extract an induced subgraph containing only the specified node IDs."""
    return graph.subgraph(node_ids).copy()


def calculate_graph_metrics(graph: nx.DiGraph) -> dict[str, Any]:
    """Calculate degree metrics and density for the graph."""
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "density": nx.density(graph),
        "in_degrees": in_degrees,
        "out_degrees": out_degrees,
    }


# Aliases for compatibility with original PHOTON source code
_graph_to_json = graph_to_json
_snapshot = snapshot_graph
_restore = restore_graph
