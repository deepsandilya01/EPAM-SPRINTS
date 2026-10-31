"""
Unit tests for RE:Flow Graph Domain Models (Sprint 1 domain entity layer).
Tests cover:
- Valid and invalid node creation across all 4 tiers
- Valid and invalid edge types, self-loops, and tier transition verification
- SupplyChainGraph in-memory container operations, queries, and serialization
- Canonical baseline scenario dataset compatibility (19 nodes, 21 edges)
"""

import json
import subprocess

import pytest

from backend.app.core.constants import EdgeType, TierType
from backend.app.core.exceptions import InvalidEdgeError, ModelValidationError
from backend.app.models.edges import (
    FulfillsEdge,
    SuppliesEdge,
    UsedInEdge,
    create_edge,
)
from backend.app.models.graph import SupplyChainGraph
from backend.app.models.nodes import (
    BOMPartNode,
    CustomerOrderNode,
    FinishedProductNode,
    SupplierNode,
    create_node,
)

# =============================================================================
# 1. Node Domain Model Tests
# =============================================================================

class TestNodeModels:
    def test_supplier_node_creation_valid(self):
        supplier = SupplierNode(
            id="SUP-01",
            tier=TierType.SUPPLIER,
            name="Apex Components",
            location="Pune",
            note="Primary electronics vendor",
        )
        assert supplier.id == "SUP-01"
        assert supplier.tier == TierType.SUPPLIER
        assert supplier.name == "Apex Components"
        assert supplier.location == "Pune"
        assert supplier.note == "Primary electronics vendor"
        assert supplier.label == "Apex Components"

        d = supplier.to_dict()
        assert d["id"] == "SUP-01"
        assert d["tier"] == "supplier"
        assert d["location"] == "Pune"

    def test_bom_part_node_creation_valid(self):
        part = BOMPartNode(
            id="PART-01",
            tier=TierType.BOM_PART,
            name="Control Board",
            stock_on_hand=120,
            daily_consumption=20,
        )
        assert part.id == "PART-01"
        assert part.stock_on_hand == 120
        assert part.daily_consumption == 20
        # Automatically calculated: 120 / 20 = 6.0
        assert part.days_of_supply == 6.0

        d = part.to_dict()
        assert d["stock_on_hand"] == 120
        assert d["days_of_supply"] == 6.0

    def test_finished_product_node_creation_valid(self):
        prod = FinishedProductNode(
            id="PROD-01",
            tier=TierType.FINISHED_PRODUCT,
            name="Smart Controller Unit",
            parts_needed="PART-01 x1, PART-02 x1",
        )
        assert prod.id == "PROD-01"
        assert prod.parts_needed == "PART-01 x1, PART-02 x1"
        assert prod.to_dict()["parts_needed"] == "PART-01 x1, PART-02 x1"

    def test_customer_order_node_creation_valid(self):
        order = CustomerOrderNode(
            id="ORD-01",
            tier=TierType.CUSTOMER_ORDER,
            name="Order ORD-01 (Meridian Retail)",
            customer="Meridian Retail",
            product_id="PROD-01",
            quantity=40,
            deadline="2026-11-05",
        )
        assert order.id == "ORD-01"
        assert order.customer == "Meridian Retail"
        assert order.quantity == 40
        assert order.deadline == "2026-11-05"

    def test_node_validation_empty_id(self):
        with pytest.raises(ModelValidationError) as exc:
            SupplierNode(id="   ", tier=TierType.SUPPLIER, name="Invalid")
        assert "Node ID must be a non-empty string" in str(exc.value)

    def test_node_validation_empty_name(self):
        with pytest.raises(ModelValidationError) as exc:
            SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="")
        assert "Node name must be a non-empty string" in str(exc.value)

    def test_bom_part_negative_values(self):
        with pytest.raises(ModelValidationError):
            BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Part", stock_on_hand=-10)
        with pytest.raises(ModelValidationError):
            BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Part", daily_consumption=-5)

    def test_customer_order_zero_or_negative_quantity(self):
        with pytest.raises(ModelValidationError):
            CustomerOrderNode(
                id="ORD-01",
                tier=TierType.CUSTOMER_ORDER,
                name="Order",
                customer="Client",
                quantity=0,
            )
        with pytest.raises(ModelValidationError):
            CustomerOrderNode(
                id="ORD-01",
                tier=TierType.CUSTOMER_ORDER,
                name="Order",
                customer="Client",
                quantity=-5,
            )

    def test_create_node_factory_variants(self):
        # Factory with raw dictionary and prefix inference
        n1 = create_node({"id": "SUP-01", "name": "Vendor A", "location": "Pune"})
        assert isinstance(n1, SupplierNode)
        assert n1.location == "Pune"

        n2 = create_node({"part_id": "PART-02", "name": "Battery", "stock_on_hand": 200, "daily_consumption": 25})
        assert isinstance(n2, BOMPartNode)
        assert n2.days_of_supply == 8.0

        n3 = create_node({"product_id": "PROD-01", "name": "Controller", "parts_needed": "PART-01"})
        assert isinstance(n3, FinishedProductNode)

        n4 = create_node({"order_id": "ORD-01", "name": "Order 1", "customer": "Cust", "quantity": 10, "deadline": "2026-11-01"})
        assert isinstance(n4, CustomerOrderNode)


