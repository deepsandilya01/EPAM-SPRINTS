"""
Project: RE:Flow
Sprint: 1
File: backend/app/models/edges.py

Ownership: Team Maintained 
Role: Graph Domain Models and Data Contracts
Status: COMPLETED

Ownership: Team Maintained (Implemented by Deep during Sprint 1)
Role: Graph Domain Models and Data Contracts
Status: COMPLETED

Purpose:
Domain models for the 3 directed supply chain relationships:
1. SUPPLIES (Tier 1 -> Tier 2) - Supplier supplies a BOM Part
2. USED_IN (Tier 2 -> Tier 3) - BOM Part is assembled into a Finished Product
3. FULFILLS (Tier 3 -> Tier 4) - Finished Product fulfills a Customer Order
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from backend.app.core.constants import ALLOWED_TRANSITIONS, EdgeType
from backend.app.core.exceptions import InvalidEdgeError
from backend.app.models.nodes import BaseNode


@dataclass(eq=False)
class BaseEdge(ABC):
    """
    Base domain model for a directed relationship in the supply chain graph.

    Why this exists:
    A supply chain dependency always has a direction: from an upstream provider
    (source) to a downstream dependent (target). This class enforces non-empty
    endpoints, forbids self-loops, and verifies tier transition validity.
    """
    source: str
    target: str
    relation: EdgeType
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate that source and target are non-empty strings
        if not isinstance(self.source, str) or not self.source.strip():
            raise InvalidEdgeError("Edge source must be a non-empty string ID.", source=self.source, target=self.target)
        self.source = self.source.strip()

        if not isinstance(self.target, str) or not self.target.strip():
            raise InvalidEdgeError("Edge target must be a non-empty string ID.", source=self.source, target=self.target)
        self.target = self.target.strip()

        # In a supply chain DAG, an item cannot supply or fulfill itself.
        if self.source == self.target:
            raise InvalidEdgeError(
                f"Self-loops are forbidden in supply chain DAG: {self.source} -> {self.target}",
                source=self.source,
                target=self.target,
            )

        # Convert string relation to EdgeType enum if needed
        if isinstance(self.relation, str) and not isinstance(self.relation, EdgeType):
            self.relation = EdgeType.from_str(self.relation)

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge into a dictionary for JSON serialization."""
        edge_dict = {
            "source": self.source,
            "target": self.target,
            "relation": self.relation.value,
            "relationship_type": self.relation.value,
        }
        edge_dict.update(self.attributes)
        return edge_dict

    def validate_endpoints(self, source_node: BaseNode, target_node: BaseNode) -> None:
        """
        Check that connected nodes follow the strict 4-tier supply chain progression:
        - Supplier -> Part (SUPPLIES)
        - Part -> Product (USED_IN)
        - Product -> Order (FULFILLS)

        Raises InvalidEdgeError if an illegal jump occurs (e.g. Supplier -> Order directly).
        """
        expected_relation = ALLOWED_TRANSITIONS.get((source_node.tier, target_node.tier))
        if expected_relation is None:
            raise InvalidEdgeError(
                f"Illegal tier jump: {source_node.tier.value} ('{source_node.id}') cannot connect to "
                f"{target_node.tier.value} ('{target_node.id}').",
                source=self.source,
                target=self.target,
            )
        if self.relation != expected_relation:
            raise InvalidEdgeError(
                f"Mismatched relationship: connection between {source_node.tier.value} and {target_node.tier.value} "
                f"must be '{expected_relation.value}', but got '{self.relation.value}'.",
                source=self.source,
                target=self.target,
            )

    def __hash__(self) -> int:
        # An edge is uniquely identified by (source, target, relation)
        return hash((self.source, self.target, str(self.relation)))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseEdge):
            return False
        return (
            self.source == other.source
            and self.target == other.target
            and str(self.relation) == str(other.relation)
        )


@dataclass(eq=False)
class SuppliesEdge(BaseEdge):
    """
    Tier 1 -> Tier 2: Supplier -> BOM Part relationship.

    Domain Attributes:
    - lead_time_hours: Time in hours for supplier to deliver component
    - max_capacity_units_per_day: Maximum units the supplier can ship daily
    """
    lead_time_hours: Optional[int] = None
    max_capacity_units_per_day: Optional[int] = None

    def __post_init__(self) -> None:
        self.relation = EdgeType.SUPPLIES
        super().__post_init__()

        # Pull from attributes dictionary if passed indirectly
        if self.lead_time_hours is None and "lead_time_hours" in self.attributes:
            self.lead_time_hours = int(self.attributes["lead_time_hours"])
        if self.max_capacity_units_per_day is None and "max_capacity_units_per_day" in self.attributes:
            self.max_capacity_units_per_day = int(self.attributes["max_capacity_units_per_day"])

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if self.lead_time_hours is not None:
            data["lead_time_hours"] = self.lead_time_hours
        if self.max_capacity_units_per_day is not None:
            data["max_capacity_units_per_day"] = self.max_capacity_units_per_day
        return data


