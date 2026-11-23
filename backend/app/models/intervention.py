"""
Project: RE:Flow
Sprint: 2
File: backend/app/models/intervention.py

Primary Owner: Mishti
Role: Decision-Intelligence & ΔT Formula Engineer

Purpose:
Pydantic domain models for the intervention window calculation (Feature 5).
Tracks the window of opportunity to intervene before disruption causes irreversible customer damage.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class InterventionWindowResult(BaseModel):
    """Result of intervention window calculation.

    Formula: ΔT = T_stockout - T_curr - t_recovery
    - ΔT > 0  → FEASIBLE (action window is still open)
    - ΔT == 0 → CRITICAL (last moment to act)
    - ΔT < 0  → BREACHED (too late, irreversible damage)
    """

    stockout_hour: float = Field(
        description="Hour at which inventory hits zero (from StockoutPredictionResult)"
    )
    current_hour: float = Field(
        default=0.0,
        description="Simulation reference time (default 0.0)"
    )
    recovery_lead_time_hours: float = Field(
        description="Supplier recovery lead time in hours (from dataset/supplier)"
    )
    delta_t_hours: float = Field(
        description="Intervention window ΔT = T_stockout - T_curr - t_recovery"
    )
    is_feasible: bool = Field(
        description="True if ΔT > 0, indicating intervention is still possible"
    )
    status: str = Field(
        description="Categorical status: 'FEASIBLE' | 'CRITICAL' | 'BREACHED'"
    )
    affected_order_ids: List[str] = Field(
        default_factory=list,
        description="List of customer orders breached or affected"
    )
    message: str = Field(
        default="",
        description="Human-readable decision intelligence guidance"
    )


__all__ = ["InterventionWindowResult"]
