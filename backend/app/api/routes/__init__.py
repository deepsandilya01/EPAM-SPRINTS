from __future__ import annotations

from backend.app.api.routes.benchmarks import benchmarks_bp
from backend.app.api.routes.graph import graph_bp
from backend.app.api.routes.health import health_bp
from backend.app.api.routes.traversal import traversal_bp
from backend.app.api.routes.validation import validation_bp

__all__ = [
    "graph_bp",
    "traversal_bp",
    "validation_bp",
    "benchmarks_bp",
    "health_bp",
]
