from __future__ import annotations

from typing import Any

from backend.app.core.constants import (
    EdgeType,
    TierType,
)

# Canonical tier progression order
TIER_ORDER = [
    TierType.SUPPLIER.value,
    TierType.BOM_PART.value,
    TierType.FINISHED_PRODUCT.value,
    TierType.CUSTOMER_ORDER.value,
]

# Allowed directed tier transitions
ALLOWED_TRANSITIONS = {
    EdgeType.SUPPLIES.value: (TierType.SUPPLIER.value, TierType.BOM_PART.value),
    EdgeType.USED_IN.value: (TierType.BOM_PART.value, TierType.FINISHED_PRODUCT.value),
    EdgeType.FULFILLS.value: (TierType.FINISHED_PRODUCT.value, TierType.CUSTOMER_ORDER.value),
}

# Required node attributes by tier
REQUIRED_NODE_KEYS = {
    TierType.SUPPLIER.value: {"id", "name", "tier", "location"},
    TierType.BOM_PART.value: {"id", "name", "tier", "stock_on_hand", "daily_consumption", "days_of_supply"},
    TierType.FINISHED_PRODUCT.value: {"id", "name", "tier", "parts_needed"},
    TierType.CUSTOMER_ORDER.value: {"id", "name", "tier", "customer", "quantity", "deadline"},
}

# Required edge attributes
REQUIRED_EDGE_KEYS = {"source", "target", "relation"}


def is_valid_tier_transition(relation: str, source_tier: str, target_tier: str) -> bool:
    """Check if the edge relation satisfies the tier transition specification."""
    expected = ALLOWED_TRANSITIONS.get(relation)
    if not expected:
        return False
    return (source_tier, target_tier) == expected


def validate_node_attributes(node_id: str, tier: str, attributes: dict[str, Any]) -> list[str]:
    """Return list of missing required attribute names for a given node tier."""
    required = REQUIRED_NODE_KEYS.get(tier, {"id", "name", "tier"})
    return [k for k in required if k not in attributes and k != "id" and k != "tier"]
