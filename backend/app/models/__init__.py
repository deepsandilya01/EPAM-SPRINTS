"""
Project: RE:Flow
Sprint: 1
File: backend/app/models/__init__.py

Ownership: Team Maintained
Role: Graph Domain Models and Data Contracts
Status: COMPLETED

Ownership: Team Maintained (Implemented by Deep during Sprint 1)
Role: Graph Domain Models and Data Contracts
Status: COMPLETED

Purpose:
Models package initializer exposing domain entity classes for supply chain nodes, edges, and graphs.
"""

from backend.app.models.edges import (
    BaseEdge,
    EdgeUnion,
    FulfillsEdge,
    SuppliesEdge,
    UsedInEdge,
    create_edge,
)
from backend.app.models.graph import SupplyChainGraph
from backend.app.models.nodes import (
    BaseNode,
    BOMPartNode,
    CustomerOrderNode,
    FinishedProductNode,
    NodeUnion,
    SupplierNode,
    create_node,
)

__all__ = [
    # Nodes
    "BaseNode",
    "SupplierNode",
    "BOMPartNode",
    "FinishedProductNode",
    "CustomerOrderNode",
    "NodeUnion",
    "create_node",
    # Edges
    "BaseEdge",
    "SuppliesEdge",
    "UsedInEdge",
    "FulfillsEdge",
    "EdgeUnion",
    "create_edge",
    # Graph
    "SupplyChainGraph",
]
