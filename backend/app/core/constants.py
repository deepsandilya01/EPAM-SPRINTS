"""
Project: RE:Flow
Sprint: 1
File: backend/app/core/constants.py

Ownership: Team Maintained
Role: Domain Constants and System Enums
Status: COMPLETED

Ownership: Team Maintained (Implemented by Deep during Sprint 1)
Role: Domain Constants and System Enums
Status: COMPLETED

Purpose:
System-wide constants and enumerations for the RE:Flow platform.
"""

from enum import Enum
from typing import Dict, Tuple


class TierType(str, Enum):
    """Enumeration of supply chain tiers in topological order."""
    SUPPLIER = "supplier"
    BOM_PART = "part"
    FINISHED_PRODUCT = "product"
    CUSTOMER_ORDER = "order"

    @classmethod
    def from_str(cls, value: str) -> "TierType":
        """Normalize case-insensitive or pluralized tier strings to TierType."""
        if not isinstance(value, str):
            raise ValueError(f"Tier must be a string, got {type(value).__name__}")
        normalized = value.strip().lower()
        mapping = {
            "supplier": cls.SUPPLIER,
            "suppliers": cls.SUPPLIER,
            "sup": cls.SUPPLIER,
            "part": cls.BOM_PART,
            "parts": cls.BOM_PART,
            "bom_part": cls.BOM_PART,
            "bom_parts": cls.BOM_PART,
            "product": cls.FINISHED_PRODUCT,
            "products": cls.FINISHED_PRODUCT,
            "finished_product": cls.FINISHED_PRODUCT,
            "finished_products": cls.FINISHED_PRODUCT,
            "prod": cls.FINISHED_PRODUCT,
            "order": cls.CUSTOMER_ORDER,
            "orders": cls.CUSTOMER_ORDER,
            "customer_order": cls.CUSTOMER_ORDER,
            "customer_orders": cls.CUSTOMER_ORDER,
            "ord": cls.CUSTOMER_ORDER,
        }
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(
            f"Unknown tier '{value}'. Allowed tiers: {[t.value for t in cls]}"
        )


class EdgeType(str, Enum):
    """Enumeration of valid directed relationship types between supply chain nodes."""
    SUPPLIES = "SUPPLIES"
    USED_IN = "USED_IN"
    FULFILLS = "FULFILLS"

    @classmethod
    def from_str(cls, value: str) -> "EdgeType":
        """Normalize case-insensitive relationship string to EdgeType."""
        if not isinstance(value, str):
            raise ValueError(f"Edge type must be a string, got {type(value).__name__}")
        normalized = value.strip().upper()
        mapping = {
            "SUPPLIES": cls.SUPPLIES,
            "USED_IN": cls.USED_IN,
            "USEDIN": cls.USED_IN,
            "USED-IN": cls.USED_IN,
            "FULFILLS": cls.FULFILLS,
        }
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(
            f"Unknown edge relationship '{value}'. Allowed: {[e.value for e in cls]}"
        )


# Valid directed transitions: (Source Tier, Target Tier) -> EdgeType
ALLOWED_TRANSITIONS: Dict[Tuple[TierType, TierType], EdgeType] = {
    (TierType.SUPPLIER, TierType.BOM_PART): EdgeType.SUPPLIES,
    (TierType.BOM_PART, TierType.FINISHED_PRODUCT): EdgeType.USED_IN,
    (TierType.FINISHED_PRODUCT, TierType.CUSTOMER_ORDER): EdgeType.FULFILLS,
}

# Canonical Sprint 1 baseline scenario metrics
CANONICAL_SUPPLIERS_COUNT = 2
CANONICAL_PARTS_COUNT = 5
CANONICAL_PRODUCTS_COUNT = 2
CANONICAL_ORDERS_COUNT = 10
CANONICAL_TOTAL_NODES = 19

CANONICAL_SUPPLIES_EDGE_COUNT = 6
CANONICAL_USED_IN_EDGE_COUNT = 5
CANONICAL_FULFILLS_EDGE_COUNT = 10
CANONICAL_TOTAL_EDGES = 21

# Performance SLAs
MAX_DOWNSTREAM_TRAVERSAL_SLA_MS = 10.0
