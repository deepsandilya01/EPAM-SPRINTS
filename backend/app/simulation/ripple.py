from __future__ import annotations

from typing import List, Set
import networkx as nx

from backend.app.models.disruption import DisruptionEvent
from backend.app.models.impact import RippleImpactSummary


def propagate_ripple_effect(
    graph: nx.DiGraph,
    event: DisruptionEvent,
) -> RippleImpactSummary:
    """
    Traverse downstream from a disrupted supplier using Breadth-First Search (BFS).

    Cycle and multi-parent safe traversal using a visited set ensures no node
    (e.g., shared Bill-of-Materials components or multi-source products)
    is processed more than once.

    Categorizes reachable downstream nodes into:
    - affected_parts: BOM components (Tier 2)
    - affected_products: Finished assemblies (Tier 3)
    - affected_orders: Customer purchase orders (Tier 4)
    """
    supplier_id = event.supplier_id

    if supplier_id not in graph:
        raise ValueError(f"Supplier {supplier_id} not found in graph")

    visited: Set[str] = set()
    queue: List[str] = [supplier_id]

    affected_parts: List[str] = []
    affected_products: List[str] = []
    affected_orders: List[str] = []

    while queue:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)

        # Do not categorize the disrupted supplier root itself
        if node_id != supplier_id:
            node_data = graph.nodes.get(node_id, {})

            # Resilient node typing across raw JSON dictionaries, canonical domain models,
            # and synthetic test fixtures (checks 'type', 'tier', 'kind', and standard prefixes)
            raw_type = (
                node_data.get("type")
                or node_data.get("tier")
                or node_data.get("kind")
                or ""
            )
            type_str = str(raw_type).strip().upper()

            if (
                type_str in ("PART", "PARTS", "BOM_PART", "BOM_PARTS")
                or node_id.startswith(("PART-", "P-"))
            ):
                affected_parts.append(node_id)
            elif (
                type_str in ("PRODUCT", "PRODUCTS", "FINISHED_PRODUCT", "FINISHED_PRODUCTS")
                or node_id.startswith(("PROD-", "PRODUCT-"))
            ):
                affected_products.append(node_id)
            elif (
                type_str in ("ORDER", "ORDERS", "CUSTOMER_ORDER", "CUSTOMER_ORDERS")
                or node_id.startswith(("ORD-", "ORDER-"))
            ):
                affected_orders.append(node_id)

        # Traverse downstream directed successors
        for neighbor in graph.successors(node_id):
            if neighbor not in visited:
                queue.append(neighbor)

    return RippleImpactSummary(
        disrupted_supplier=supplier_id,
        affected_parts=affected_parts,
        affected_products=affected_products,
        affected_orders=affected_orders,
        total_affected_nodes=max(0, len(visited) - 1),
    )


__all__ = ["propagate_ripple_effect"]

