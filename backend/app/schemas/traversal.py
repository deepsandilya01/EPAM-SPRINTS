"""
Project: RE:Flow
Sprint: 1
File: backend/app/schemas/traversal.py

Ownership: Team Maintained 
Role: Graph Domain Models and Data Contracts
Status: COMPLETED

Ownership: Team Maintained (Implemented by Deep during Sprint 1)
Role: Graph Domain Models and Data Contracts
Status: COMPLETED

Purpose:
Request and response validation contracts for graph traversal and downstream
blast-radius impact analysis (POST /api/traversal).
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TraversalDirection(str, Enum):
    """
    Direction of graph propagation:
    - DOWNSTREAM: From supplier towards customer orders (blast-radius analysis)
    - UPSTREAM: From customer order back towards suppliers (root-cause tracing)
    """
    DOWNSTREAM = "downstream"
    UPSTREAM = "upstream"


class TraversalRequestSchema(BaseModel):
    """
    Request payload schema for graph traversal requests.

    Example:
    {
      "node_id": "SUP-01",
      "direction": "downstream",
      "max_depth": 5
    }
    """
    model_config = ConfigDict(populate_by_name=True)

    node_id: str = Field(..., min_length=1, description="Root node identifier to initiate traversal from")
    direction: TraversalDirection = Field(
        default=TraversalDirection.DOWNSTREAM,
        description="Direction of traversal ('downstream' or 'upstream')",
    )
    max_depth: Optional[int] = Field(
        default=None,
        ge=1,
        description="Optional maximum hop limit for traversal",
    )

    @field_validator("node_id")
    @classmethod
    def validate_node_id(cls, value: str) -> str:
        # Strip whitespace and reject empty string
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("node_id cannot be blank or empty whitespace.")
        return cleaned


class TraversalResponseSchema(BaseModel):
    """
    Response schema returned by the graph traversal service.

    Why this exists:
    Provides a standardized contract for Preetam's BFS algorithm output so that
    the frontend demo can highlight the impacted blast-radius path in the UI.

    Canonical contract example:
    {
      "source_node": "SUP-01",
      "direction": "downstream",
      "visited_nodes": ["PART-01", "PROD-01", "ORD-01"],
      "total_nodes": 3
    }
    """
    model_config = ConfigDict(populate_by_name=True)

    source_node: str = Field(..., description="Root node ID from which traversal was executed")
    direction: str = Field(default="downstream", description="Traversal direction executed")
    visited_nodes: List[str] = Field(default_factory=list, description="Ordered list of visited descendant node IDs")
    total_nodes: int = Field(default=0, ge=0, description="Total count of impacted visited nodes")
    paths: Optional[List[List[str]]] = Field(
        default=None,
        description="Detailed traversal paths from source to leaf nodes",
    )
    blast_radius_by_tier: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Impacted nodes categorized by tier (parts, products, orders)",
    )
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Algorithm execution duration in milliseconds (target < 10ms SLA)",
    )
