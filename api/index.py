
"""
Vercel serverless entry point.
Re-exports the Flask application from backend.app.
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

__all__ = ["app"]