# =============================================================================
# 2. Edge Domain Model Tests
# =============================================================================

class TestEdgeModels:
    def test_supplies_edge_valid(self):
        edge = SuppliesEdge(
            source="SUP-01",
            target="PART-01",
            relation=EdgeType.SUPPLIES,
            lead_time_hours=24,
            max_capacity_units_per_day=100,
        )
        assert edge.source == "SUP-01"
        assert edge.target == "PART-01"
        assert edge.relation == EdgeType.SUPPLIES
        assert edge.lead_time_hours == 24
        assert edge.max_capacity_units_per_day == 100

        d = edge.to_dict()
        assert d["source"] == "SUP-01"
        assert d["relation"] == "SUPPLIES"
        assert d["lead_time_hours"] == 24

    def test_used_in_edge_valid(self):
        edge = UsedInEdge(
            source="PART-01",
            target="PROD-01",
            relation=EdgeType.USED_IN,
            quantity_per_unit=2,
        )
        assert edge.source == "PART-01"
        assert edge.target == "PROD-01"
        assert edge.quantity_per_unit == 2
        assert edge.to_dict()["quantity_per_unit"] == 2

    def test_fulfills_edge_valid(self):
        edge = FulfillsEdge(
            source="PROD-01",
            target="ORD-01",
            relation=EdgeType.FULFILLS,
        )
        assert edge.source == "PROD-01"
        assert edge.target == "ORD-01"
        assert edge.relation == EdgeType.FULFILLS

    def test_edge_self_loop_forbidden(self):
        with pytest.raises(InvalidEdgeError) as exc:
            SuppliesEdge(source="SUP-01", target="SUP-01", relation=EdgeType.SUPPLIES)
        assert "Self-loops are forbidden" in str(exc.value)

    def test_edge_empty_endpoints(self):
        with pytest.raises(InvalidEdgeError):
            SuppliesEdge(source="", target="PART-01", relation=EdgeType.SUPPLIES)
        with pytest.raises(InvalidEdgeError):
            SuppliesEdge(source="SUP-01", target="", relation=EdgeType.SUPPLIES)

    def test_edge_endpoint_tier_validation(self):
        sup = SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Supplier")
        part = BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Part", stock_on_hand=10, daily_consumption=1)
        prod = FinishedProductNode(id="PROD-01", tier=TierType.FINISHED_PRODUCT, name="Product")

        valid_edge = SuppliesEdge(source="SUP-01", target="PART-01", relation=EdgeType.SUPPLIES)
        # Valid tier transition: Supplier -> Part
        valid_edge.validate_endpoints(sup, part)

        # Illegal tier jump: Supplier -> Product
        illegal_jump_edge = SuppliesEdge(source="SUP-01", target="PROD-01", relation=EdgeType.SUPPLIES)
        with pytest.raises(InvalidEdgeError) as exc:
            illegal_jump_edge.validate_endpoints(sup, prod)
        assert "Illegal tier jump" in str(exc.value)

    def test_create_edge_factory(self):
        e1 = create_edge({"from_supplier": "SUP-01", "to_part": "PART-01", "lead_time_hours": 12})
        assert isinstance(e1, SuppliesEdge)
        assert e1.relation == EdgeType.SUPPLIES
        assert e1.lead_time_hours == 12

        e2 = create_edge({"source": "PART-01", "target": "PROD-01", "relation": "USED_IN", "quantity_per_unit": 2})
        assert isinstance(e2, UsedInEdge)
        assert e2.quantity_per_unit == 2

        e3 = create_edge({"source": "PROD-01", "target": "ORD-01", "relation": "FULFILLS"})
        assert isinstance(e3, FulfillsEdge)


