from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes.benchmarks import router as benchmarks_router
from backend.app.api.routes.graph import router as graph_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.traversal import router as traversal_router
from backend.app.api.routes.validation import router as validation_router

api_router = APIRouter(prefix="/api")
api_bp = api_router

# Register sub-routers onto api_router
api_router.include_router(graph_router, tags=["Graph"])
api_router.include_router(traversal_router, tags=["Traversal"])
api_router.include_router(validation_router, tags=["Validation"])
api_router.include_router(benchmarks_router, tags=["Benchmarks"])
api_router.include_router(health_router, tags=["Health"])

__all__ = ["api_router"]
