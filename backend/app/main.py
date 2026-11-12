from __future__ import annotations

import os
import pathlib
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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

# Initialize FastAPI application
app = FastAPI(
    title="RE:Flow — Team PHOTON Decision Intelligence",
    description="Multi-Tier Supply Chain Graph & Disruption Simulation Engine",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Mount static folder
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def index():
    """Serve the interactive supply chain dependency graph visualization demo."""
    demo_file = static_dir / "sprint-1-demo.html"
    return FileResponse(demo_file)


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
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=404,
                content={"error": "Resource not found", "status": 404},
            )
        demo_file = static_dir / "sprint-1-demo.html"
        if demo_file.exists():
            return FileResponse(demo_file, status_code=404)
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
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=True)
