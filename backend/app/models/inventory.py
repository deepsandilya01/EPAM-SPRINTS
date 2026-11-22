"""Pydantic models for hourly inventory depletion simulation."""

from typing import List, Optional

from pydantic import BaseModel


class HourlyStockPoint(BaseModel):
    """Inventory state at one simulation hour."""

    hour: int
    stock_units: float
    supply_blocked: bool


class InventoryDepletionTimeline(BaseModel):
    """Hourly inventory depletion result for one part."""

    part_id: str
    initial_stock: float
    hourly_consumption: float
    delay_hours: float
    timeline: List[HourlyStockPoint]
    stockout_hour: Optional[float] = None
