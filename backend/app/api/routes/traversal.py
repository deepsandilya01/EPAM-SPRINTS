from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.app.schemas.traversal import TraversalRequestSchema
from backend.app.services.traversal_service import TraversalService

traversal_bp = Blueprint("traversal", __name__)
traversal_service = TraversalService()


@traversal_bp.route("/downstream/<node_id>", methods=["GET"])
def api_downstream(node_id: str):
    """Return all downstream reachable node IDs from starting node using BFS."""
    result = traversal_service.get_downstream_reachability(node_id)
    if result is None:
        return jsonify({"error": f"Node '{node_id}' not found"}), 404
    return jsonify(result)


@traversal_bp.route("/impact/<node_id>", methods=["GET"])
def api_impact(node_id: str):
    """Return cascading blast radius impact details for node_id."""
    result = traversal_service.get_downstream_impact(node_id)
    if result is None:
        return jsonify({"error": f"Node '{node_id}' not found"}), 404
    return jsonify(result)


@traversal_bp.route("/traversal", methods=["POST"])
def api_traversal():
    """Execute downstream reachability trace from POST payload."""
    payload = request.get_json(silent=True) or {}
    node_id = payload.get("node_id", payload.get("start_node_id", ""))
    if not node_id:
        return jsonify({"error": "node_id or start_node_id is required"}), 400

    try:
        req_schema = TraversalRequestSchema(node_id=str(node_id))
        node_id = req_schema.node_id
    except Exception:
        pass

    result = traversal_service.get_downstream_reachability(node_id)
    if result is None:
        return jsonify({"error": f"Node '{node_id}' not found"}), 404
    return jsonify(result)
