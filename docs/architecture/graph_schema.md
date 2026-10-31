# Graph Schema Specification — RE:Flow

> **Sprint 1 Ownership & Task Assignment**
> - **Ownership**: Team Maintained (Implemented by Deep during Sprint 1)
> - **Role**: Graph Domain Models and Data Contracts
> - **File**: `docs/architecture/graph_schema.md`
> - **Status**: COMPLETED / ACTIVE
> - **Last Updated**: 2026-10-31

---

## 1. Purpose of the Graph Schema

RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.

The **RE:Flow Graph Schema** establishes the canonical topological data contract and domain modeling foundation for representing multi-tier supply chain dependency networks. 

The primary objectives of this schema are:
1. **Topological Invariant Enforcement**: Enforce a strict Directed Acyclic Graph (DAG) structure that models the physical progression from Tier-1 suppliers down to customer purchase orders.
2. **Contract Decoupling**: Decouple raw JSON storage formats and NetworkX execution algorithms from internal domain models (`backend/app/models/`) and REST API serialization contracts (`backend/app/schemas/`).
3. **Multi-Tier Interoperability**: Provide a shared, type-safe interface for all Sprint 1 module owners (Aadee for data loading, Ansh for graph building, Preetam for BFS traversal, and Soumya for graph validation).

---

## 2. Node Types and Responsibilities

The RE:Flow graph models four sequential supply chain tiers:

| Tier | Domain Class | Constant Enum | ID Prefix Pattern | Responsibility in Network |
|:---:|---|---|---|---|
| **Tier 1** | `SupplierNode` | `TierType.SUPPLIER` (`"supplier"`) | `SUP-XX` | Upstream component/raw material vendors. Roots of the dependency graph (in-degree = 0). |
| **Tier 2** | `BOMPartNode` | `TierType.BOM_PART` (`"part"`) | `PART-XX` | Bill of Materials (BOM) components with stock on hand and daily burn rates. |
| **Tier 3** | `FinishedProductNode` | `TierType.FINISHED_PRODUCT` (`"product"`) | `PROD-XX` | Manufactured assemblies assembled from BOM parts. |
| **Tier 4** | `CustomerOrderNode` | `TierType.CUSTOMER_ORDER` (`"order"`) | `ORD-XX` | Downstream customer demand with quantities and fulfillment deadlines. Sinks of the graph (out-degree = 0). |

---

## 3. Edge Types and Relationship Directions

Edges in RE:Flow are strictly directed and follow the physical material and demand flow.

$$\text{Supplier} \xrightarrow{\text{SUPPLIES}} \text{BOM Part} \xrightarrow{\text{USED_IN}} \text{Finished Product} \xrightarrow{\text{FULFILLS}} \text{Customer Order}$$

| Relationship Type | Domain Class | Source Tier | Target Tier | Semantics & Multiplicity |
|---|---|:---:|:---:|---|
| `SUPPLIES` | `SuppliesEdge` | Tier 1 (Supplier) | Tier 2 (BOM Part) | Supplier delivers components with lead-time and daily capacity constraints. Many-to-Many. |
| `USED_IN` | `UsedInEdge` | Tier 2 (BOM Part) | Tier 3 (Product) | Part is consumed in assembling a finished product with bill-of-materials unit ratio. Many-to-Many. |
| `FULFILLS` | `FulfillsEdge` | Tier 3 (Product) | Tier 4 (Order) | Product allocation fulfills a customer order. One-to-Many. |

### Forbidden Transitions
- **Self-loops**: Any edge where `source == target` is strictly prohibited.
- **Backward Edges**: Any edge flowing from a higher tier to a lower tier (e.g. `Order -> Product`) is prohibited.
- **Skipping Edges**: Direct jumps (e.g. `Supplier -> Product` or `Supplier -> Order`) bypass intermediate tiers and violate domain validation rules.

---

## 4. Node and Edge Attributes

### A. Node Attributes

