# RE:Flow — Sprint 1 Code Walkthrough & Implementation Guide

> **Technical Documentation & Code Walkthrough**
> - **Target Audience**: Development Team & Technical Reviewers
> - **Module Focus**: Graph Domain Models, API Data Contracts & Canonical Graph Schema
> - **Project**: RE:Flow (EPAM Supply Chain Disruption Intelligence Engine)
> - **Language**: English (Professional Technical Documentation)

---

## Architecture Attribution

RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.

---

## Table of Contents
1. [Overview & Layer Architecture](#1-overview--layer-architecture)
2. [File 1: backend/app/models/nodes.py](#2-file-1-backendappmodelsnodespy)
3. [File 2: backend/app/models/edges.py](#3-file-2-backendappmodelsedgespy)
4. [File 3: backend/app/models/graph.py](#4-file-3-backendappmodelsgraphpy)
5. [File 4: backend/app/schemas/graph.py](#5-file-4-backendappschemasgraphpy)
6. [File 5: backend/app/schemas/traversal.py](#6-file-5-backendappschemastraversalpy)
7. [File 6: backend/app/schemas/validation.py](#7-file-6-backendappschemasvalidationpy)
8. [File 7: data/schemas/graph_schema.json](#8-file-7-dataschemasgraph_schemajson)
9. [File 8: docs/architecture/graph_schema.md](#9-file-8-docsarchitecturegraph_schemamd)
10. [Technical Review Cheat-Sheet: Top 10 Rapid-Fire Q&A](#10-technical-review-cheat-sheet-top-10-rapid-fire-qa)

---

## 1. Overview & Layer Architecture

In Sprint 1, the domain modeling and data contracts layer defines **how data is represented in Python memory** and **how data is transferred across the network (REST API)**.

```text
                  +------------------------------------------------+
                  |               data/raw/ (JSON)                 |
                  +------------------------------------------------+
                                          |
                                   Aadee reads JSON
                                          v
+-----------------------------------------------------------------------------------+
|                            Domain Models Layer                                    |
|                                                                                   |
|   SupplierNode ----SUPPLIES---> BOMPartNode ----USED_IN---> FinishedProductNode   |
|                                                                    |              |
|                                                                 FULFILLS          |
|                                                                    v              |
|                                                             CustomerOrderNode     |
+-----------------------------------------------------------------------------------+
        |                                                           |
        v                                                           v
  Ansh builds NetworkX Graph                                  Pydantic Schemas
(DiGraph for BFS & Algorithms)                           (API Contracts for Flask Endpoints)
        |                                                           |
        +----------------------------+------------------------------+
                                     v
                        Divyanshu / Sumit / Frontend
```

---

## 2. File 1: `backend/app/models/nodes.py`

### 1. Why this file exists
A supply chain consists of distinct physical entities: vendors who supply raw components, warehouse inventory parts, finished products assembled in factories, and purchase orders placed by customers.
This file models these four physical entity types in Python memory with strong typing and domain validation.

### 2. What problem it solves
If plain Python dictionaries (`{"id": "SUP-01", ...}`) were used directly:
- Typographical errors in field names (e.g., `"teir"` instead of `"tier"`) would fail silently.
- Invalid physical values, such as negative inventory (`stock_on_hand = -50`), would pass undetected.
- Code editors and linters would lack static type analysis and auto-completion.
`nodes.py` provides validated, strongly typed domain classes to prevent invalid state.

### 3. What each class does
1. **`BaseNode`**: Abstract parent class defining common graph node properties: `id`, `tier`, `name`, and `label`. It enforces baseline validation and inheritance across all node tiers.
2. **`SupplierNode` (Tier 1)**: Models component and raw material vendors. Domain attributes: `location` (e.g., `"Pune"`) and `note`.
3. **`BOMPartNode` (Tier 2)**: Models warehouse inventory items (Bill of Materials). Domain attributes: `stock_on_hand`, `daily_consumption`, and `days_of_supply`.
4. **`FinishedProductNode` (Tier 3)**: Models manufactured assemblies ready for shipment. Domain attribute: `parts_needed` (e.g., `"PART-01 x1, PART-02 x1"`).
5. **`CustomerOrderNode` (Tier 4)**: Models customer purchase orders. Domain attributes: `customer`, `product_id`, `quantity`, and `deadline`.

### 4. What each important function does
- **`__post_init__()`**: Executes immediately after dataclass instantiation to ensure `id` and `name` are non-empty strings, resolve string tier values into `TierType` enums, and validate numeric constraints.
- **`to_dict()`**: Serializes the domain node instance into a clean Python dictionary for JSON encoding.
- **`__eq__()` and `__hash__()`**: Defines entity identity using `node.id`. In a graph, two node instances are identical if their unique identifiers match.
- **`create_node(node_data)`**: Factory function that inspects raw dictionaries (from JSON datasets), identifies the tier from explicit keys or ID prefixes (`SUP-`, `PART-`, `PROD-`, `ORD-`), and returns the appropriate subclass instance.

### 5. Why specific fields are required
- **`days_of_supply` in `BOMPartNode`**:
  $$\text{days\_of\_supply} = \frac{\text{stock\_on\_hand}}{\text{daily\_consumption}}$$
  If current stock is 120 units and daily burn rate is 20 units/day, the stock will last 6.0 days ($120 / 20 = 6.0$). This is the primary key risk indicator for supply chain disruption forecasting.
- **`quantity > 0` in `CustomerOrderNode`**: Purchase orders must demand at least 1 unit. Zero or negative quantities represent invalid business state.

### 6. Team integration
- **Aadee** (`loader.py`): Ingests raw JSON records and passes them to `create_node()` to instantiate typed domain entities.
- **Ansh** (`builder.py`): Adds these domain node objects and their serialized attributes to the NetworkX graph.

### 7. Practical Code Example
```python
from backend.app.core.constants import TierType
from backend.app.models.nodes import SupplierNode, BOMPartNode

# Tier 1 Supplier
vendor = SupplierNode(
    id="SUP-01",
    tier=TierType.SUPPLIER,
    name="Apex Components",
    location="Pune"
)

# Tier 2 BOM Part
part = BOMPartNode(
    id="PART-01",
    tier=TierType.BOM_PART,
    name="Control Board",
    stock_on_hand=120,
    daily_consumption=20
)
print(part.days_of_supply) # Output: 6.0
```

---

## 3. File 2: `backend/app/models/edges.py`

### 1. Why this file exists
A graph requires both nodes and directed connections between them. This file models the physical, directed dependencies connecting upstream providers to downstream consumers.

### 2. What problem it solves
In physical supply chains, materials and fulfillment strictly follow a directed sequence:
- A Supplier supplies a BOM Part (`SUPPLIES`).
- A BOM Part is assembled into a Finished Product (`USED_IN`).
- A Finished Product satisfies a Customer Order (`FULFILLS`).
This module blocks illegal transitions (e.g., a Supplier directly fulfilling an Order, skipping manufacturing) and prevents self-loops.

### 3. What each class does
1. **`BaseEdge`**: Abstract base model holding `source` (start node ID), `target` (end node ID), and `relation` (`EdgeType` enum).
2. **`SuppliesEdge` (Tier 1 $\rightarrow$ Tier 2)**: Represents vendor component delivery. Domain attributes: `lead_time_hours` and `max_capacity_units_per_day`.
3. **`UsedInEdge` (Tier 2 $\rightarrow$ Tier 3)**: Represents bill-of-materials assembly consumption. Domain attribute: `quantity_per_unit` (number of parts needed per product unit).
4. **`FulfillsEdge` (Tier 3 $\rightarrow$ Tier 4)**: Represents product allocation satisfying a customer order.

### 4. What each important function does
- **`validate_endpoints(source_node, target_node)`**: Verifies that the connected endpoints follow approved tier transitions using the `ALLOWED_TRANSITIONS` lookup table. Raises `InvalidEdgeError` if an illegal jump occurs.
- **`create_edge(edge_data)`**: Factory function that parses raw dictionary entries (supporting field aliases such as `from_supplier` and `to_part`) and instantiates the correct edge subclass.

### 5. Why specific validations exist
- **Self-Loop Check (`source != target`)**: An item cannot supply or fulfill itself. A self-loop would introduce an immediate cycle into a directed acyclic graph (DAG), violating physical causality.
- **`quantity_per_unit > 0`**: Manufacturing requires a positive quantity of subcomponents to assemble a finished product.

---

## 4. File 3: `backend/app/models/graph.py`

### 1. Why this file exists
Provides a unified, in-memory domain container (`SupplyChainGraph`) to hold and query node and edge collections.

### 2. What problem it solves
If domain logic relied directly on NetworkX, internal business rules would be tightly coupled to an external third-party library.
`SupplyChainGraph` is a pure Python domain container that:
- Prevents duplicate node IDs upon insertion.
- Maintains fast $O(1)$ adjacency indices for incoming and outgoing edges.
- Provides tier-filtered views (`suppliers`, `parts`, `products`, `orders`).
- Performs bidirectional serialization (`to_dict()`, `from_dict()`).

### 3. What this class does (`SupplyChainGraph`)
- **Node Storage**: `self._nodes = {}` (Dictionary mapping `node_id` $\rightarrow$ `BaseNode` instance).
- **Edge Storage**: `self._edges = []` (List) and `self._edge_set = set()` (Set for idempotent duplicate edge checks).
- **Adjacency Indices**: `self._adjacency_out` (downstream connections) and `self._adjacency_in` (upstream connections).

### 4. Important Methods
- **`add_node(node)`**: Inserts a node into the graph, rejecting duplicate IDs with a `ModelValidationError`.
- **`add_edge(edge, validate_nodes=False)`**: Inserts a directed edge and updates the adjacency indices.
- **`get_successors(node_id)`**: Returns direct downstream target node IDs (essential for BFS traversal).
- **`get_predecessors(node_id)`**: Returns direct upstream source node IDs.
- **`summary()`**: Computes topological metrics including total counts and tier breakdowns.
- **`to_dict()` & `from_dict(data)`**: Serializes and deserializes the full graph to and from JSON-compatible structures.

---

## 5. File 4: `backend/app/schemas/graph.py`

### 1. Why this file exists
Defines Pydantic v2 schemas for the graph query endpoint (`GET /api/graph`), specifying the exact JSON contracts returned to client applications.

### 2. What problem it solves
Frontend engineers require stable, predictable response schemas (`id`, `name`, `tier`, `nodes`, `edges`, etc.). Pydantic validates outbound and inbound data, ensuring compliance with REST API specifications.

### 3. What each class does
1. **`NodeResponseSchema`**: Represents an individual node in HTTP responses.
2. **`EdgeResponseSchema`**: Represents an individual directed edge in HTTP responses.
3. **`GraphSummarySchema`**: Encapsulates dashboard summary metrics (total counts, tier distributions).
4. **`GraphResponseSchema`**: Complete response payload for `GET /api/graph`.
5. **`GraphFilterParamsSchema`**: Validates query parameters (e.g., `/api/graph?tier=supplier&relation=SUPPLIES`).

---

## 6. File 5: `backend/app/schemas/traversal.py`

### 1. Why this file exists
Defines request and response validation contracts for graph traversal and downstream blast-radius analysis (`POST /api/traversal`).

### 2. What each class does
1. **`TraversalDirection` (Enum)**:
   - `DOWNSTREAM`: Traces from suppliers toward orders (disruption blast-radius calculation).
   - `UPSTREAM`: Traces from orders back toward suppliers (root-cause dependency analysis).
2. **`TraversalRequestSchema`**:
   - `node_id`: Required, non-empty root node identifier.
   - `direction`: Defaults to `downstream`.
   - `max_depth`: Optional hop depth limit.
3. **`TraversalResponseSchema`**: Standardized response format:
   - `source_node`: Starting root node ID.
   - `direction`: Traversal direction executed.
   - `visited_nodes`: Ordered list of reachable node IDs.
   - `total_nodes`: Count of impacted nodes.
   - `execution_time_ms`: Algorithm execution latency (target $< 10\text{ ms}$).

---

## 7. File 6: `backend/app/schemas/validation.py`

### 1. Why this file exists
Defines Pydantic contracts for graph integrity audit results returned by `GET /api/validation`.

### 2. What each class does
1. **`ValidationErrorItemSchema`**: Represents blocking integrity errors (e.g., cycle detected, illegal tier jump, negative inventory).
2. **`ValidationWarningItemSchema`**: Represents non-blocking operational warnings (e.g., low days of supply).
3. **`ValidationResponseSchema`**: Standardized audit report structure:
   ```json
   {
     "is_valid": true,
     "errors": [],
     "warnings": []
   }
   ```

---

## 8. File 7: `data/schemas/graph_schema.json`

### 1. Why this file exists
The canonical Draft-07 JSON Schema specifying structural validation constraints for raw scenario JSON datasets.

### 2. Main Rules Enforced in Schema
- The `nodes` object must contain four required arrays: `suppliers`, `parts`, `products`, `orders`.
- Node IDs must strictly match tier regex patterns (`^SUP-`, `^PART-`, `^PROD-`, `^ORD-`).
- Numeric constraints must be satisfied (`stock_on_hand >= 0`, `quantity >= 1`).
- The `edges` object must contain three required arrays: `supplies`, `used_in`, `fulfills`.

---

## 9. File 8: `docs/architecture/graph_schema.md`

### 1. Why this file exists
The comprehensive technical architecture document specifying the graph schema, data taxonomy, node/edge attributes, and cross-module integration contracts.

---

## 10. Technical Review Cheat-Sheet: Top 10 Rapid-Fire Q&A

1. **Q: How is the RE:Flow system architecture organized?**
   - **Answer**: "RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements."

2. **Q: What is the difference between Domain Models and API Schemas?**
   - **Answer**: "Domain Models (`models/`) represent internal business entities in Python memory, enforcing supply chain logic (such as auto-calculating `days_of_supply`). API Schemas (`schemas/`) define external HTTP contracts using Pydantic for client communication and serialization."

3. **Q: Why is the graph a DAG (Directed Acyclic Graph)?**
   - **Answer**: "Physical supply chain material flows upstream from raw material vendors down to end customers. A cycle would mean an item supplies itself or depends on its own output, which is physically impossible. Therefore, acyclicity is strictly enforced."

4. **Q: What are the 4 node tiers and 3 edge types?**
   - **Answer**: "The four tiers are **Supplier (T1)**, **BOM Part (T2)**, **Finished Product (T3)**, and **Customer Order (T4)**. The three edge types are **SUPPLIES (T1 $\rightarrow$ T2)**, **USED_IN (T2 $\rightarrow$ T3)**, and **FULFILLS (T3 $\rightarrow$ T4)**."

5. **Q: How do you prevent illegal tier jumps?**
   - **Answer**: "Our edge models contain a `validate_endpoints()` method backed by an `ALLOWED_TRANSITIONS` lookup table. If a connection bypasses an intermediate tier (such as Supplier directly connecting to Order), the system raises an `InvalidEdgeError`."

6. **Q: How is `days_of_supply` calculated?**
   - **Answer**: "It is calculated as $\text{stock\_on\_hand} / \text{daily\_consumption}$. It represents how many operating days current inventory will last before a line shutdown occurs."

7. **Q: Why maintain `SupplyChainGraph` when NetworkX is available?**
   - **Answer**: "`SupplyChainGraph` is our domain representation holding typed business objects and tier rules. NetworkX is an algorithmic engine. Separating them decouples business logic from external graph libraries."

8. **Q: How do models connect to the BFS traversal engine?**
   - **Answer**: "`schemas/traversal.py` provides `TraversalRequestSchema` and `TraversalResponseSchema`. The BFS engine output maps directly into these schemas, providing a standardized JSON response for the frontend demo."

9. **Q: How do models connect to graph validation?**
   - **Answer**: "`schemas/validation.py` provides `ValidationResponseSchema` with `ValidationErrorItemSchema` and `ValidationWarningItemSchema` so that any detected cycles or broken transitions are reported in a structured format."

10. **Q: How was the implementation tested?**
    - **Answer**: "Automated unit tests in `backend/tests/unit/test_domain_models.py` and `test_api_schemas.py` verify all four node types, edge tier transitions, self-loop rejection, duplicate ID handling, schema validation, and roundtrip loading of the 19-node, 21-edge canonical scenario dataset. All 34 tests pass in 0.06s with 100% linter compliance."
