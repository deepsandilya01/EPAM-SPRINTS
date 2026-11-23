"""Sprint 2 Feature 5: Intervention Window Calculator."""

from backend.app.models.intervention import InterventionWindowResult
from backend.app.models.stockout import StockoutPredictionResult


def calculate_intervention_window(
    stockout_result: StockoutPredictionResult,
    current_hour: float = 0.0,
    recovery_lead_time_hours: float = 5.0,
) -> InterventionWindowResult:
    """Calculate ΔT = T_stockout - T_current - t_recovery_lead_time.

    Status rules from the Team Photon Sprint 2 responsibilities:
    - ΔT > 0: FEASIBLE
    - ΔT == 0: CRITICAL
    - ΔT < 0: BREACHED

    The calculator consumes Anushka's StockoutPredictionResult and copies
    its breached order IDs. It does not recalculate order impact or choose a
    supplier; the selected supplier's recovery lead time is supplied by the
    caller (default 5.0 hours for the official benchmark).
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

    affected_ids = [order.order_id for order in stockout_result.breached_orders]

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
