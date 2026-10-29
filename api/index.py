"""
Vercel Serverless Function entry point for Team Photon Supply-Chain Intelligence.
Exposes the WSGI Flask application to Vercel's Python runtime.
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app import app  # noqa: E402

# Vercel's serverless Python runtime automatically discovers the 'app' WSGI callable
__all__ = ["app"]
