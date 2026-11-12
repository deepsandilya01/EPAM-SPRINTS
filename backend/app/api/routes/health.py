from __future__ import annotations

from fastapi import APIRouter

from backend.app.services.graph_service import service_instance

router = APIRouter()
health_bp = router


@router.get("/health")
def api_health():
    """Return service health status and active graph counts."""
    graph = service_instance.get_graph()
    return {
        "status": "healthy",
        "service": "RE:Flow — Supply Chain Graph",
        "version": "1.0.0",
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
    }