#### 1. SupplierNode (`TierType.SUPPLIER`)
- `id` (`str`): Unique identifier (e.g. `"SUP-01"`).
- `name` (`str`): Legal vendor name (e.g. `"Apex Components"`).
- `location` (`str`): Geographic origin/city (e.g. `"Pune"`, `"Indore"`).
- `note` (`Optional[str]`): Operational category or vendor note.
- `label` (`str`): UI display label.

#### 2. BOMPartNode (`TierType.BOM_PART`)
- `id` (`str`): Unique part identifier (e.g. `"PART-01"`).
- `name` (`str`): Component name (e.g. `"Control Board"`).
- `stock_on_hand` (`int`): Quantity currently in warehouse inventory ($\ge 0$).
- `daily_consumption` (`int`): Units consumed per operating day ($\ge 0$).
- `days_of_supply` (`float`): Metric computed as $\text{stock\_on\_hand} / \text{daily\_consumption}$ ($\ge 0.0$).
- `label` (`str`): UI display label.

#### 3. FinishedProductNode (`TierType.FINISHED_PRODUCT`)
- `id` (`str`): Product identifier (e.g. `"PROD-01"`).
- `name` (`str`): Product name (e.g. `"Smart Controller Unit"`).
- `parts_needed` (`Optional[str]`): Textual bill-of-materials breakdown (e.g. `"PART-01 x1, PART-02 x1, PART-05 x2"`).
- `label` (`str`): UI display label.

#### 4. CustomerOrderNode (`TierType.CUSTOMER_ORDER`)
- `id` (`str`): Order identifier (e.g. `"ORD-01"`).
- `customer` (`str`): Customer or client company name (e.g. `"Meridian Retail"`).
- `product_id` (`str`): Referenced target finished product ID (e.g. `"PROD-01"`).
- `quantity` (`int`): Number of product units ordered ($> 0$).
- `deadline` (`str`): Promised delivery date in ISO 8601 format (`YYYY-MM-DD`).
- `label` (`str`): UI display label.

### B. Edge Attributes

#### 1. SuppliesEdge (`EdgeType.SUPPLIES`)
- `source` (`str`): Supplier node ID.
- `target` (`str`): BOM Part node ID.
- `relation` (`EdgeType.SUPPLIES`): `"SUPPLIES"`.
- `lead_time_hours` (`Optional[int]`): Fulfillment delivery lead-time in hours ($\ge 0$).
- `max_capacity_units_per_day` (`Optional[int]`): Maximum vendor output volume ($\ge 0$).

#### 2. UsedInEdge (`EdgeType.USED_IN`)
- `source` (`str`): BOM Part node ID.
- `target` (`str`): Finished Product node ID.
- `relation` (`EdgeType.USED_IN`): `"USED_IN"`.
- `quantity_per_unit` (`int`): Units of part required per unit of finished product ($\ge 1$).

#### 3. FulfillsEdge (`EdgeType.FULFILLS`)
- `source` (`str`): Finished Product node ID.
- `target` (`str`): Customer Order node ID.
- `relation` (`EdgeType.FULFILLS`): `"FULFILLS"`.

---

## 5. Graph Structure and Baseline Metrics

The Sprint 1 canonical baseline scenario dataset contains:

```text
       [ 2 Suppliers ]          (Tier 1: SUP-01, SUP-02)
              │
              ▼  (6 SUPPLIES edges)
       [ 5 BOM Parts ]          (Tier 2: PART-01 ... PART-05)
              │
              ▼  (5 USED_IN edges)
    [ 2 Finished Products ]     (Tier 3: PROD-01, PROD-02)
              │
              ▼  (10 FULFILLS edges)
     [ 10 Customer Orders ]     (Tier 4: ORD-01 ... ORD-10)
```

