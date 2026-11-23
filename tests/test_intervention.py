"""Feature 5 tests using Pydantic models matching Anushka's contract."""

import sys
import types

from pydantic import BaseModel


# The integration package intentionally does not ship Anushka's file.
# Provide its documented Pydantic interface only when running this isolated
# Feature 5 test suite; the real project module takes precedence if present.
try:
    from backend.app.models.stockout import StockoutPredictionResult  # noqa: F401
except ModuleNotFoundError:
    stockout_module = types.ModuleType("backend.app.models.stockout")

    class BreachedOrder(BaseModel):
        order_id: str
        delivery_deadline_hours: float
        will_fail: bool = True
        reason: str = ""

    class StockoutPredictionResult(BaseModel):
        part_id: str
        stockout_hour: float | None = None
        no_stockout: bool = False
        breached_orders: list[BreachedOrder] = []
        total_breached: int = 0

    stockout_module.BreachedOrder = BreachedOrder
    stockout_module.StockoutPredictionResult = StockoutPredictionResult
    sys.modules["backend.app.models.stockout"] = stockout_module

from backend.app.simulation.intervention import calculate_intervention_window
from backend.app.models.stockout import StockoutPredictionResult, BreachedOrder


def benchmark_result() -> StockoutPredictionResult:
    return StockoutPredictionResult(
        part_id="PART-05",
        stockout_hour=8.0,
        no_stockout=False,
        breached_orders=[
            BreachedOrder(
                order_id="ORD-01",
                delivery_deadline_hours=10.0,
                will_fail=True,
                reason="Benchmark order breach",
            ),
            BreachedOrder(
                order_id="ORD-02",
                delivery_deadline_hours=12.0,
                will_fail=True,
                reason="Benchmark order breach",
            ),
        ],
        total_breached=2,
    )


def test_official_benchmark_returns_three_hour_feasible_window():
    result = calculate_intervention_window(benchmark_result())

    assert result.stockout_hour == 8.0
    assert result.current_hour == 0.0
    assert result.recovery_lead_time_hours == 5.0
    assert result.delta_t_hours == 3.0
    assert result.is_feasible is True
    assert result.status == "FEASIBLE"
    assert result.affected_order_ids == ["ORD-01", "ORD-02"]


def test_positive_delta_is_feasible():
    result = calculate_intervention_window(
        benchmark_result(), current_hour=1.0, recovery_lead_time_hours=5.0
    )
    assert result.delta_t_hours == 2.0
    assert result.status == "FEASIBLE"
    assert result.is_feasible is True


def test_zero_delta_is_critical_and_still_feasible():
    result = calculate_intervention_window(
        benchmark_result(), current_hour=3.0, recovery_lead_time_hours=5.0
    )
    assert result.delta_t_hours == 0.0
    assert result.status == "CRITICAL"
    assert result.is_feasible is True


def test_negative_delta_is_breached_and_not_feasible():
    result = calculate_intervention_window(
        benchmark_result(), current_hour=4.0, recovery_lead_time_hours=5.0
    )
    assert result.delta_t_hours == -1.0
    assert result.status == "BREACHED"
    assert result.is_feasible is False


def test_uses_recovery_lead_time_passed_by_pipeline():
    # SUP-02's calibrated recovery lead time is 6.0 h in the scenario data.
    result = calculate_intervention_window(
        benchmark_result(), recovery_lead_time_hours=6.0
    )
    assert result.recovery_lead_time_hours == 6.0
    assert result.delta_t_hours == 2.0


def test_no_stockout_returns_specified_infinite_window_and_no_orders():
    no_stockout = StockoutPredictionResult(
        part_id="PART-05",
        stockout_hour=None,
        no_stockout=True,
        breached_orders=[],
        total_breached=0,
    )
    result = calculate_intervention_window(no_stockout)

    assert result.stockout_hour == float("inf")
    assert result.delta_t_hours == float("inf")
    assert result.status == "FEASIBLE"
    assert result.is_feasible is True
    assert result.affected_order_ids == []


def test_affected_order_ids_are_taken_from_stockout_result():
    result = calculate_intervention_window(benchmark_result())
    assert result.affected_order_ids == ["ORD-01", "ORD-02"]


def test_result_model_has_only_the_eight_specified_fields():
    from backend.app.models.intervention import InterventionWindowResult

    assert set(InterventionWindowResult.model_fields) == {
        "stockout_hour",
        "current_hour",
        "recovery_lead_time_hours",
        "delta_t_hours",
        "is_feasible",
        "status",
        "affected_order_ids",
        "message",
    }
