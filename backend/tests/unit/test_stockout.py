"""Acceptance and unit tests for Feature 4: Stockout Predictor & 2-Order Matcher (Anushka).

Verifies Sprint 2 Acceptance Criteria:
- AC-06: Exactly 2 customer orders identified (benchmark anchor: ORD-01, ORD-02)
- AC-08: Stockout timestamp predicted (T_stockout == 8.0 hours)
"""

import pytest

from backend.app.models.impact import RippleImpactSummary
from backend.app.models.inventory import HourlyStockPoint, InventoryDepletionTimeline
from backend.app.simulation.inventory import simulate_inventory_depletion
from backend.app.simulation.stockout import predict_stockout_and_orders


@pytest.fixture
def benchmark_depletion() -> InventoryDepletionTimeline:
    """Official 8-hour delay scenario: 40 stock, 5/hr burn -> stocks out at hour 8.0."""
    return simulate_inventory_depletion(
        part_id="P-01",
        initial_stock=40,
        hourly_consumption=5.0,
        delay_duration_hours=8.0,
    )


@pytest.fixture
def benchmark_impact() -> RippleImpactSummary:
    """Downstream ripple impact summary from SUP-01 containing 5 affected orders."""
    return RippleImpactSummary(
        disrupted_supplier="SUP-01",
        affected_parts=["P-01"],
        affected_products=["PROD-01"],
        affected_orders=["ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05"],
        total_affected_nodes=7,
    )


@pytest.fixture
def benchmark_order_deadlines() -> dict:
    """Delivery deadlines from the calibrated scenario dataset."""
    return {
        "ORD-01": 10.0,
        "ORD-02": 12.0,
        "ORD-03": 36.0,
        "ORD-04": 48.0,
        "ORD-05": 72.0,
    }


def test_ac08_stockout_timestamp_predicted(benchmark_depletion, benchmark_impact, benchmark_order_deadlines):
    """AC-08: Stockout timestamp correctly identified from inventory depletion."""
    result = predict_stockout_and_orders(
        depletion=benchmark_depletion,
        impact=benchmark_impact,
        order_deadlines=benchmark_order_deadlines,
    )

    assert result.stockout_hour == 8.0
    assert result.no_stockout is False
    assert result.part_id == "P-01"


def test_ac06_exactly_two_orders_impacted_benchmark(benchmark_depletion, benchmark_impact, benchmark_order_deadlines):
    """AC-06: Exactly 2 customer orders (ORD-01, ORD-02) breach delivery deadline."""
    result = predict_stockout_and_orders(
        depletion=benchmark_depletion,
        impact=benchmark_impact,
        order_deadlines=benchmark_order_deadlines,
    )

    assert result.total_breached == 2
    breached_ids = [order.order_id for order in result.breached_orders]
    assert breached_ids == ["ORD-01", "ORD-02"]
    assert "ORD-01" in breached_ids
    assert "ORD-02" in breached_ids
    assert "ORD-03" not in breached_ids


def test_breached_order_reasons_and_attributes(benchmark_depletion, benchmark_impact, benchmark_order_deadlines):
    """Each breached order must record its deadline, will_fail=True, and explanatory reason."""
    result = predict_stockout_and_orders(
        depletion=benchmark_depletion,
        impact=benchmark_impact,
        order_deadlines=benchmark_order_deadlines,
    )

    ord_01 = next(o for o in result.breached_orders if o.order_id == "ORD-01")
    assert ord_01.delivery_deadline_hours == 10.0
    assert ord_01.will_fail is True
    assert "stocks out at hour 8.0" in ord_01.reason

    ord_02 = next(o for o in result.breached_orders if o.order_id == "ORD-02")
    assert ord_02.delivery_deadline_hours == 12.0
    assert ord_02.will_fail is True
    assert "stocks out at hour 8.0" in ord_02.reason


def test_no_stockout_returns_zero_breached():
    """When stock never runs out, no orders should breach."""
    depletion = InventoryDepletionTimeline(
        part_id="P-01",
        initial_stock=1000.0,
        hourly_consumption=1.0,
        delay_hours=8.0,
        timeline=[
            HourlyStockPoint(hour=h, stock_units=1000.0 - h, supply_blocked=(h < 8))
            for h in range(73)
        ],
        stockout_hour=None,
    )
    impact = RippleImpactSummary(
        disrupted_supplier="SUP-01",
        affected_parts=["P-01"],
        affected_products=["PROD-01"],
        affected_orders=["ORD-01", "ORD-02"],
        total_affected_nodes=4,
    )
    deadlines = {"ORD-01": 10.0, "ORD-02": 12.0}

    result = predict_stockout_and_orders(depletion, impact, deadlines)

    assert result.stockout_hour is None
    assert result.no_stockout is True
    assert result.total_breached == 0
    assert result.breached_orders == []


def test_missing_deadlines_skipped_safely(benchmark_depletion, benchmark_impact):
    """Orders in affected_orders without a deadline in order_deadlines are safely ignored."""
    deadlines = {"ORD-01": 10.0}  # ORD-02 to ORD-05 are missing
    result = predict_stockout_and_orders(
        depletion=benchmark_depletion,
        impact=benchmark_impact,
        order_deadlines=deadlines,
    )

    assert result.total_breached == 1
    assert result.breached_orders[0].order_id == "ORD-01"


def test_unaffected_orders_not_evaluated(benchmark_depletion, benchmark_order_deadlines):
    """Orders that are not downstream of the disruption must not be flagged."""
    impact = RippleImpactSummary(
        disrupted_supplier="SUP-02",
        affected_parts=["PART-03"],
        affected_products=["PROD-02"],
        affected_orders=["ORD-07", "ORD-08"],
        total_affected_nodes=4,
    )
    deadlines = {"ORD-01": 10.0, "ORD-07": 14.0, "ORD-08": 24.0}

    result = predict_stockout_and_orders(
        depletion=benchmark_depletion,
        impact=impact,
        order_deadlines=deadlines,
    )

    breached_ids = [o.order_id for o in result.breached_orders]
    assert "ORD-01" not in breached_ids  # Not affected by this supplier
