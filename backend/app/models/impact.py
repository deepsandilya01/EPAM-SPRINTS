from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class RippleImpactSummary(BaseModel):
    disrupted_supplier: str
    affected_parts: List[str] = Field(default_factory=list, description="Downstream affected BOM parts")
    affected_products: List[str] = Field(default_factory=list, description="Downstream affected finished products")
    affected_orders: List[str] = Field(default_factory=list, description="Downstream affected customer orders")
    total_affected_nodes: int = Field(default=0, description="Total unique downstream nodes excluding supplier")

