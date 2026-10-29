"""
Vercel serverless entry point — re-exports the Flask application from backend.app.

Vercel's framework detector scans this file for a module-level ``app`` variable.
The [tool.vercel] section in pyproject.toml sets the authoritative entrypoint to
``backend.app:app``, but this shim satisfies both the detector and existing tests
that import ``from api.index import app``.
"""

from __future__ import annotations

import pathlib
import sys

# Ensure repo root is on sys.path so ``backend`` package is importable.
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Also add backend/ so its internal relative imports (graph_validation) resolve.
_BACKEND_DIR = _REPO_ROOT / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Module-level re-export: Vercel's AST scanner requires ``app`` to be a
# bare top-level name, not buried inside a try/except block.
from backend.app import app  # noqa: E402

__all__ = ["app"]
