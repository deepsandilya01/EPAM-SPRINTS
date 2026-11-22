"""Stockout prediction and customer order breach analysis."""

from typing import Dict, Optional

from backend.app.models.impact import RippleImpactSummary
from backend.app.models.inventory import InventoryDepletionTimeline
from backend.app.models.stockout import BreachedOrder, StockoutPredictionResult


def predict_stockout_and_orders(
    depletion: InventoryDepletionTimeline,
    impact: RippleImpactSummary,
    order_deadlines: Dict[str, float],
    recovery_lead_time_hours: float = 5.0,
) -> StockoutPredictionResult:
    """Predict inventory stockout inflection and identify failing customer orders.

    Matches the Sprint 2 benchmark oracle (AC-06, AC-08):
    1. Extracts T_stockout from the inventory depletion timeline.
    2. Identifies orders reachable downstream from the disrupted supplier.
    3. Evaluates delivery deadlines against the stockout recovery window.
       Orders due before component recovery (T_stockout + t_recovery) cannot
       be manufactured/delivered on time and are flagged as breached.
    """
    stockout_hour = depletion.stockout_hour

    if stockout_hour is None:
        return StockoutPredictionResult(
            part_id=depletion.part_id,
            stockout_hour=None,
            no_stockout=True,
            breached_orders=[],
            total_breached=0,
        )

    # Stock is exhausted at stockout_hour and replenishment is unavailable
    # until the recovery lead time elapses. Orders due before replenishment
    # completes breach their promised delivery deadline.
    recovery_threshold = stockout_hour + recovery_lead_time_hours

    breached = []
    for order_id in impact.affected_orders:
        deadline = order_deadlines.get(order_id)
        if deadline is None:
            continue

        will_fail = deadline <= recovery_threshold

        if will_fail:
            breached.append(
                BreachedOrder(
                    order_id=order_id,
                    delivery_deadline_hours=float(deadline),
                    will_fail=True,
                    reason=(
                        f"Delivery due at hour {deadline}, but part '{depletion.part_id}' "
                        f"stocks out at hour {stockout_hour} (recovery available at hour {recovery_threshold})"
                    ),
                )
            )

    return StockoutPredictionResult(
        part_id=depletion.part_id,
        stockout_hour=stockout_hour,
        no_stockout=False,
        breached_orders=breached,
        total_breached=len(breached),
    )


__all__ = ["predict_stockout_and_orders"]
