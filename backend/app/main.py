from __future__ import annotations

import os
import pathlib
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.api import api_router  # noqa: E402
from backend.app.services.graph_service import (  # noqa: E402
    STATE_COOKIE,
    service_instance,
)

# Sprint 2: Eagerly initialize the simulation service so the
# /api/disruptions endpoints are ready on first request.
from backend.app.services.simulation_service import simulation_service  # noqa: E402, F401

# Initialize FastAPI application
app = FastAPI(
    title="RE:Flow — Team PHOTON Decision Intelligence",
    description="Multi-Tier Supply Chain Graph & Disruption Simulation Engine",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware — explicit origins for development and configured production hosts
_default_dev_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_cors_env = os.getenv("CORS_ORIGINS", "")
_configured_origins = [o.strip().rstrip("/") for o in _cors_env.split(",") if o.strip()]
_frontend_host = os.getenv("FRONTEND_HOST", "").strip().rstrip("/")
if _frontend_host:
    if not _frontend_host.startswith(("http://", "https://")):
        _frontend_host = f"https://{_frontend_host}"
    if _frontend_host not in _configured_origins:
        _configured_origins.append(_frontend_host)

_is_production = os.getenv("ENVIRONMENT", os.getenv("FLASK_ENV", "development")).lower() == "production"
_allowed_origins = _configured_origins if _configured_origins else ([] if _is_production else _default_dev_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


@app.middleware("http")
async def cookie_state_middleware(request: Request, call_next):
    """Synchronize graph state from client cookie and persist updates in response."""
    cookie_val = request.cookies.get(STATE_COOKIE)
    if cookie_val:
        service_instance.sync_state_from_cookie(cookie_val)

    response = await call_next(request)
    service_instance.persist_state_cookie(response)
    return response


# Include unified API router (endpoints prefixed with /api)
app.include_router(api_router)


@app.get("/")
def index():
    """Return RE:Flow API service metadata (frontend is decoupled in frontend/)."""
    return {
        "status": "online",
        "service": "RE:Flow — Team PHOTON Decision Intelligence",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/health")
def root_health():
    """Direct root health check probe for cloud deployments (Render, Vercel, AWS)."""
    graph = service_instance.get_graph()
    return {
        "status": "healthy",
        "service": "RE:Flow — Supply Chain Graph",
        "framework": "FastAPI",
        "version": "2.0.0",
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
    }


# --- Production JSON Exception Handlers ---


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"error": "Resource not found", "status": 404},
        )

    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={"error": "Method not allowed", "status": 405},
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail or "Internal error", "status": exc.status_code},
    )


def create_app() -> FastAPI:
    """Application factory for ASGI servers and pytest fixtures."""
    return app


# Backwards compatibility helper for tests expecting app.test_client()
def _test_client():
    from fastapi.testclient import TestClient

    class _Wrapper:
        def __init__(self, client):
            self._client = client

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, *a, **kw):
            from tests.conftest import FastAPITestResponseWrapper

            return FastAPITestResponseWrapper(self._client.get(*a, **kw))

        def post(self, *a, **kw):
            from tests.conftest import FastAPITestResponseWrapper

            return FastAPITestResponseWrapper(self._client.post(*a, **kw))

        def delete(self, *a, **kw):
            from tests.conftest import FastAPITestResponseWrapper

            return FastAPITestResponseWrapper(self._client.delete(*a, **kw))

    client = TestClient(app)
    return _Wrapper(client)


app.test_client = _test_client


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 5001))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=not _is_production)
