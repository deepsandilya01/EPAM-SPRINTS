from __future__ import annotations

from flask import Blueprint, jsonify

from backend.app.services.graph_service import service_instance

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def api_health():
    """Return service health status and active graph counts."""
    graph = service_instance.get_graph()
    return jsonify({
        "status": "healthy",
        "service": "RE:Flow — Supply Chain Graph",
        "version": "1.0.0",
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
    }), 200
