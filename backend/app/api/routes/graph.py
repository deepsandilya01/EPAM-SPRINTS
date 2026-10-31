from __future__ import annotations

from flask import Blueprint, jsonify

from backend.app.services.graph_service import service_instance

graph_bp = Blueprint("graph", __name__)
graph_service = service_instance


@graph_bp.route("/graph", methods=["GET"])
def api_graph():
    """Return active graph structure formatted for UI visualization."""
    return jsonify(graph_service.get_graph_json())


@graph_bp.route("/node/<node_id>", methods=["DELETE"])
def api_delete_node(node_id: str):
    """
    Simulate supplier disruption or component deletion.
    Cascades removal to all downstream dependent parts, assemblies, and customer orders.
    """
    graph = graph_service.get_graph()
    if node_id not in graph:
        return jsonify({"error": f"Node '{node_id}' not found"}), 404

    result = graph_service.apply_delete(node_id)
    return jsonify(result)


@graph_bp.route("/undo", methods=["POST"])
def api_undo():
    """Undo the last deletion by restoring the previous graph snapshot."""
    restored = graph_service.undo()
    if restored is None:
        return jsonify({"error": "Nothing to undo"}), 400

    return jsonify(restored)


@graph_bp.route("/reset", methods=["POST"])
def api_reset():
    """Reset graph to the canonical baseline dataset."""
    result = graph_service.reset()
    return jsonify(result)
