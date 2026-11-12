from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from backend.app.schemas.traversal import TraversalRequestSchema
from backend.app.services.graph_service import service_instance

router = APIRouter()
traversal_bp = router
graph_service = service_instance


@router.get("/downstream/{node_id}")
def api_downstream(node_id: str):
    """Return all downstream reachable node IDs from starting node using BFS."""
    result = graph_service.get_downstream_reachability(node_id)
    if result is None:
        return JSONResponse(status_code=404, content={"error": f"Node '{node_id}' not found"})
    return result


@router.get("/impact/{node_id}")
def api_impact(node_id: str):
    """Return cascading blast radius impact details for node_id."""
    result = graph_service.get_downstream_impact(node_id)
    if result is None:
        return JSONResponse(status_code=404, content={"error": f"Node '{node_id}' not found"})
    return result


@router.post("/traversal")
def api_traversal(payload: Dict[str, Any] = Body(default_factory=dict)):
    """Execute downstream reachability trace from POST payload."""
    node_id = payload.get("node_id", payload.get("start_node_id", ""))
    if not node_id:
        return JSONResponse(status_code=400, content={"error": "node_id or start_node_id is required"})

    try:
        req_schema = TraversalRequestSchema(node_id=str(node_id))
        node_id = req_schema.node_id
    except Exception:
        pass

    result = graph_service.get_downstream_reachability(node_id)
    if result is None:
        return JSONResponse(status_code=404, content={"error": f"Node '{node_id}' not found"})
    return result
