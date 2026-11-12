from typing import Any, Dict, List, Optional, Set, Union

from backend.app.core.constants import EdgeType, TierType
from backend.app.core.exceptions import InvalidEdgeError, ModelValidationError
from backend.app.models.edges import (
    BaseEdge,
    FulfillsEdge,
    SuppliesEdge,
    UsedInEdge,
    create_edge,
)
from backend.app.models.nodes import (
    BaseNode,
    BOMPartNode,
    CustomerOrderNode,
    FinishedProductNode,
    SupplierNode,
    create_node,
)


class SupplyChainGraph:
    """
    In-memory domain model representing the multi-tier supply chain network.

    Why this class exists:
    This class holds the business entities (suppliers, parts, products, orders)
    and their connections independently from any external graph library like NetworkX.
    This separates domain logic from algorithm execution.
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.metadata: Dict[str, Any] = metadata or {}
        # Node storage: dictionary mapping node_id -> BaseNode instance
        self._nodes: Dict[str, BaseNode] = {}
        # Edge storage: list and set of BaseEdge instances
        self._edges: List[BaseEdge] = []
        self._edge_set: Set[BaseEdge] = set()
        # Adjacency maps for fast O(1) neighbor lookups
        self._adjacency_out: Dict[str, List[BaseEdge]] = {}
        self._adjacency_in: Dict[str, List[BaseEdge]] = {}

    # -------------------------------------------------------------------------
    # Node Management
    # -------------------------------------------------------------------------

    def add_node(self, node: BaseNode) -> None:
        """
        Add a domain node to the graph.
        Rejects duplicate node IDs to ensure graph integrity.
        """
        if not isinstance(node, BaseNode):
            raise ModelValidationError(f"Expected BaseNode instance, got {type(node).__name__}")

        if node.id in self._nodes:
            raise ModelValidationError(
                f"Duplicate node ID detected: '{node.id}' already exists in graph.",
                field="id",
            )

        self._nodes[node.id] = node
        self._adjacency_out.setdefault(node.id, [])
        self._adjacency_in.setdefault(node.id, [])

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        """Look up a node by its ID. Returns None if node is not found."""
        return self._nodes.get(node_id)

    def has_node(self, node_id: str) -> bool:
        """Check whether a node exists in the graph."""
        return node_id in self._nodes

    def get_nodes_by_tier(self, tier: Union[TierType, str]) -> List[BaseNode]:
        """Return all nodes belonging to a specific tier."""
        resolved_tier = TierType.from_str(tier) if isinstance(tier, str) else tier
        return [node for node in self._nodes.values() if node.tier == resolved_tier]

    @property
    def suppliers(self) -> List[SupplierNode]:
        """All Tier 1 Supplier nodes."""
        return [node for node in self._nodes.values() if isinstance(node, SupplierNode)]

    @property
    def parts(self) -> List[BOMPartNode]:
        """All Tier 2 BOM Part nodes."""
        return [node for node in self._nodes.values() if isinstance(node, BOMPartNode)]

    @property
    def products(self) -> List[FinishedProductNode]:
        """All Tier 3 Finished Product nodes."""
        return [node for node in self._nodes.values() if isinstance(node, FinishedProductNode)]

    @property
    def orders(self) -> List[CustomerOrderNode]:
        """All Tier 4 Customer Order nodes."""
        return [node for node in self._nodes.values() if isinstance(node, CustomerOrderNode)]

    @property
    def nodes(self) -> List[BaseNode]:
        """List of all domain nodes in the graph."""
        return list(self._nodes.values())

    @property
    def node_count(self) -> int:
        """Total number of nodes."""
        return len(self._nodes)

    # -------------------------------------------------------------------------
    # Edge Management
    # -------------------------------------------------------------------------

    def add_edge(self, edge: BaseEdge, validate_nodes: bool = False) -> None:
        """
        Add a directed edge to the graph.

        If validate_nodes is True, confirms that both endpoint nodes exist
        in this graph and satisfy tier transition rules.
        """
        if not isinstance(edge, BaseEdge):
            raise InvalidEdgeError(f"Expected BaseEdge instance, got {type(edge).__name__}")

        if validate_nodes:
            source_node = self.get_node(edge.source)
            target_node = self.get_node(edge.target)
            if not source_node:
                raise InvalidEdgeError(f"Edge source node '{edge.source}' does not exist in graph.", source=edge.source)
            if not target_node:
                raise InvalidEdgeError(f"Edge target node '{edge.target}' does not exist in graph.", target=edge.target)
            edge.validate_endpoints(source_node, target_node)

        # Ignore duplicate edges idempotently
        if edge in self._edge_set:
            return

        self._edges.append(edge)
        self._edge_set.add(edge)
        self._adjacency_out.setdefault(edge.source, []).append(edge)
        self._adjacency_in.setdefault(edge.target, []).append(edge)

    def get_edges(self, relation: Optional[Union[EdgeType, str]] = None) -> List[BaseEdge]:
        """Retrieve all edges, optionally filtered by relationship type."""
        if relation is None:
            return list(self._edges)
        resolved_rel = EdgeType.from_str(relation) if isinstance(relation, str) else relation
        return [edge for edge in self._edges if edge.relation == resolved_rel]

    @property
    def supplies_edges(self) -> List[SuppliesEdge]:
        """All SUPPLIES edges."""
        return [edge for edge in self._edges if isinstance(edge, SuppliesEdge)]

    @property
    def used_in_edges(self) -> List[UsedInEdge]:
        """All USED_IN edges."""
        return [edge for edge in self._edges if isinstance(edge, UsedInEdge)]

    @property
    def fulfills_edges(self) -> List[FulfillsEdge]:
        """All FULFILLS edges."""
        return [edge for edge in self._edges if isinstance(edge, FulfillsEdge)]

    @property
    def edges(self) -> List[BaseEdge]:
        """List of all directed edges."""
        return list(self._edges)

    @property
    def edge_count(self) -> int:
        """Total number of directed edges."""
        return len(self._edges)

    # -------------------------------------------------------------------------
    # Graph Traversal Helpers
    # -------------------------------------------------------------------------

    def get_out_edges(self, node_id: str) -> List[BaseEdge]:
        """Return all outgoing directed edges starting from node_id."""
        return self._adjacency_out.get(node_id, [])

    def get_in_edges(self, node_id: str) -> List[BaseEdge]:
        """Return all incoming directed edges pointing to node_id."""
        return self._adjacency_in.get(node_id, [])

    def get_successors(self, node_id: str) -> List[str]:
        """Return direct downstream target node IDs."""
        return [edge.target for edge in self.get_out_edges(node_id)]

    def get_predecessors(self, node_id: str) -> List[str]:
        """Return direct upstream source node IDs."""
        return [edge.source for edge in self.get_in_edges(node_id)]

    # -------------------------------------------------------------------------
    # Serialization and Statistics
    # -------------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Generate high-level counts and topological statistics."""
        return {
            "total_nodes": self.node_count,
            "total_edges": self.edge_count,
            "node_counts": {
                "suppliers": len(self.suppliers),
                "parts": len(self.parts),
                "products": len(self.products),
                "orders": len(self.orders),
            },
            "edge_counts": {
                "supplies": len(self.supplies_edges),
                "used_in": len(self.used_in_edges),
                "fulfills": len(self.fulfills_edges),
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete domain graph into a canonical dictionary."""
        return {
            "metadata": self.metadata,
            "summary": self.summary(),
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SupplyChainGraph":
        """
        Build a SupplyChainGraph instance from raw scenario JSON or normalized dictionary.

        Supports two common data formats:
        1. Categorized nested dictionaries: {"nodes": {"suppliers": [...], "parts": [...]}}
        2. Flat list format: {"nodes": [{"id": "..."}, ...]}
        """
        metadata = data.get("metadata", {})
        graph = cls(metadata=metadata)

        # Parse nodes
        raw_nodes = data.get("nodes", {})
        if isinstance(raw_nodes, dict):
            # Nested format by tier
            for tier_nodes in raw_nodes.values():
                if isinstance(tier_nodes, list):
                    for node_item in tier_nodes:
                        graph.add_node(create_node(node_item))
        elif isinstance(raw_nodes, list):
            # Flat list of nodes
            for node_item in raw_nodes:
                graph.add_node(create_node(node_item))

        # Parse edges
        raw_edges = data.get("edges", {})
        if isinstance(raw_edges, dict):
            # Nested format by relationship
            for relation_edges in raw_edges.values():
                if isinstance(relation_edges, list):
                    for edge_item in relation_edges:
                        graph.add_edge(create_edge(edge_item))
        elif isinstance(raw_edges, list):
            # Flat list of edges
            for edge_item in raw_edges:
                graph.add_edge(create_edge(edge_item))

        return graph
