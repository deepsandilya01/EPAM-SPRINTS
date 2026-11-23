"""
Project: RE:Flow
Sprint: 2
File: backend/app/simulation/intervention.py

Primary Owner: Mishti
Role: Decision-Intelligence & ΔT Formula Engineer

Purpose:
Calculates the intervention window (ΔT) to evaluate whether a supply disruption
can be mitigated before critical stockout occurs and customer orders fail.

Official Formula:
    ΔT_intervention = T_stockout - T_current - t_recovery_lead_time

Thresholds:
    ΔT > 0  → FEASIBLE  (action window still open)
    ΔT == 0 → CRITICAL  (last moment to act)
    ΔT < 0  → BREACHED  (too late, irreversible damage)

Benchmark Oracle Validation:
    T_stockout       = 8.0 hours
    T_current        = 0.0 hours
    t_recovery       = 5.0 hours
    ΔT = 8.0 - 0.0 - 5.0 = +3.0 hours
    Status = FEASIBLE  (AC-09)
"""

from __future__ import annotations

from typing import Optional
from backend.app.models.intervention import InterventionWindowResult
from backend.app.models.stockout import StockoutPredictionResult


def calculate_intervention_window(
    stockout_result: StockoutPredictionResult,
    current_hour: float = 0.0,
    recovery_lead_time_hours: float = 5.0,
) -> InterventionWindowResult:
    """Calculate the actionable intervention window ΔT.

    Parameters
    ----------
    stockout_result : StockoutPredictionResult
        Result from Anushka's stockout predictor.
    current_hour : float
        Current simulation reference hour (default: 0.0).
    recovery_lead_time_hours : float
        Supplier recovery lead time in hours (default: 5.0 for SUP-01).

    Returns
    -------
    InterventionWindowResult
        Structured calculation with delta_t_hours, feasibility flag, and advice.
    """
    t_stockout = stockout_result.stockout_hour

    if t_stockout is None:
        return InterventionWindowResult(
            stockout_hour=float("inf"),
            current_hour=current_hour,
            recovery_lead_time_hours=recovery_lead_time_hours,
            delta_t_hours=float("inf"),
            is_feasible=True,
            status="FEASIBLE",
            affected_order_ids=[],
            message="No stockout predicted. No intervention required.",
        )

    delta_t = t_stockout - current_hour - recovery_lead_time_hours

    if delta_t > 0:
        status = "FEASIBLE"
        is_feasible = True
        message = f"Action window is OPEN. {delta_t:.1f} hours remaining to intervene."
    elif delta_t == 0:
        status = "CRITICAL"
        is_feasible = True
        message = "CRITICAL: Last moment to act. Immediate action required."
    else:
        status = "BREACHED"
        is_feasible = False
        message = f"Intervention window BREACHED by {abs(delta_t):.1f} hours."

    affected_ids = [o.order_id for o in stockout_result.breached_orders]

    return InterventionWindowResult(
        stockout_hour=t_stockout,
        current_hour=current_hour,
        recovery_lead_time_hours=recovery_lead_time_hours,
        delta_t_hours=round(delta_t, 4),
        is_feasible=is_feasible,
        status=status,
        affected_order_ids=affected_ids,
        message=message,
    )


# Compatibility alias
compute_intervention_window = calculate_intervention_window

__all__ = ["calculate_intervention_window", "compute_intervention_window"]
