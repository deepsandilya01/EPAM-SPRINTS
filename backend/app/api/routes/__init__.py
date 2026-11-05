from __future__ import annotations

from backend.app.api.routes.benchmarks import router as benchmarks_router
from backend.app.api.routes.graph import router as graph_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.traversal import router as traversal_router
from backend.app.api.routes.validation import router as validation_router

# Compatibility aliases
benchmarks_bp = benchmarks_router
graph_bp = graph_router
health_bp = health_router
traversal_bp = traversal_router
validation_bp = validation_router

__all__ = [
    "graph_router",
    "traversal_router",
    "validation_router",
    "benchmarks_router",
    "health_router",
    "graph_bp",
    "traversal_bp",
    "validation_bp",
    "benchmarks_bp",
    "health_bp",
]
