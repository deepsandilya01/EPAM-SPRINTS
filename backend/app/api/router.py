from __future__ import annotations

from flask import Blueprint

from backend.app.api.routes.benchmarks import benchmarks_bp
from backend.app.api.routes.graph import graph_bp
from backend.app.api.routes.health import health_bp
from backend.app.api.routes.traversal import traversal_bp
from backend.app.api.routes.validation import validation_bp
from backend.app.services.graph_service import (
    _persist_state_cookie,
    _sync_state_from_cookie,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Register sub-blueprints directly on api_bp
api_bp.register_blueprint(graph_bp)
api_bp.register_blueprint(traversal_bp)
api_bp.register_blueprint(validation_bp)
api_bp.register_blueprint(benchmarks_bp)
api_bp.register_blueprint(health_bp)


@api_bp.before_request
def sync_client_state():
    """Synchronize in-memory graph state from cookie history before handling API request."""
    _sync_state_from_cookie()


@api_bp.after_request
def persist_client_state(response):
    """Persist updated graph history into client cookie."""
    return _persist_state_cookie(response)
