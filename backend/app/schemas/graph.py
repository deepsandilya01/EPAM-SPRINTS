from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NodeResponseSchema(BaseModel):
    """
    Schema for an individual graph node in API responses.

    Why this exists:
    Guarantees that the frontend receives uniform node data across all 4 tiers,
    including identifier, display name, tier name, and custom attributes.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Unique node identifier (e.g. 'SUP-01', 'PART-01')")
    name: str = Field(..., description="Display name of the node")
    tier: str = Field(..., description="Supply chain tier ('supplier', 'part', 'product', 'order')")
    kind: Optional[str] = Field(None, description="Alias for tier matching scenario dataset format")
    label: Optional[str] = Field(None, description="Human-readable node label")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Tier-specific domain attributes")


class EdgeResponseSchema(BaseModel):
    """
    Schema for an individual directed edge in API responses.

    Why this exists:
    Represents dependencies between nodes so that the visualization demo can
    draw directed arrows between connected entities.
    """
    model_config = ConfigDict(populate_by_name=True)

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relation: str = Field(..., description="Relationship type ('SUPPLIES', 'USED_IN', 'FULFILLS')")
    relationship_type: Optional[str] = Field(None, description="Alias for relation")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata (lead time, capacity, etc.)")


class GraphSummarySchema(BaseModel):
    """
    High-level statistics about the supply chain network.

    Why this exists:
    Provides immediate KPI counters (total nodes, total edges, counts per tier)
    for dashboard summary cards without needing to iterate all elements.
    """
    total_nodes: int = Field(..., description="Total count of nodes across all tiers")
    total_edges: int = Field(..., description="Total count of directed edges")
    node_counts: Dict[str, int] = Field(default_factory=dict, description="Node counts broken down by tier")
    edge_counts: Dict[str, int] = Field(default_factory=dict, description="Edge counts broken down by relation")


class GraphResponseSchema(BaseModel):
    """
    Complete graph payload returned by the GET /api/graph endpoint.

    Contains summary statistics, the full list of nodes, and all directed edges.
    """
    summary: GraphSummarySchema = Field(..., description="Graph metrics summary")
    nodes: List[NodeResponseSchema] = Field(..., description="Complete list of nodes")
    edges: List[EdgeResponseSchema] = Field(..., description="Complete list of directed edges")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Project and scenario metadata")


class GraphFilterParamsSchema(BaseModel):
    """
    Query parameter schema for filtering graph elements in GET /api/graph requests.
    Example: /api/graph?tier=supplier&relation=SUPPLIES
    """
    tier: Optional[str] = Field(None, description="Filter nodes by tier (e.g. 'supplier', 'part')")
    relation: Optional[str] = Field(None, description="Filter edges by relationship type (e.g. 'SUPPLIES')")
