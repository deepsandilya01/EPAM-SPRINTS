"""Canonical schema and configurable baseline expectations."""
from dataclasses import dataclass

NODE_CATEGORIES = {"suppliers": "supplier", "parts": "part", "products": "product", "orders": "order"}
RELATIONSHIP_CATEGORIES = {"supplies": ("supplier", "part"), "used_in": ("part", "product"), "fulfills": ("product", "order")}
EXPECTED_NODE_COUNTS = {"supplier": 2, "part": 5, "product": 2, "order": 10}
EXPECTED_EDGE_COUNTS = {"supplies": 6, "used_in": 5, "fulfills": 10}

NODE_REQUIRED_FIELDS = {
    "supplier": {"id": str, "kind": str, "label": str, "name": str, "location": str},
    "part": {"id": str, "kind": str, "label": str, "name": str, "stock_on_hand": (int, float), "daily_consumption": (int, float), "days_of_supply": (int, float)},
    "product": {"id": str, "kind": str, "label": str, "name": str, "parts_needed": str},
    "order": {"id": str, "kind": str, "label": str, "order_id": str, "customer": str, "product_id": str, "quantity": (int, float), "deadline": str},
}
EDGE_REQUIRED_FIELDS = {"relation": str, "source": str, "target": str}
@dataclass(frozen=True)
class ValidationPolicy:
    directed: bool = True
    require_acyclic: bool | None = True
    check_baseline_counts: bool = True
