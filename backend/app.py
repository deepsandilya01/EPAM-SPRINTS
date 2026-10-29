"""
Supply chain dependency graph server.
Exposes REST endpoints to query the 4-tier network (Suppliers -> Parts -> Products -> Orders),
simulate downstream disruptions, and validate graph integrity.
"""

from __future__ import annotations

import copy
import json
import os
import pathlib
import sys
import time

import networkx as nx
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from graph_validation import (  # noqa: E402
    AcyclicityPolicy,
    ValidationPolicy,
    trace_downstream_with_metrics,
    validate_networkx_graph,
    validate_raw_graph_data,
)

DATA_FILE = BASE_DIR / "data" / "photon_sprint1_graph_data.json"
if not DATA_FILE.exists():
    for _candidate in (
        REPO_ROOT / "data" / "photon_sprint1_graph_data.json",
        pathlib.Path("backend/data") / "photon_sprint1_graph_data.json",
        pathlib.Path("data") / "photon_sprint1_graph_data.json",
        BASE_DIR / "photon_sprint1_graph_data.json",
    ):
        if _candidate.exists():
            DATA_FILE = _candidate
            break

app = Flask(__name__, static_folder="static", static_url_path="/static")


def _load_raw_data() -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


RAW = _load_raw_data()

# Validate the JSON data at startup before building the graph
_startup_report = validate_raw_graph_data(RAW)
if not _startup_report.valid:
    print(
        f"[VALIDATION WARNING] Baseline graph validation failed on startup: {len(_startup_report.errors)} errors.",
        file=sys.stderr,
    )


def _build_graph(raw: dict) -> nx.DiGraph:
    """Build the directed graph from raw JSON data."""
    G = nx.DiGraph()

    for category in ("suppliers", "parts", "products", "orders"):
        for node in raw["nodes"][category]:
            G.add_node(node["id"], **node)

    for edge_type in ("supplies", "used_in", "fulfills"):
        for edge in raw["edges"][edge_type]:
            G.add_edge(
                edge["source"],
                edge["target"],
                relation=edge["relation"],
                **{k: v for k, v in edge.items() if k not in ("source", "target", "relation")},
            )
    return G


# In-memory graph and snapshot history for undo
GRAPH: nx.DiGraph = _build_graph(RAW)
UNDO_STACK: list[dict] = []


def _graph_to_json(G: nx.DiGraph) -> dict:
    """Format graph into nodes and edges lists for the UI."""
    nodes = [{**attrs, "id": nid} for nid, attrs in G.nodes(data=True)]
    edges = [{"source": src, "target": tgt, **attrs} for src, tgt, attrs in G.edges(data=True)]
    return {"nodes": nodes, "edges": edges}


def _downstream(G: nx.DiGraph, start: str) -> set[str]:
    """Find all reachable nodes downstream using BFS traversal."""
    if start not in G:
        return set()
    return set(nx.descendants(G, start))


def _snapshot() -> dict:
    """Take a deep copy of current graph state before a mutation."""
    return {
        "nodes": {n: copy.deepcopy(d) for n, d in GRAPH.nodes(data=True)},
        "edges": [(u, v, copy.deepcopy(d)) for u, v, d in GRAPH.edges(data=True)],
    }


def _restore(snap: dict):
    """Restore nodes and edges from a previous snapshot."""
    GRAPH.clear()
    for nid, attrs in snap["nodes"].items():
        GRAPH.add_node(nid, **attrs)
    for u, v, attrs in snap["edges"]:
        GRAPH.add_edge(u, v, **attrs)


# --- REST Routes ---

@app.route("/")
def index():
    return send_from_directory(BASE_DIR / "static", "index.html")


@app.route("/api/graph")
def api_graph():
    return jsonify(_graph_to_json(GRAPH))


@app.route("/api/downstream/<node_id>")
def api_downstream(node_id: str):
    """Get all descendant node IDs starting from node_id."""
    if node_id not in GRAPH:
        return jsonify({"error": f"Node {node_id} not found"}), 404
    reachable = _downstream(GRAPH, node_id)
    return jsonify({"root": node_id, "downstream": list(reachable)})


