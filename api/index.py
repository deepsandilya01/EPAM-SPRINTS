"""
Vercel Serverless Function entry point for Team Photon Supply-Chain Intelligence.
Exposes the WSGI Flask application to Vercel's Python runtime.
"""

from __future__ import annotations

import logging
import pathlib
import sys
import traceback

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from backend.app import app  # noqa: E402
except Exception as e:
    logging.exception("Failed to import backend.app: %s", e)
    from flask import Flask, jsonify

    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return (
            jsonify(
                {
                    "error": "Backend initialization failed",
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )

# Vercel's serverless Python runtime automatically discovers the 'app' WSGI callable
__all__ = ["app"]
