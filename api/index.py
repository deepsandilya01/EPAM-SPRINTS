"""
Vercel serverless entry point.
Re-exports the Flask application from backend.app with Vercel path fixing middleware.
"""

from __future__ import annotations

import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_BACKEND_DIR = _REPO_ROOT / "backend"

for directory in (_REPO_ROOT, _BACKEND_DIR):
    directory_str = str(directory)
    if directory_str not in sys.path:
        sys.path.insert(0, directory_str)

from backend.app import app  # noqa: E402


class _VercelPathFixer:
    """WSGI middleware ensuring proper routing when Vercel rewrites to /api/index."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched = environ.get("HTTP_X_MATCHED_PATH") or environ.get("HTTP_X_FORWARDED_URI")
        if matched and matched not in ("/api/index", "/api/index.py"):
            environ["PATH_INFO"] = matched
        elif environ.get("PATH_INFO") in ("/api/index", "/api/index.py"):
            environ["PATH_INFO"] = "/"
        return self.wsgi_app(environ, start_response)


if not isinstance(app.wsgi_app, _VercelPathFixer):
    app.wsgi_app = _VercelPathFixer(app.wsgi_app)

__all__ = ["app"]