@app.route("/api/impact/<node_id>")
def api_impact(node_id: str):
    """Preview the ripple effect (affected nodes & edges) if node_id is removed."""
    if node_id not in GRAPH:
        return jsonify({"error": f"Node {node_id} not found"}), 404

    node_attrs = dict(GRAPH.nodes[node_id])

    outgoing_edges = [
        {"source": u, "target": v, "relation": d.get("relation", "")}
        for u, v, d in GRAPH.out_edges(node_id, data=True)
    ]
    incoming_edges = [
        {"source": u, "target": v, "relation": d.get("relation", "")}
        for u, v, d in GRAPH.in_edges(node_id, data=True)
    ]

    downstream_nodes = _downstream(GRAPH, node_id)
    all_affected_nodes = downstream_nodes | {node_id}

    affected_nodes_info = []
    for nid in sorted(all_affected_nodes):
        attrs = dict(GRAPH.nodes[nid])
        affected_nodes_info.append({
            "id": nid,
            "kind": attrs.get("kind", ""),
            "label": attrs.get("label", nid),
        })

    edges_to_remove = []
    for u, v, attrs in GRAPH.edges(data=True):
        if u in all_affected_nodes or v in all_affected_nodes:
            edges_to_remove.append({
                "source": u,
                "target": v,
                "relation": attrs.get("relation", ""),
            })

    return jsonify({
        "node": {"id": node_id, **node_attrs},
        "outgoing_edges": outgoing_edges,
        "incoming_edges": incoming_edges,
        "downstream_nodes": list(downstream_nodes),
        "affected_nodes_details": affected_nodes_info,
        "edges_to_remove": edges_to_remove,
        "total_nodes_affected": len(all_affected_nodes),
        "total_edges_affected": len(edges_to_remove),
        "time_complexity": "O(V + E)",
        "time_complexity_explanation": f"Traversal & cascade removal visits {len(all_affected_nodes)} vertices and inspects {len(edges_to_remove)} edges in O(V + E) time.",
    })


@app.route("/api/node/<node_id>", methods=["DELETE"])
def api_delete_node(node_id: str):
    """Delete a node and its downstream cascade, saving an undo snapshot."""
    if node_id not in GRAPH:
        return jsonify({"error": f"Node {node_id} not found"}), 404

    target_attrs = dict(GRAPH.nodes[node_id])
    target_label = target_attrs.get("label", node_id)
    target_kind = target_attrs.get("kind", "")

    t0 = time.perf_counter()
    snap = _snapshot()

    # Determine cascade impact before modifying the graph
    to_remove = _downstream(GRAPH, node_id) | {node_id}
    removed_nodes_info = []
    for nid in sorted(to_remove):
        attrs = dict(GRAPH.nodes[nid])
        removed_nodes_info.append({"id": nid, "kind": attrs.get("kind", ""), "label": attrs.get("label", nid)})

    edges_removed_list = []
    for u, v, attrs in list(GRAPH.edges(data=True)):
        if u in to_remove or v in to_remove:
            edges_removed_list.append({"source": u, "target": v, "relation": attrs.get("relation", "")})

    GRAPH.remove_nodes_from(list(to_remove))

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Save metadata with snapshot so the UI can display undo timing & details
    snap["deleted_node_id"] = node_id
    snap["deleted_label"] = target_label
    snap["deleted_kind"] = target_kind
    snap["deleted_details"] = removed_nodes_info
    snap["edges_removed"] = len(edges_removed_list)
    snap["edges_removed_list"] = edges_removed_list
    snap["delete_elapsed_ms"] = round(elapsed_ms, 3)
    snap["time_complexity"] = "O(V + E)"
    snap["time_complexity_details"] = f"NetworkX BFS traversal & removal of {len(to_remove)} nodes and {len(edges_removed_list)} edges"

    UNDO_STACK.append(snap)

    return jsonify({
        "deleted_node_id": node_id,
        "deleted_label": target_label,
        "deleted_kind": target_kind,
        "deleted": list(to_remove),
        "deleted_details": removed_nodes_info,
        "edges_removed": len(edges_removed_list),
        "edges_removed_list": edges_removed_list,
        "elapsed_ms": round(elapsed_ms, 3),
        "time_complexity": "O(V + E)",
        "time_complexity_details": f"NetworkX BFS traversal & removal of {len(to_remove)} nodes and {len(edges_removed_list)} edges",
        "graph": _graph_to_json(GRAPH),
    })


