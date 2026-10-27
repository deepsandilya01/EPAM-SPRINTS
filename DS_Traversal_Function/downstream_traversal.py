"""Downstream dependency traversal for Team Photon Sprint 1.

This module accepts an already-built NetworkX directed graph and a supplier ID.
It returns reachable parts, products, and orders in separate sorted lists.

Expected node attribute:
    kind="supplier" | "part" | "product" | "order"

It also supports node_type as a fallback for compatibility with other graph builders.
"""

import networkx as nx


def find_downstream_dependencies(graph: nx.DiGraph, supplier_id: str) -> dict:
    """Return all downstream parts, products, and orders for a supplier."""
    # Validate that the requested node exists.
    if supplier_id not in graph:
        raise ValueError(f"Supplier '{supplier_id}' not found.")

    # Validate that the starting node is a supplier.
    supplier_type = (
        graph.nodes[supplier_id].get("kind")
        or graph.nodes[supplier_id].get("node_type")
    )
    if supplier_type != "supplier":
        raise ValueError(f"'{supplier_id}' is not a supplier.")

    # Find every node reachable by following the directed edges.
    downstream_nodes = nx.descendants(graph, supplier_id)

    result = {"parts": [], "products": [], "orders": []}
    type_mapping = {
        "part": "parts",
        "product": "products",
        "order": "orders",
    }

    # Group reachable node IDs by their type.
    for node_id in downstream_nodes:
        node_type = (
            graph.nodes[node_id].get("kind")
            or graph.nodes[node_id].get("node_type")
        )
        category = type_mapping.get(node_type)
        if category is not None:
            result[category].append(node_id)

    # Stable output makes testing and comparison easier.
    for category in result:
        result[category].sort()

    return result
