"""
Project: RE:Flow
Sprint: 1
File: backend/app/api/routes/validation.py

Primary Owner: Soumya
Role: Graph and Data Validation

Purpose:
Graph structural integrity and schema validation route definitions.

Responsibilities:
- Implement GET /api/validation endpoint.
- Invoke ValidationService to execute full validation suite.
- Return 200 OK with comprehensive validation report payload.

Dependencies:
- Soumya: Validation service (backend/app/services/validation_service.py).
- Validation schemas in backend/app/schemas/validation.py (Implemented by Deep; Team Maintained).

Deliverables:
- Working GET /api/validation endpoint returning structured audit report.

Status: COMPLETED
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.app.schemas.validation import ValidationRequestSchema
from backend.app.services.validation_service import ValidationService

validation_bp = Blueprint("validation", __name__)
validation_service = ValidationService()


@validation_bp.route("/validation", methods=["GET"])
def api_validation():
    """
    Validate current graph structure.
    Query params:
      - mode: 'baseline' (expects original 19 nodes) or 'integrity' (validates structure after mutations).
      - strict: 'true' to return 422 on failure instead of 200 with report.
    """
    req_mode = request.args.get("mode")
    strict = request.args.get("strict", "false").lower() == "true"

    try:
        if req_mode:
            ValidationRequestSchema(mode=req_mode, strict=strict)
    except Exception:
        pass

    result, status_code = validation_service.validate_graph(mode_param=req_mode, strict=strict)
    return jsonify(result), status_code
