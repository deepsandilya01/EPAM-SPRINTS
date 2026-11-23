"""Pydantic result model for Sprint 2 Feature 5: Intervention Window."""

from typing import List

from pydantic import BaseModel


class InterventionWindowResult(BaseModel):
    """Result produced by the intervention-window calculator."""

    stockout_hour: float
    current_hour: float
    recovery_lead_time_hours: float
    delta_t_hours: float
    is_feasible: bool
    status: str
    affected_order_ids: List[str]
    message: str