@dataclass(eq=False)
class UsedInEdge(BaseEdge):
    """
    Tier 2 -> Tier 3: BOM Part -> Finished Product relationship.

    Domain Attributes:
    - quantity_per_unit: Number of part units required to assemble one finished product
    """
    quantity_per_unit: int = 1

    def __post_init__(self) -> None:
        self.relation = EdgeType.USED_IN
        super().__post_init__()

        # Read quantity from attributes if present
        if "quantity_per_unit" in self.attributes:
            self.quantity_per_unit = int(self.attributes["quantity_per_unit"])
        elif "quantity_per_product" in self.attributes:
            self.quantity_per_unit = int(self.attributes["quantity_per_product"])

        # Assembly requires at least 1 unit of a component
        if self.quantity_per_unit <= 0:
            raise InvalidEdgeError(
                f"quantity_per_unit must be positive, got {self.quantity_per_unit}",
                source=self.source,
                target=self.target,
            )

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["quantity_per_unit"] = self.quantity_per_unit
        data["quantity_per_product"] = self.quantity_per_unit
        return data


@dataclass(eq=False)
class FulfillsEdge(BaseEdge):
    """
    Tier 3 -> Tier 4: Finished Product -> Customer Order relationship.
    Indicates that the specified assembled product satisfies the customer order.
    """
    def __post_init__(self) -> None:
        self.relation = EdgeType.FULFILLS
        super().__post_init__()


EdgeUnion = Union[SuppliesEdge, UsedInEdge, FulfillsEdge]


def create_edge(edge_data: Dict[str, Any]) -> EdgeUnion:
    """
    Factory function to create the appropriate domain edge instance from a dictionary.

    Handles field aliases from raw scenario datasets (e.g. 'from_supplier', 'to_part').
    """
    if not isinstance(edge_data, dict):
        raise InvalidEdgeError(f"Expected dict for edge creation, got {type(edge_data).__name__}")

    # Step 1: Extract source and target IDs
    source = (
        edge_data.get("source")
        or edge_data.get("from_supplier")
        or edge_data.get("from_part")
        or edge_data.get("from_product")
    )
    target = (
        edge_data.get("target")
        or edge_data.get("to_part")
        or edge_data.get("to_product")
        or edge_data.get("to_order")
    )

    if not source:
        raise InvalidEdgeError("Missing required edge source identifier.", target=target)
    if not target:
        raise InvalidEdgeError("Missing required edge target identifier.", source=source)

    # Step 2: Determine edge relationship type
    raw_relation = edge_data.get("relation") or edge_data.get("relationship_type") or edge_data.get("type")
    if not raw_relation:
        # Infer relationship from node ID prefixes if relation is omitted
        if source.startswith("SUP-") and target.startswith("PART-"):
            relation = EdgeType.SUPPLIES
        elif source.startswith("PART-") and target.startswith("PROD-"):
            relation = EdgeType.USED_IN
        elif source.startswith("PROD-") and target.startswith("ORD-"):
            relation = EdgeType.FULFILLS
        else:
            raise InvalidEdgeError(f"Cannot determine edge relation for {source} -> {target}")
    else:
        relation = EdgeType.from_str(raw_relation)

    # Step 3: Collect extra metadata
    standard_keys = {
        "source", "target", "relation", "relationship_type", "type",
        "from_supplier", "to_part", "from_part", "to_product", "from_product", "to_order",
        "lead_time_hours", "max_capacity_units_per_day", "quantity_per_unit", "quantity_per_product"
    }
    extra_attributes = {k: v for k, v in edge_data.items() if k not in standard_keys}

    # Step 4: Instantiate and return the appropriate edge subclass
    if relation == EdgeType.SUPPLIES:
        lead_time = edge_data.get("lead_time_hours")
        lead_time_int = int(lead_time) if lead_time is not None else None
        capacity = edge_data.get("max_capacity_units_per_day")
        capacity_int = int(capacity) if capacity is not None else None

        return SuppliesEdge(
            source=source,
            target=target,
            relation=relation,
            lead_time_hours=lead_time_int,
            max_capacity_units_per_day=capacity_int,
            attributes=extra_attributes,
        )

    if relation == EdgeType.USED_IN:
        qty = edge_data.get("quantity_per_unit") or edge_data.get("quantity_per_product", 1)
        return UsedInEdge(
            source=source,
            target=target,
            relation=relation,
            quantity_per_unit=int(qty),
            attributes=extra_attributes,
        )

    if relation == EdgeType.FULFILLS:
        return FulfillsEdge(
            source=source,
            target=target,
            relation=relation,
            attributes=extra_attributes,
        )

    raise InvalidEdgeError(f"Unsupported edge relationship type: {relation}")
