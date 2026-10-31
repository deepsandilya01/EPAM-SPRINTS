from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from backend.app.core.constants import TierType
from backend.app.core.exceptions import ModelValidationError


@dataclass(eq=False)
class BaseNode(ABC):
    """
    Base domain model for any node in the supply chain graph.

    Why this exists:
    All supply chain entities (suppliers, parts, products, orders) share common
    graph properties: a unique identifier, a tier category, and a readable name.
    Subclasses extend this with tier-specific supply chain attributes.
    """
    id: str
    tier: TierType
    name: str
    label: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate that ID is a non-empty string (required for graph node identification)
        if not isinstance(self.id, str) or not self.id.strip():
            raise ModelValidationError("Node ID must be a non-empty string.", field="id")
        self.id = self.id.strip()

        # Convert string tier to enum if string was provided
        if isinstance(self.tier, str) and not isinstance(self.tier, TierType):
            self.tier = TierType.from_str(self.tier)

        # Validate that node has a readable name
        if not isinstance(self.name, str) or not self.name.strip():
            raise ModelValidationError("Node name must be a non-empty string.", field="name")
        self.name = self.name.strip()

        # If human-friendly label was not explicitly provided, default to the node name
        if not self.label:
            self.label = self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert the domain node into a dictionary for JSON serialization."""
        node_dict = {
            "id": self.id,
            "tier": self.tier.value,
            "kind": self.tier.value,
            "name": self.name,
            "label": self.label,
        }
        # Include any extra attributes stored in the dictionary
        node_dict.update(self.attributes)
        return node_dict

    def __hash__(self) -> int:
        # In a graph, a node is uniquely identified by its ID.
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        # Two node objects are identical if they belong to BaseNode and have matching IDs.
        if not isinstance(other, BaseNode):
            return False
        return self.id == other.id


@dataclass(eq=False)
class SupplierNode(BaseNode):
    """
    Tier 1: Supplier node representing component and material vendors.

    Domain Attributes:
    - location: City or region of the vendor facility (e.g. 'Pune')
    - note: Operational note or qualification detail
    """
    location: str = ""
    note: Optional[str] = None

    def __post_init__(self) -> None:
        self.tier = TierType.SUPPLIER
        super().__post_init__()

        # Pull from attributes dict if not supplied as direct arguments
        if not self.location:
            self.location = self.attributes.get("location", "")
        if self.note is None:
            self.note = self.attributes.get("note")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["location"] = self.location
        if self.note is not None:
            data["note"] = self.note
        return data


@dataclass(eq=False)
class BOMPartNode(BaseNode):
    """
    Tier 2: Bill of Materials (BOM) Part node.

    Domain Attributes:
    - stock_on_hand: Units currently available in warehouse
    - daily_consumption: Units consumed per day during production
    - days_of_supply: How many days current stock will last (stock / daily_consumption)
    """
    stock_on_hand: int = 0
    daily_consumption: int = 0
    days_of_supply: float = 0.0

    def __post_init__(self) -> None:
        self.tier = TierType.BOM_PART
        super().__post_init__()

        # Inventory cannot be negative in physical supply chains
        if self.stock_on_hand < 0:
            raise ModelValidationError(
                f"stock_on_hand must be non-negative, got {self.stock_on_hand}",
                field="stock_on_hand",
            )
        if self.daily_consumption < 0:
            raise ModelValidationError(
                f"daily_consumption must be non-negative, got {self.daily_consumption}",
                field="daily_consumption",
            )

        # Automatically compute days of supply if not provided in the raw dataset
        if not self.days_of_supply:
            if self.daily_consumption > 0:
                self.days_of_supply = round(self.stock_on_hand / self.daily_consumption, 2)
            else:
                self.days_of_supply = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["stock_on_hand"] = self.stock_on_hand
        data["daily_consumption"] = self.daily_consumption
        data["days_of_supply"] = self.days_of_supply
        return data


@dataclass(eq=False)
class FinishedProductNode(BaseNode):
    """
    Tier 3: Finished Product node representing assembled goods ready for customer orders.

    Domain Attributes:
    - parts_needed: Summary description of subcomponents required (e.g. 'PART-01 x1, PART-02 x1')
    """
    parts_needed: str = ""

    def __post_init__(self) -> None:
        self.tier = TierType.FINISHED_PRODUCT
        super().__post_init__()

        if not self.parts_needed:
            self.parts_needed = self.attributes.get("parts_needed", "")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if self.parts_needed:
            data["parts_needed"] = self.parts_needed
        return data


@dataclass(eq=False)
class CustomerOrderNode(BaseNode):
    """
    Tier 4: Customer Order node representing customer demand and fulfillment targets.

    Domain Attributes:
    - customer: Client company or retail buyer name
    - product_id: ID of the finished product being purchased
    - quantity: Total units ordered (must be at least 1)
    - deadline: Target delivery date (ISO format string YYYY-MM-DD)
    """
    customer: str = ""
    product_id: str = ""
    quantity: int = 0
    deadline: str = ""

    def __post_init__(self) -> None:
        self.tier = TierType.CUSTOMER_ORDER
        super().__post_init__()

        if not self.customer:
            self.customer = self.attributes.get("customer", "")
        if not self.product_id:
            self.product_id = self.attributes.get("product_id", "")

        # Customer orders must demand at least 1 unit
        if self.quantity <= 0:
            raise ModelValidationError(
                f"Order quantity must be positive, got {self.quantity}",
                field="quantity",
            )

        if not self.deadline:
            self.deadline = self.attributes.get("deadline", "")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["customer"] = self.customer
        data["product_id"] = self.product_id
        data["quantity"] = self.quantity
        data["deadline"] = self.deadline
        return data


NodeUnion = Union[SupplierNode, BOMPartNode, FinishedProductNode, CustomerOrderNode]


def create_node(node_data: Dict[str, Any]) -> NodeUnion:
    """
    Factory function to create the appropriate domain node instance from a dictionary.

    Handles raw scenario dataset variations, including tier aliases ('kind', 'tier')
    and field naming differences (e.g. 'supplier_id', 'part_id').
    """
    if not isinstance(node_data, dict):
        raise ModelValidationError(f"Expected dict for node creation, got {type(node_data).__name__}")

    # Step 1: Extract unique node ID (check canonical 'id' first, then tier-specific aliases)
    node_id = (
        node_data.get("id")
        or node_data.get("supplier_id")
        or node_data.get("part_id")
        or node_data.get("product_id")
        or node_data.get("order_id")
    )
    if not node_id:
        raise ModelValidationError("Node data missing required identifier ('id').", field="id")

    # Step 2: Determine node tier from explicit field or node ID prefix
    raw_tier = node_data.get("kind") or node_data.get("tier")
    if raw_tier:
        tier = TierType.from_str(raw_tier)
    elif node_id.startswith("SUP-"):
        tier = TierType.SUPPLIER
    elif node_id.startswith("PART-"):
        tier = TierType.BOM_PART
    elif node_id.startswith("PROD-"):
        tier = TierType.FINISHED_PRODUCT
    elif node_id.startswith("ORD-"):
        tier = TierType.CUSTOMER_ORDER
    else:
        raise ModelValidationError(f"Unable to determine node tier for node ID '{node_id}'.")

    # Step 3: Extract display name and human-readable label
    name = node_data.get("name") or node_data.get("label") or node_id
    label = node_data.get("label") or name

    # Step 4: Collect remaining custom attributes
    standard_keys = {
        "id", "tier", "kind", "name", "label",
        "supplier_id", "part_id", "product_id", "order_id",
        "location", "note", "stock_on_hand", "daily_consumption",
        "days_of_supply", "parts_needed", "customer", "quantity", "deadline"
    }
    extra_attributes = {k: v for k, v in node_data.items() if k not in standard_keys}

    # Step 5: Instantiate the specific node subclass
    if tier == TierType.SUPPLIER:
        return SupplierNode(
            id=node_id,
            tier=tier,
            name=name,
            label=label,
            location=node_data.get("location", ""),
            note=node_data.get("note"),
            attributes=extra_attributes,
        )

    if tier == TierType.BOM_PART:
        return BOMPartNode(
            id=node_id,
            tier=tier,
            name=name,
            label=label,
            stock_on_hand=int(node_data.get("stock_on_hand", 0)),
            daily_consumption=int(node_data.get("daily_consumption", 0)),
            days_of_supply=float(node_data.get("days_of_supply", 0.0)),
            attributes=extra_attributes,
        )

    if tier == TierType.FINISHED_PRODUCT:
        return FinishedProductNode(
            id=node_id,
            tier=tier,
            name=name,
            label=label,
            parts_needed=node_data.get("parts_needed", ""),
            attributes=extra_attributes,
        )

    if tier == TierType.CUSTOMER_ORDER:
        return CustomerOrderNode(
            id=node_id,
            tier=tier,
            name=name,
            label=label,
            customer=node_data.get("customer", ""),
            product_id=node_data.get("product_id", ""),
            quantity=int(node_data.get("quantity", 0)),
            deadline=node_data.get("deadline", ""),
            attributes=extra_attributes,
        )

    raise ModelValidationError(f"Unsupported tier: {tier}")
