from __future__ import annotations

import json
import logging
import pathlib
import threading
import time
from typing import Any

import networkx as nx

from backend.app.data.loader import load_scenario_dataset
from backend.app.graph.builder import build_graph
from backend.app.graph.operations import graph_to_json, restore_graph, snapshot_graph
from backend.app.graph.traversal import get_downstream
from backend.app.validation import validate_raw_graph_data

logger = logging.getLogger(__name__)

# Serverless and multi-client state tracking constants
STATE_COOKIE = "photon_history"
_STATE_LOCK = threading.RLock()


class GraphService:
    """Service managing in-memory graph state, undo stack, mutations, and traversals."""

    def __init__(self, data_path: str | pathlib.Path | None = None) -> None:
        self.data_path = data_path
        self.raw_data = load_scenario_dataset(self.data_path)
        self.startup_report = validate_raw_graph_data(self.raw_data)
        if not self.startup_report.valid:
            logger.warning(
                f"Baseline graph validation warning: {len(self.startup_report.errors)} errors."
            )

        self.graph: nx.DiGraph = build_graph(self.raw_data)
        self.undo_stack: list[dict[str, Any]] = []
        self.history: list[str] = []

    def get_graph(self) -> nx.DiGraph:
        """Return the active NetworkX graph instance."""
        return self.graph

    def get_domain_graph(self) -> Any | None:
        """Return the SupplyChainGraph domain model aggregate if available."""
        return self.graph.graph.get("domain_model")

    def get_graph_json(self) -> dict[str, Any]:
        """Return graph nodes and edges serializable to JSON."""
        return graph_to_json(self.graph)

    def get_downstream_reachability(self, node_id: str) -> dict[str, Any] | None:
        """Compute downstream reachable node IDs from starting node."""
        if node_id not in self.graph:
            return None

        reachable = get_downstream(self.graph, node_id)
        downstream_list = sorted(list(reachable))
        return {
            "root": node_id,
            "node_id": node_id,
            "downstream": downstream_list,
            "count": len(downstream_list),
        }

    def get_downstream_impact(self, node_id: str) -> dict[str, Any] | None:
        """Compute comprehensive blast-radius and cascading deletion impact preview."""
        if node_id not in self.graph:
            return None

        node_attrs = dict(self.graph.nodes[node_id])
        direct_outgoing = [
            {"source": u, "target": v, **d}
            for u, v, d in self.graph.out_edges(node_id, data=True)
        ]
        direct_incoming = [
            {"source": u, "target": v, **d}
            for u, v, d in self.graph.in_edges(node_id, data=True)
        ]

        downstream_nodes = get_downstream(self.graph, node_id)
        downstream_details = []
        for nid in sorted(downstream_nodes):
            attrs = dict(self.graph.nodes[nid])
            downstream_details.append(
                {
                    "id": nid,
                    "kind": attrs.get("kind", ""),
                    "label": attrs.get("label", nid),
                    **attrs,
                }
            )

        all_impacted_nodes = downstream_nodes | {node_id}
        edges_to_remove = []
        for u, v, attrs in self.graph.edges(data=True):
            if u in all_impacted_nodes or v in all_impacted_nodes:
                edges_to_remove.append(
                    {
                        "source": u,
                        "target": v,
                        "relation": attrs.get("relation", ""),
                    }
                )

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
            "time_complexity_explanation": (
                f"Traversal & cascade removal visits {len(all_impacted_nodes)} vertices "
                f"and inspects {len(edges_to_remove)} edges in O(V + E) time."
            ),
        }

    def apply_delete(self, node_id: str) -> dict[str, Any]:
        """Delete node_id plus downstream cascade, push an undo snapshot, and return metrics."""
        t0 = time.perf_counter()
        snap = snapshot_graph(self.graph)

        to_remove = get_downstream(self.graph, node_id) | {node_id}
        removed_nodes_info = []
        for nid in sorted(to_remove):
            attrs = dict(self.graph.nodes[nid])
            removed_nodes_info.append(
                {
                    "id": nid,
                    "kind": attrs.get("kind", ""),
                    "label": attrs.get("label", nid),
                }
            )

        edges_removed_list = []
        for u, v, attrs in list(self.graph.edges(data=True)):
            if u in to_remove or v in to_remove:
                edges_removed_list.append(
                    {
                        "source": u,
                        "target": v,
                        "relation": attrs.get("relation", ""),
                    }
                )

        target_attrs = dict(self.graph.nodes[node_id])
        target_label = target_attrs.get("label", node_id)
        target_kind = target_attrs.get("kind", "")

        self.graph.remove_nodes_from(list(to_remove))
        elapsed_ms = (time.perf_counter() - t0) * 1000

        snap["deleted_node_id"] = node_id
        snap["deleted_label"] = target_label
        snap["deleted_kind"] = target_kind
        snap["deleted_ids"] = list(to_remove)
        snap["deleted_details"] = removed_nodes_info
        snap["edges_removed"] = len(edges_removed_list)
        snap["edges_removed_list"] = edges_removed_list
        snap["delete_elapsed_ms"] = round(elapsed_ms, 3)
        snap["time_complexity"] = "O(V + E)"
        snap["time_complexity_details"] = "O(V + E) NetworkX Graph Traversal"

        self.undo_stack.append(snap)
        self.history.append(node_id)

        return {
            "deleted_node_id": node_id,
            "deleted_label": target_label,
            "deleted_kind": target_kind,
            "deleted": list(to_remove),
            "deleted_details": removed_nodes_info,
            "edges_removed": len(edges_removed_list),
            "edges_removed_list": edges_removed_list,
            "elapsed_ms": round(elapsed_ms, 3),
            "time_complexity": "O(V + E)",
            "time_complexity_details": snap["time_complexity_details"],
            "graph": graph_to_json(self.graph),
        }

    def undo(self) -> dict[str, Any] | None:
        """Undo the last deletion by restoring the previous snapshot."""
        if not self.undo_stack:
            return None

        snap = self.undo_stack.pop()
        if self.history:
            self.history.pop()

        t0 = time.perf_counter()
        restore_graph(self.graph, snap)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        return {
            "graph": graph_to_json(self.graph),
            "restored_node_id": snap.get("deleted_node_id"),
            "restored_label": snap.get("deleted_label"),
            "restored_kind": snap.get("deleted_kind"),
            "deleted_details": snap.get("deleted_details", []),
            "edges_removed": snap.get("edges_removed", 0),
            "delete_elapsed_ms": snap.get("delete_elapsed_ms", 0.0),
            "time_complexity": snap.get("time_complexity", "O(V + E)"),
            "time_complexity_details": snap.get(
                "time_complexity_details", "O(V + E) NetworkX Graph Traversal"
            ),
            "undo_elapsed_ms": round(elapsed_ms, 3),
        }

    def reset(self) -> dict[str, Any]:
        """Reset graph to canonical baseline dataset."""
        self.rebuild_from_history([])
        return {
            "graph": graph_to_json(self.graph),
            "node_count": self.graph.number_of_nodes(),
        }

    def rebuild_from_history(self, history: list[str]) -> None:
        """Replay deletion history onto a fresh baseline graph."""
        fresh = build_graph(self.raw_data)
        self.graph.clear()
        self.graph.add_nodes_from(fresh.nodes(data=True))
        self.graph.add_edges_from(fresh.edges(data=True))
        self.undo_stack.clear()
        self.history.clear()

        for node_id in history:
            if node_id in self.graph:
                self.apply_delete(node_id)

    def sync_state_from_cookie(self, cookie_val: str | None = None) -> None:
        """Synchronize in-memory graph state from HTTP cookie."""
        if not cookie_val:
            return
        try:
            wanted = json.loads(cookie_val)
            if not isinstance(wanted, list):
                return
            with _STATE_LOCK:
                if wanted != self.history:
                    self.rebuild_from_history(wanted)
        except Exception:
            pass

    def persist_state_cookie(self, response: Any) -> Any:
        """Persist current deletion history into cookie for serverless/session safety."""
        with _STATE_LOCK:
            if self.history:
                response.set_cookie(
                    STATE_COOKIE,
                    json.dumps(self.history, separators=(",", ":")),
                    path="/",
                    samesite="Lax",
                    max_age=86400,
                )
            else:
                response.delete_cookie(STATE_COOKIE, path="/")
        return response


# Module-level singletons for direct imports across routes and tests
service_instance = GraphService()
GRAPH = service_instance.graph
UNDO_STACK = service_instance.undo_stack
HISTORY = service_instance.history
RAW = service_instance.raw_data

_apply_delete = service_instance.apply_delete
_rebuild_from_history = service_instance.rebuild_from_history
_sync_state_from_cookie = service_instance.sync_state_from_cookie
_persist_state_cookie = service_instance.persist_state_cookie
