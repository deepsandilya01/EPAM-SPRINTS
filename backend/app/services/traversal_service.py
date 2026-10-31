from __future__ import annotations

from typing import Any

from backend.app.graph.traversal import get_downstream
from backend.app.services.graph_service import GraphService, service_instance


class TraversalService:
    """Service for computing downstream reachability, blast radius, and cascade impacts."""

    def __init__(self, graph_service: GraphService | None = None) -> None:
        self.graph_service = graph_service or service_instance

    def get_downstream_reachability(self, node_id: str) -> dict[str, Any] | None:
        """Compute downstream reachable node IDs from starting node."""
        graph = self.graph_service.get_graph()
        if node_id not in graph:
            return None

        reachable = get_downstream(graph, node_id)
        downstream_list = sorted(list(reachable))
        return {
            "root": node_id,
            "node_id": node_id,
            "downstream": downstream_list,
            "count": len(downstream_list),
        }

    def get_downstream_impact(self, node_id: str) -> dict[str, Any] | None:
        """Compute comprehensive blast-radius and cascading deletion impact preview."""
        graph = self.graph_service.get_graph()
        if node_id not in graph:
            return None

        node_attrs = dict(graph.nodes[node_id])
        direct_outgoing = [
            {"source": u, "target": v, **d}
            for u, v, d in graph.out_edges(node_id, data=True)
        ]
        direct_incoming = [
            {"source": u, "target": v, **d}
            for u, v, d in graph.in_edges(node_id, data=True)
        ]

        downstream_nodes = get_downstream(graph, node_id)
        downstream_details = []
        for nid in sorted(downstream_nodes):
            attrs = dict(graph.nodes[nid])
            downstream_details.append({
                "id": nid,
                "kind": attrs.get("kind", ""),
                "label": attrs.get("label", nid),
                **attrs,
            })

        all_impacted_nodes = downstream_nodes | {node_id}
        edges_to_remove = []
        for u, v, attrs in graph.edges(data=True):
            if u in all_impacted_nodes or v in all_impacted_nodes:
                edges_to_remove.append({
                    "source": u,
                    "target": v,
                    "relation": attrs.get("relation", ""),
                })

        return {
            "node": {"id": node_id, **node_attrs},
            "target_node": {
                "id": node_id,
                "kind": node_attrs.get("kind", ""),
                "label": node_attrs.get("label", node_id),
                **node_attrs,
            },
            "outgoing_edges": direct_outgoing,
            "incoming_edges": direct_incoming,
            "direct_outgoing_edges": direct_outgoing,
            "direct_incoming_edges": direct_incoming,
            "downstream_nodes": sorted(list(downstream_nodes)),
            "downstream_node_ids": sorted(list(downstream_nodes)),
            "affected_nodes_details": downstream_details,
            "downstream_nodes_detailed": downstream_details,
            "total_nodes_affected": len(all_impacted_nodes),
            "total_edges_affected": len(edges_to_remove),
            "edges_to_remove": edges_to_remove,
            "time_complexity": "O(V + E)",
            "time_complexity_explanation": f"Traversal & cascade removal visits {len(all_impacted_nodes)} vertices and inspects {len(edges_to_remove)} edges in O(V + E) time.",
        }


# Module-level singleton
traversal_service = TraversalService()
