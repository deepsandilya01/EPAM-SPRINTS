from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.app.services.graph_service import service_instance

router = APIRouter()
graph_bp = router
graph_service = service_instance


@router.get("/graph")
def api_graph():
    """Return active graph structure formatted for UI visualization."""
    return graph_service.get_graph_json()


@router.delete("/node/{node_id}")
def api_delete_node(node_id: str):
    """
    Simulate supplier disruption or component deletion.
    Cascades removal to all downstream dependent parts, assemblies, and customer orders.
    """
    graph = graph_service.get_graph()
    if node_id not in graph:
        return JSONResponse(status_code=404, content={"error": f"Node '{node_id}' not found"})

    result = graph_service.apply_delete(node_id)
    return result


@router.post("/undo")
def api_undo():
    """Undo the last deletion by restoring the previous graph snapshot."""
    restored = graph_service.undo()
    if restored is None:
        return JSONResponse(status_code=400, content={"error": "Nothing to undo"})

    return restored


@router.post("/reset")
def api_reset():
    """Reset graph to the canonical baseline dataset."""
    result = graph_service.reset()
    return result