- **Total Canonical Nodes**: 19 nodes
- **Total Canonical Edges**: 21 directed edges
- **Graph Topology**: Directed Acyclic Graph (DAG) with 0 cycles and topological ordering:
  $$\text{Tier 1} \to \text{Tier 2} \to \text{Tier 3} \to \text{Tier 4}$$

---

## 6. Dataset-to-Model Mapping

The domain model loader in `SupplyChainGraph.from_dict()` transparently accepts both:

1. **Nested Canonical Scenario Dataset** (`data/raw/scenario_dataset.json`):
   ```json
   {
     "metadata": { ... },
     "nodes": {
       "suppliers": [ { "id": "SUP-01", ... } ],
       "parts": [ { "id": "PART-01", ... } ],
       "products": [ { "id": "PROD-01", ... } ],
       "orders": [ { "id": "ORD-01", ... } ]
     },
     "edges": {
       "supplies": [ { "source": "SUP-01", "target": "PART-01", ... } ],
       "used_in": [ { "source": "PART-01", "target": "PROD-01", ... } ],
       "fulfills": [ { "source": "PROD-01", "target": "ORD-01", ... } ]
     }
   }
   ```
2. **Flat List Representation**:
   ```json
   {
     "nodes": [ { "id": "SUP-01", "tier": "supplier", ... } ],
     "edges": [ { "source": "SUP-01", "target": "PART-01", "relation": "SUPPLIES" } ]
   }
   ```

`create_node()` automatically normalizes key aliases (`supplier_id`, `part_id`, `product_id`, `order_id` $\to$ `id`), infers tiers from prefixes if omitted, and casts numeric constraints safely.

---

## 7. API Schema Relationship

The REST API contracts defined in `backend/app/schemas/` mirror and wrap domain entities for HTTP serialization:

```
Domain Layer (app.models)       API Serialization Layer (app.schemas)
─────────────────────────       ────────────────────────────────────
BaseNode                        NodeResponseSchema
BaseEdge                        EdgeResponseSchema
SupplyChainGraph                GraphResponseSchema (with GraphSummarySchema)
(Downstream BFS Result)         TraversalResponseSchema (from TraversalRequestSchema)
(Validation Audit Result)       ValidationResponseSchema (with ValidationErrorItemSchema)
```

Every response schema includes Pydantic v2 `model_validate()` and `.model_dump()` support, guaranteeing clean serialization into Flask `jsonify()`.

---

## 8. Validation Rules

1. **DAG Acyclicity**: The network must have zero directed cycles ($\text{Cycles} = \emptyset$).
2. **ID Uniqueness**: All node IDs across all tiers must be mutually exclusive.
3. **Endpoint Existence**: Every edge `source` and `target` must resolve to an existing node ID.
4. **Strict Tier Transition**: Edges must connect adjacent tiers only according to `ALLOWED_TRANSITIONS`.
5. **Positive Quantities**: Order quantities and BOM consumption ratios must be strictly $> 0$.
6. **Non-Negative Stock**: Inventory counts must be $\ge 0$.

---

## 9. Example Graph Representation

```json
{
  "summary": {
    "total_nodes": 19,
    "total_edges": 21,
    "node_counts": { "suppliers": 2, "parts": 5, "products": 2, "orders": 10 },
    "edge_counts": { "supplies": 6, "used_in": 5, "fulfills": 10 }
  },
  "nodes": [
    { "id": "SUP-01", "name": "Apex Components", "tier": "supplier", "location": "Pune" },
    { "id": "PART-01", "name": "Control Board", "tier": "part", "stock_on_hand": 120, "daily_consumption": 20, "days_of_supply": 6.0 },
    { "id": "PROD-01", "name": "Smart Controller Unit", "tier": "product", "parts_needed": "PART-01 x1, PART-02 x1, PART-05 x2" },
    { "id": "ORD-01", "name": "Order ORD-01 (Meridian Retail)", "tier": "order", "customer": "Meridian Retail", "product_id": "PROD-01", "quantity": 40, "deadline": "2026-11-05" }
  ],
  "edges": [
    { "source": "SUP-01", "target": "PART-01", "relation": "SUPPLIES", "lead_time_hours": 24, "max_capacity_units_per_day": 100 },
    { "source": "PART-01", "target": "PROD-01", "relation": "USED_IN", "quantity_per_unit": 1 },
    { "source": "PROD-01", "target": "ORD-01", "relation": "FULFILLS" }
  ]
}
```

