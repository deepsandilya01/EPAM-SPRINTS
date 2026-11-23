"""
Project: RE:Flow
Sprint: 2
File: backend/app/schemas/disruption.py

Primary Owner: Preetam
Role: REST API Architect & OpenAPI Documentation Lead

Purpose:
Pydantic serialization schemas for disruption simulation requests and responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DisruptionRequest(BaseModel):
    """Request payload for triggering disruption simulation."""
    model_config = ConfigDict(populate_by_name=True)

    supplier_id: str = Field(
        default="SUP-01",
        description="Tier-1 Supplier identifier (e.g. 'SUP-01')",
        json_schema_extra={"example": "SUP-01"}
    )
    disruption_type: str = Field(
        default="SUPPLIER_DELAY",
        description="Category of disruption (e.g. 'SUPPLIER_DELAY')",
        json_schema_extra={"example": "SUPPLIER_DELAY"}
    )
    delay_duration_hours: float = Field(
        default=8.0,
        gt=0,
        description="Duration of supply delay in hours (must be > 0)",
        json_schema_extra={"example": 8.0}
    )
    description: str = Field(
        default="",
        description="Optional narrative describing disruption scenario",
        json_schema_extra={"example": "Benchmark test disruption"}
    )


class SimulationResponse(BaseModel):
    """Complete simulation response schema."""
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(default="success", description="Status string: 'success'")
    event: Dict[str, Any] = Field(description="DisruptionEvent details")
    impact: Dict[str, Any] = Field(description="RippleImpactSummary details")
    depletion_timeline: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Hourly stock timeline"
    )
    stockout: Dict[str, Any] = Field(description="StockoutPredictionResult details")
    intervention: Dict[str, Any] = Field(description="InterventionWindowResult details")
    critical_part: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Critical part metadata"
    )
    execution_time_ms: float = Field(
        description="End-to-end pipeline execution time in milliseconds (<25ms SLA)"
    )


__all__ = ["DisruptionRequest", "SimulationResponse"]
