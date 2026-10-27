"""
Supply-Chain Graph Server
─────────────────────────
Uses **NetworkX** to build and manipulate the directed acyclic graph
(Suppliers → Parts → Products → Orders) and exposes it over a tiny
Flask API that the D3.js front-end consumes.

Endpoints
─────────
GET  /                → serves the interactive HTML page
GET  /api/graph       → full graph as {nodes, edges}
GET  /api/downstream/<node_id> → downstream trace from a node
DELETE /api/node/<node_id>     → remove node + downstream cascade
POST /api/undo                 → undo the last delete
"""

import json, copy, pathlib, time
from flask import Flask, jsonify, request, send_from_directory

import networkx as nx

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "photon_sprint1_graph_data.json"

# ──────────────────────────────────────────────
# Flask app
# ──────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="/static")

# ──────────────────────────────────────────────
# Graph helpers
# ──────────────────────────────────────────────

def _load_raw_data() -> dict:
    """Load the original JSON once."""
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

RAW = _load_raw_data()


def _build_graph(raw: dict) -> nx.DiGraph:
    """Build a NetworkX DiGraph from the raw JSON data."""
    G = nx.DiGraph()

    # --- nodes --------------------------------------------------------
    for category in ("suppliers", "parts", "products", "orders"):
        for node in raw["nodes"][category]:
            G.add_node(node["id"], **node)

    # --- edges --------------------------------------------------------
    for edge_type in ("supplies", "used_in", "fulfills"):
        for edge in raw["edges"][edge_type]:
            G.add_edge(
                edge["source"],
                edge["target"],
                relation=edge["relation"],
                **{k: v for k, v in edge.items() if k not in ("source", "target", "relation")},
            )
    return G


# The "live" graph the API operates on + an undo stack
GRAPH: nx.DiGraph = _build_graph(RAW)
UNDO_STACK: list[dict] = []          # snapshots of (nodes_data, edges_data)


def _graph_to_json(G: nx.DiGraph) -> dict:
    """Serialise the current graph into D3-friendly JSON."""
    nodes = []
    for nid, attrs in G.nodes(data=True):
        nodes.append({**attrs, "id": nid})

    edges = []
    for src, tgt, attrs in G.edges(data=True):
        edges.append({"source": src, "target": tgt, **attrs})

    return {"nodes": nodes, "edges": edges}


def _downstream(G: nx.DiGraph, start: str) -> set[str]:
    """Return all nodes reachable downstream from *start* (BFS)."""
    if start not in G:
        return set()
    return set(nx.descendants(G, start))


def _snapshot() -> dict:
    """Deep-copy the current graph data for undo."""
    return {
        "nodes": {n: copy.deepcopy(d) for n, d in GRAPH.nodes(data=True)},
        "edges": [(u, v, copy.deepcopy(d)) for u, v, d in GRAPH.edges(data=True)],
    }


def _restore(snap: dict):
    """Restore the graph from a snapshot."""
    GRAPH.clear()
    for nid, attrs in snap["nodes"].items():
        GRAPH.add_node(nid, **attrs)
    for u, v, attrs in snap["edges"]:
        GRAPH.add_edge(u, v, **attrs)


# ──────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(BASE_DIR / "static", "index.html")


@app.route("/api/graph")
def api_graph():
    return jsonify(_graph_to_json(GRAPH))


@app.route("/api/downstream/<node_id>")
def api_downstream(node_id: str):
    """Return the downstream node-ids from a given starting node."""
    reachable = _downstream(GRAPH, node_id)
    return jsonify({"root": node_id, "downstream": list(reachable)})


@app.route("/api/impact/<node_id>")
def api_impact(node_id: str):
    """Return impact preview if node_id were to be deleted."""
    if node_id not in GRAPH:
        return jsonify({"error": f"Node {node_id} not found"}), 404

    node_attrs = dict(GRAPH.nodes[node_id])
    
    # Direct outgoing & incoming edges
    outgoing_edges = [
        {"source": u, "target": v, "relation": d.get("relation", "")}
        for u, v, d in GRAPH.out_edges(node_id, data=True)
    ]
    incoming_edges = [
        {"source": u, "target": v, "relation": d.get("relation", "")}
        for u, v, d in GRAPH.in_edges(node_id, data=True)
    ]

    # Downstream cascade
    downstream_nodes = _downstream(GRAPH, node_id)
    all_affected_nodes = downstream_nodes | {node_id}

    affected_nodes_info = []
    for nid in sorted(all_affected_nodes):
        attrs = dict(GRAPH.nodes[nid])
        affected_nodes_info.append({
            "id": nid,
            "kind": attrs.get("kind", ""),
            "label": attrs.get("label", nid)
        })

    # All edges that would be removed
    edges_to_remove = []
    for u, v, attrs in GRAPH.edges(data=True):
        if u in all_affected_nodes or v in all_affected_nodes:
            edges_to_remove.append({
                "source": u,
                "target": v,
                "relation": attrs.get("relation", "")
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
        "time_complexity_explanation": f"Traversal & cascade removal visits {len(all_affected_nodes)} vertices and inspects {len(edges_to_remove)} edges in O(V + E) time."
    })


@app.route("/api/node/<node_id>", methods=["DELETE"])
def api_delete_node(node_id: str):
    """
    Delete a node and consecutive connected edges / downstream cascade.
    Pushes snapshot onto UNDO_STACK with timing and complexity metrics.
    """
    if node_id not in GRAPH:
        return jsonify({"error": f"Node {node_id} not found"}), 404

    target_attrs = dict(GRAPH.nodes[node_id])
    target_label = target_attrs.get("label", node_id)
    target_kind = target_attrs.get("kind", "")

    t0 = time.perf_counter()

    snap = _snapshot()

    # Collect info BEFORE removal
    to_remove = _downstream(GRAPH, node_id) | {node_id}
    removed_nodes_info = []
    for nid in sorted(to_remove):
        attrs = dict(GRAPH.nodes[nid])
        removed_nodes_info.append({"id": nid, "kind": attrs.get("kind", ""), "label": attrs.get("label", nid)})

    # Connected consecutive edges removed
    edges_removed_list = []
    for u, v, attrs in list(GRAPH.edges(data=True)):
        if u in to_remove or v in to_remove:
            edges_removed_list.append({"source": u, "target": v, "relation": attrs.get("relation", "")})

    GRAPH.remove_nodes_from(list(to_remove))

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Enrich snapshot with delete metadata for undo
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
    """Pop the most recent snapshot and restore."""
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
    """Reset graph to original state and clear undo history."""
    global GRAPH
    UNDO_STACK.clear()
    GRAPH = _build_graph(RAW)
    return jsonify({"graph": _graph_to_json(GRAPH), "node_count": GRAPH.number_of_nodes()})


# ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
