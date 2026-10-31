from __future__ import annotations

import os
import pathlib

from flask import Flask, jsonify, request, send_from_directory

from backend.app.api.router import api_bp

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent

# Initialize Flask application
app = Flask(__name__, static_folder=str(BASE_DIR / "static"), static_url_path="/static")

# Register unified API blueprint
app.register_blueprint(api_bp)


@app.route("/")
def index():
    """Serve the interactive supply chain dependency graph visualization demo."""
    static_dir = BASE_DIR / "static"
    return send_from_directory(static_dir, "sprint-1-demo.html")


# --- Production JSON Error Handlers ---


@app.errorhandler(404)
def handle_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    static_dir = BASE_DIR / "static"
    demo_file = static_dir / "sprint-1-demo.html"
    if demo_file.exists():
        return send_from_directory(static_dir, "sprint-1-demo.html"), 404
    return jsonify({"error": "Resource not found", "status": 404}), 404


@app.errorhandler(405)
def handle_method_not_allowed(e):
    return jsonify({"error": "Method not allowed", "status": 405}), 405


@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500


def create_app() -> Flask:
    """Application factory for WSGI servers and pytest fixtures."""
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
