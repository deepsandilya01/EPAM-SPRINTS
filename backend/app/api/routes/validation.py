from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.app.schemas.validation import ValidationRequestSchema
from backend.app.services.validation_service import ValidationService

router = APIRouter()
validation_bp = router
validation_service = ValidationService()


@router.get("/validation")
def api_validation(
    mode: Optional[str] = Query(None),
    strict: str = Query("false"),
):
    """
    Validate current graph structure.
    Query params:
      - mode: 'baseline' (expects original 19 nodes) or 'integrity' (validates structure after mutations).
      - strict: 'true' to return 422 on failure instead of 200 with report.
    """
    is_strict = strict.lower() == "true"

    try:
        if mode:
            ValidationRequestSchema(mode=mode, strict=is_strict)
    except Exception:
        pass

    result, status_code = validation_service.validate_graph(mode_param=mode, strict=is_strict)
    return JSONResponse(status_code=status_code, content=result)
