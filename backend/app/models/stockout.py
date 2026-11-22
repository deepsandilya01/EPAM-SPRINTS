"""Pydantic models for stockout prediction and breached customer orders."""

from typing import List, Optional
from pydantic import BaseModel, Field


class BreachedOrder(BaseModel):
    """Customer order that will breach its delivery deadline due to stockout."""

    order_id: str = Field(description="Customer order identifier, e.g. ORD-01")
    delivery_deadline_hours: float = Field(
        description="Delivery deadline in hours from simulation start"
    )
    will_fail: bool = Field(
        default=True, description="Whether this order is predicted to fail"
    )
    reason: str = Field(
        default="", description="Diagnostic reason for predicted breach"
    )


class StockoutPredictionResult(BaseModel):
    """Prediction outcome of stockout inflection and impacted customer orders."""

    part_id: str = Field(description="Identifier of the depleted component part")
    stockout_hour: Optional[float] = Field(
        default=None, description="Hour at which inventory stock hits zero"
    )
    no_stockout: bool = Field(
        default=False, description="True if stock remains positive across horizon"
    )
    breached_orders: List[BreachedOrder] = Field(
        default_factory=list,
        description="List of customer orders predicted to fail",
    )
    total_breached: int = Field(
        default=0, description="Total count of breached orders"
    )
