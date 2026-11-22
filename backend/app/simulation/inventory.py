"""Discrete-time hourly inventory depletion simulator."""

from backend.app.models.inventory import (
    HourlyStockPoint,
    InventoryDepletionTimeline,
)


def simulate_inventory_depletion(
    part_id: str,
    initial_stock: float,
    hourly_consumption: float,
    delay_duration_hours: float,
    simulation_horizon_hours: int = 72,
) -> InventoryDepletionTimeline:
    """Calculate remaining stock for each hour in the simulation horizon.

    Stock(h) = max(0, Stock(h-1) - hourly_consumption)

    The supplier is treated as blocked for integer hours h where
    h < delay_duration_hours. Hour 0 records the initial stock without
    consuming it; consumption is applied at each subsequent hour.
    """
    if not part_id or not part_id.strip():
        raise ValueError("part_id must not be empty")
    if initial_stock < 0:
        raise ValueError("initial_stock must be non-negative")
    if hourly_consumption < 0:
        raise ValueError("hourly_consumption must be non-negative")
    if delay_duration_hours < 0:
        raise ValueError("delay_duration_hours must be non-negative")
    if simulation_horizon_hours < 0:
        raise ValueError("simulation_horizon_hours must be non-negative")

    current_stock = float(initial_stock)
    stockout_hour = None
    timeline = []

    for hour in range(simulation_horizon_hours + 1):
        if hour > 0:
            current_stock = max(0.0, current_stock - hourly_consumption)

        timeline.append(
            HourlyStockPoint(
                hour=hour,
                stock_units=round(current_stock, 4),
                supply_blocked=hour < delay_duration_hours,
            )
        )

        if current_stock == 0.0 and stockout_hour is None and hour > 0:
            stockout_hour = float(hour)

    return InventoryDepletionTimeline(
        part_id=part_id,
        initial_stock=float(initial_stock),
        hourly_consumption=float(hourly_consumption),
        delay_hours=float(delay_duration_hours),
        timeline=timeline,
        stockout_hour=stockout_hour,
    )
