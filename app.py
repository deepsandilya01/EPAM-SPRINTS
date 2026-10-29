"""
Root application entrypoint for Team Photon Supply-Chain Intelligence.
Enables zero-configuration deployment on Vercel (Flask Framework Preset),
Render, Railway, Fly.io, and local WSGI servers.
"""

from __future__ import annotations

import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parent
_BACKEND_DIR = _REPO_ROOT / "backend"

for _directory in (_REPO_ROOT, _BACKEND_DIR):
    _dir_str = str(_directory)
    if _dir_str not in sys.path:
        sys.path.insert(0, _dir_str)

from backend.app import (  # noqa: E402
    GRAPH,
    RAW,
    UNDO_STACK,
    app,
)

__all__ = ["GRAPH", "RAW", "UNDO_STACK", "app"]

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
