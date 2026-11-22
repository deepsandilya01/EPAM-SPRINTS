"""Acceptance tests for Sonal's Sprint 2 inventory simulator."""

import pytest

from backend.app.simulation.inventory import simulate_inventory_depletion


def test_official_benchmark_stockout_and_timeline():
    result = simulate_inventory_depletion("P-01", 40, 5.0, 8.0)

    assert result.stockout_hour == 8.0
    assert len(result.timeline) == 73
    assert [point.hour for point in result.timeline] == list(range(73))
    assert [point.stock_units for point in result.timeline[:9]] == [
        40.0, 35.0, 30.0, 25.0, 20.0, 15.0, 10.0, 5.0, 0.0
    ]


def test_supply_is_blocked_for_hours_zero_to_seven():
    result = simulate_inventory_depletion("P-01", 40, 5.0, 8.0)

    assert all(point.supply_blocked for point in result.timeline[:8])
    assert result.timeline[8].supply_blocked is False


def test_stock_never_falls_below_zero():
    result = simulate_inventory_depletion("P-01", 10, 6.0, 8.0)

    assert all(point.stock_units >= 0 for point in result.timeline)
    assert result.stockout_hour == 2.0


def test_no_stockout_when_consumption_is_zero():
    result = simulate_inventory_depletion("P-01", 40, 0.0, 8.0)

    assert result.stockout_hour is None
    assert all(point.stock_units == 40.0 for point in result.timeline)


def test_no_stockout_if_horizon_ends_before_stock_reaches_zero():
    result = simulate_inventory_depletion(
        "P-01", 40, 5.0, 8.0, simulation_horizon_hours=7
    )

    assert len(result.timeline) == 8
    assert result.stockout_hour is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"part_id": "", "initial_stock": 40, "hourly_consumption": 5, "delay_duration_hours": 8},
        {"part_id": "P-01", "initial_stock": -1, "hourly_consumption": 5, "delay_duration_hours": 8},
        {"part_id": "P-01", "initial_stock": 40, "hourly_consumption": -1, "delay_duration_hours": 8},
        {"part_id": "P-01", "initial_stock": 40, "hourly_consumption": 5, "delay_duration_hours": -1},
    ],
)
def test_invalid_inputs_raise_value_error(kwargs):
    with pytest.raises(ValueError):
        simulate_inventory_depletion(**kwargs)