@app.route("/api/undo", methods=["POST"])
def api_undo():
    """Undo the last deletion by restoring the previous graph snapshot."""
    if not UNDO_STACK:
        return jsonify({"error": "Nothing to undo"}), 400

    snap = UNDO_STACK.pop()

    t0 = time.perf_counter()
    _restore(snap)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return jsonify({
        "graph": _graph_to_json(GRAPH),
        "restored_node_id": snap.get("deleted_node_id"),
        "restored_label": snap.get("deleted_label"),
        "restored_kind": snap.get("deleted_kind"),
        "deleted_details": snap.get("deleted_details", []),
        "edges_removed": snap.get("edges_removed", 0),
        "delete_elapsed_ms": snap.get("delete_elapsed_ms", 0.0),
        "time_complexity": snap.get("time_complexity", "O(V + E)"),
        "time_complexity_details": snap.get("time_complexity_details", "O(V + E) NetworkX Graph Traversal"),
        "undo_elapsed_ms": round(elapsed_ms, 3),
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset graph to the canonical baseline dataset."""
    global GRAPH
    UNDO_STACK.clear()
    GRAPH = _build_graph(RAW)
    return jsonify({"graph": _graph_to_json(GRAPH), "node_count": GRAPH.number_of_nodes()})


@app.route("/api/validation", methods=["GET"])
def api_validation():
    """
    Validate current graph structure.
    Query params:
      - mode: 'baseline' (expects original 19 nodes) or 'integrity' (validates structure after mutations).
      - strict: 'true' to return 422 on failure instead of 200 with report.
    """
    req_mode = request.args.get("mode")
    strict = request.args.get("strict", "false").lower() == "true"

    if req_mode:
        mode_clean = req_mode.strip().lower()
        if mode_clean not in ("baseline", "integrity"):
            return jsonify({
                "error": f"Invalid mode '{req_mode}'. Allowed modes: baseline, integrity",
                "valid": False,
            }), 400
        is_baseline = mode_clean == "baseline"
        mode = "baseline" if is_baseline else "integrity"
    else:
        # Auto-detect: if canonical counts match, use baseline mode; otherwise integrity mode
        is_baseline = (GRAPH.number_of_nodes() == 19 and GRAPH.number_of_edges() == 21)
        mode = "baseline" if is_baseline else "integrity"

    policy = ValidationPolicy(
        check_baseline_counts=is_baseline,
        acyclicity_policy=AcyclicityPolicy.REQUIRE_DAG,
    )
    report = validate_networkx_graph(GRAPH, policy=policy)
    report.mode = mode

    status_code = 200
    if strict and not report.valid:
        status_code = 422

    return jsonify(report.to_dict()), status_code


@app.route("/api/benchmark/tracing", methods=["GET"])
def api_benchmark_tracing():
    """Benchmark downstream traversal speed for a node (default: SUP-01) against the 10ms SLA."""
    node_id = request.args.get("node_id", "SUP-01")
    threshold_param = request.args.get("threshold_ms", "10.0")
    try:
        threshold_ms = float(threshold_param)
        if threshold_ms <= 0:
            return jsonify({
                "error": "threshold_ms must be a positive number",
                "under_threshold": False,
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "error": f"Invalid threshold_ms value: '{threshold_param}'. Expected numeric value.",
            "under_threshold": False,
        }), 400

    metrics = trace_downstream_with_metrics(GRAPH, node_id, threshold_ms=threshold_ms)
    return jsonify(metrics)


# --- Production JSON Error Handlers ---

@app.errorhandler(404)
def handle_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    return send_from_directory(BASE_DIR / "static", "index.html"), 404


@app.errorhandler(405)
def handle_method_not_allowed(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Method not allowed", "status": 405}), 405
    return jsonify({"error": "Method not allowed", "status": 405}), 405


@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, port=port)