# =============================================================================
# 3. SupplyChainGraph Domain Container Tests
# =============================================================================

class TestSupplyChainGraph:
    def test_graph_add_nodes_and_queries(self):
        graph = SupplyChainGraph(metadata={"name": "Test Network"})
        sup = SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Supplier 1")
        part = BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Part 1", stock_on_hand=50, daily_consumption=10)
        prod = FinishedProductNode(id="PROD-01", tier=TierType.FINISHED_PRODUCT, name="Product 1")
        order = CustomerOrderNode(id="ORD-01", tier=TierType.CUSTOMER_ORDER, name="Order 1", quantity=5)

        graph.add_node(sup)
        graph.add_node(part)
        graph.add_node(prod)
        graph.add_node(order)

        assert graph.node_count == 4
        assert graph.has_node("SUP-01") is True
        assert graph.has_node("NON-EXISTENT") is False
        assert graph.get_node("SUP-01") == sup

        assert len(graph.suppliers) == 1
        assert len(graph.parts) == 1
        assert len(graph.products) == 1
        assert len(graph.orders) == 1

    def test_graph_duplicate_node_id_rejected(self):
        graph = SupplyChainGraph()
        graph.add_node(SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Supplier 1"))
        with pytest.raises(ModelValidationError) as exc:
            graph.add_node(SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Duplicate Supplier"))
        assert "Duplicate node ID" in str(exc.value)

    def test_graph_edge_connectivity(self):
        graph = SupplyChainGraph()
        sup = SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Sup")
        part = BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Part")
        prod = FinishedProductNode(id="PROD-01", tier=TierType.FINISHED_PRODUCT, name="Prod")

        graph.add_node(sup)
        graph.add_node(part)
        graph.add_node(prod)

        e1 = SuppliesEdge(source="SUP-01", target="PART-01", relation=EdgeType.SUPPLIES)
        e2 = UsedInEdge(source="PART-01", target="PROD-01", relation=EdgeType.USED_IN)

        graph.add_edge(e1)
        graph.add_edge(e2)

        assert graph.edge_count == 2
        assert len(graph.supplies_edges) == 1
        assert len(graph.used_in_edges) == 1

        assert graph.get_successors("SUP-01") == ["PART-01"]
        assert graph.get_predecessors("PART-01") == ["SUP-01"]
        assert graph.get_successors("PART-01") == ["PROD-01"]

    def test_graph_serialization_roundtrip(self):
        graph = SupplyChainGraph(metadata={"project": "RE:Flow"})
        graph.add_node(SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Apex Components", location="Pune"))
        graph.add_node(BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Control Board", stock_on_hand=100, daily_consumption=20))
        graph.add_edge(SuppliesEdge(source="SUP-01", target="PART-01", relation=EdgeType.SUPPLIES, lead_time_hours=24))

        serialized = graph.to_dict()
        assert serialized["summary"]["total_nodes"] == 2
        assert serialized["summary"]["total_edges"] == 1

        # Reconstruct graph from serialized dictionary
        reconstructed = SupplyChainGraph.from_dict(serialized)
        assert reconstructed.node_count == 2
        assert reconstructed.edge_count == 1
        assert reconstructed.has_node("SUP-01")
        assert reconstructed.has_node("PART-01")

    def test_canonical_dataset_loading_compatibility(self):
        # Load the approved baseline scenario dataset from git history
        out = subprocess.check_output(['git', 'show', 'a7943b0:data/photon_sprint1_graph_data.json']).decode('utf-8')
        dataset = json.loads(out)

        graph = SupplyChainGraph.from_dict(dataset)
        assert graph.node_count == 19
        assert graph.edge_count == 21
        assert len(graph.suppliers) == 2
        assert len(graph.parts) == 5
        assert len(graph.products) == 2
        assert len(graph.orders) == 10
        assert len(graph.supplies_edges) == 6
        assert len(graph.used_in_edges) == 5
        assert len(graph.fulfills_edges) == 10