---

## 10. Integration Guidance for Dependent Team Members

### For Anushka (`data/raw/scenario_dataset.json`):
- Ensure dataset keys match `data/schemas/graph_schema.json`.
- Keep tier arrays under `nodes.suppliers`, `nodes.parts`, `nodes.products`, `nodes.orders`.
- Keep edge arrays under `edges.supplies`, `edges.used_in`, `edges.fulfills`.

### For Aadee (`backend/app/data/`):
- In `normalizer.py`, invoke `create_node(record)` and `create_edge(record)` to obtain validated domain entities.
- In `repository.py`, instantiate `SupplyChainGraph.from_dict(raw_json)` to cache the complete in-memory domain representation.

### For Ansh (`backend/app/graph/`):
- When building NetworkX `DiGraph`, iterate `graph.nodes`:
  ```python
  for node in domain_graph.nodes:
      nx_graph.add_node(node.id, **node.to_dict())
  for edge in domain_graph.edges:
      nx_graph.add_edge(edge.source, edge.target, **edge.to_dict())
  ```
- Use `node.tier` to color-code or categorize swimlanes.

### For Preetam (`backend/app/graph/traversal.py` & `routes/traversal.py`):
- Parse incoming POST body using `TraversalRequestSchema.model_validate(request.get_json())`.
- Return results formatted using `TraversalResponseSchema(source_node=..., visited_nodes=..., total_nodes=..., execution_time_ms=...)`.
- Validate starting node existence via `domain_graph.has_node(req.node_id)`; raise `NodeNotFoundError` if missing.

### For Soumya (`backend/app/validation/`):
- Use `ALLOWED_TRANSITIONS` from `backend.app.core.constants` in `edge_validator.py`.
- Format final audit reports using `ValidationResponseSchema` and `ValidationErrorItemSchema`.

---

## 11. Implementation State Matrix

| Feature | Classification | Implemented Location |
|---|---|---|
| Domain Models (`BaseNode`, `SupplierNode`, `BOMPartNode`, etc.) | **IMPLEMENTED** | `backend/app/models/nodes.py` |
| Edge Models (`BaseEdge`, `SuppliesEdge`, `UsedInEdge`, `FulfillsEdge`) | **IMPLEMENTED** | `backend/app/models/edges.py` |
| Graph Container (`SupplyChainGraph`) | **IMPLEMENTED** | `backend/app/models/graph.py` |
| Graph API Schemas (`GraphResponseSchema`, `NodeResponseSchema`, etc.) | **IMPLEMENTED** | `backend/app/schemas/graph.py` |
| Traversal API Schemas (`TraversalRequestSchema`, `TraversalResponseSchema`) | **IMPLEMENTED** | `backend/app/schemas/traversal.py` |
| Validation API Schemas (`ValidationResponseSchema`, etc.) | **IMPLEMENTED** | `backend/app/schemas/validation.py` |
| Canonical JSON Schema | **IMPLEMENTED** | `data/schemas/graph_schema.json` |
| NetworkX Graph Construction | Approved Requirement | Owned by Ansh (`backend/app/graph/builder.py`) |
| Downstream BFS Algorithm | Approved Requirement | Owned by Preetam (`backend/app/graph/traversal.py`) |
| Automated Validation Engine | Approved Requirement | Owned by Soumya (`backend/app/validation/`) |
| In-Memory Undo Stack | Pending Decision / Sprint 2 | Documented in Sprint 2 roadmap |
| Multi-Objective Optimization | Out of Scope / Sprint 3+ | Preserved boundary |
