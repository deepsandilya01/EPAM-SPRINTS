# RE:Flow — Sprint 1 EPAM Technical Review Preparation Guide

> **Technical Review & Interview Guide**
> - **Audience**: Development Team & Technical Reviewers
> - **Project**: RE:Flow (EPAM Supply Chain Disruption Intelligence Engine)
> - **Format**: 3-Level Explanations for all 12 Core Concepts:
>   1. 🟢 **Beginner-Friendly Explanation**: Intuitive everyday real-world analogy.
>   2. 🔵 **Technical Explanation**: Engineering definitions, data structures, complexity, and design patterns.
>   3. 🟡 **Practical RE:Flow Example**: Concrete code snippet and dataset example (`SUP-01`, `PART-01`, `PROD-01`, `ORD-01`).

---

## Architecture Attribution

RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.

---

## Table of Contents
1. [Domain Models vs. API Schemas](#1-domain-models-vs-api-schemas)
2. [Supply Chain Node Tiers (Supplier, Part, Product, Order)](#2-supply-chain-node-tiers-supplier-part-product-order)
3. [Graph Edges and Relationship Directions](#3-graph-edges-and-relationship-directions)
4. [Directed Graphs (DAGs) and Topological Order](#4-directed-graphs-dags-and-topological-order)
5. [NetworkX DiGraph Integration](#5-networkx-digraph-integration)
6. [JSON Serialization and Deserialization](#6-json-serialization-and-deserialization)
7. [Data Validation and Integrity Constraints](#7-data-validation-and-integrity-constraints)
8. [Type Hints and Static Typing in Python](#8-type-hints-and-static-typing-in-python)
9. [Pydantic V2 for API Contracts](#9-pydantic-v2-for-api-contracts)
10. [Domain Graph Model vs. Graph Builder](#10-domain-graph-model-vs-graph-builder)
11. [Why Architecture Separates Models and Schemas](#11-why-architecture-separates-models-and-schemas)
12. [Cross-Team Integration Matrix](#12-cross-team-integration-matrix)

---

## 1. Domain Models vs. API Schemas

### 🟢 Beginner-Friendly Explanation
Think of an automobile manufacturing company:
- **Domain Model**: The actual physical engine and chassis inside the factory workshop, where oil, pistons, valves, and spark plugs are connected under strict mechanical rules. Factory engineers maintain these components to ensure operational stability and business logic integrity.
- **API Schema**: The glossy vehicle catalog or brochure shown to prospective buyers in the showroom. The customer does not see the complex internal engine blueprints; instead, they receive clean, formatted attributes (model name, price, horsepower, fuel efficiency) designed specifically for external viewing.

### 🔵 Technical Explanation
- **Domain Models** (`backend/app/models/`): Represent the core business entities in memory. They encapsulate business rules, compute derived domain properties (e.g., calculating `days_of_supply = stock / daily_consumption`), manage internal invariants, and maintain behavioral identity (equality based on entity ID). They are independent of transport protocols like HTTP or JSON.
- **API Schemas** (`backend/app/schemas/`): Represent Data Transfer Objects (DTOs) built using Pydantic. They define request and response contracts for the boundary layer (REST API over HTTP). They validate untrusted input payloads, enforce input sanitization, and serialize internal models to JSON responses.

### 🟡 Practical RE:Flow Example
```python
# 1. DOMAIN MODEL (Internal business entity with validation & behavior)
from backend.app.models.nodes import BOMPartNode
from backend.app.core.constants import TierType

part_entity = BOMPartNode(
    id="PART-01",
    tier=TierType.BOM_PART,
    name="Control Board",
    stock_on_hand=120,
    daily_consumption=20
)
# Automatically computes business metric:
assert part_entity.days_of_supply == 6.0

# 2. API SCHEMA (Boundary DTO for HTTP client)
from backend.app.schemas.graph import NodeResponseSchema

api_response_dto = NodeResponseSchema(
    id=part_entity.id,
    name=part_entity.name,
    tier=part_entity.tier.value,
    attributes={
        "stock_on_hand": part_entity.stock_on_hand,
        "daily_consumption": part_entity.daily_consumption,
        "days_of_supply": part_entity.days_of_supply
    }
)
# Serializes cleanly to JSON for Flask response
json_output = api_response_dto.model_dump()
```

---

## 2. Supply Chain Node Tiers (Supplier, Part, Product, Order)

### 🟢 Beginner-Friendly Explanation
Think of the step-by-step production cycle of a modern smartphone:
1. **Supplier (Tier 1)**: Component manufacturers like Samsung or Sony that supply specialized camera sensors.
2. **BOM Part (Tier 2)**: The raw parts and sub-assemblies stored in the manufacturing warehouse (e.g., camera modules, processors, display glass).
3. **Finished Product (Tier 3)**: The fully assembled smartphone (e.g., iPhone or Galaxy) sealed in its retail packaging.
4. **Customer Order (Tier 4)**: A retail purchase order from Amazon or Best Buy requesting delivery of 500 units by a specified date.

### 🔵 Technical Explanation
The RE:Flow architecture models supply chain hierarchies as a multi-tier stratified network. Each tier has strict cardinality, semantics, and attributes:
1. `SupplierNode` (Tier 1): Root nodes of the network ($\text{in-degree} = 0$). Attributes: `location`, `note`.
2. `BOMPartNode` (Tier 2): Intermediate component inventory. Attributes: `stock_on_hand` ($\ge 0$), `daily_consumption` ($\ge 0$), and `days_of_supply` ($\text{float}$).
3. `FinishedProductNode` (Tier 3): Multi-part assembly representation. Attributes: `parts_needed` (BOM spec).
4. `CustomerOrderNode` (Tier 4): Sink nodes ($\text{out-degree} = 0$). Attributes: `customer`, `product_id`, `quantity` ($> 0$), `deadline` (ISO-8601).

### 🟡 Practical RE:Flow Example
```python
from backend.app.models.nodes import (
    SupplierNode, BOMPartNode, FinishedProductNode, CustomerOrderNode
)
from backend.app.core.constants import TierType

s = SupplierNode(id="SUP-01", tier=TierType.SUPPLIER, name="Apex Components", location="Pune")
p = BOMPartNode(id="PART-01", tier=TierType.BOM_PART, name="Microcontroller", stock_on_hand=500, daily_consumption=50)
prod = FinishedProductNode(id="PROD-01", tier=TierType.FINISHED_PRODUCT, name="Smart Inverter", parts_needed="PART-01 x1")
o = CustomerOrderNode(id="ORD-01", tier=TierType.CUSTOMER_ORDER, name="Order-01", customer="Tata Power", product_id="PROD-01", quantity=50, deadline="2026-11-15")
```

---

## 3. Graph Edges and Relationship Directions

### 🟢 Beginner-Friendly Explanation
Think of a one-way river system: water flows strictly downstream from mountain springs to the sea; it cannot flow uphill in reverse.
Similarly, in a supply chain network, dependencies flow downstream from suppliers toward end customers:
- A vendor supplies raw parts (`SUPPLIES`).
- A part is assembled into a finished product (`USED_IN`).
- A finished product satisfies a customer delivery order (`FULFILLS`).

### 🔵 Technical Explanation
Edges are directed ordered pairs $(u, v) \in E$ representing asymmetric material and dependency flow. The direction represents causal propagation: disruption at $u$ propagates downstream to $v$.
- `SuppliesEdge` ($T_1 \rightarrow T_2$): Carries supply attributes (`lead_time_hours`, `max_capacity_units_per_day`).
- `UsedInEdge` ($T_2 \rightarrow T_3$): Carries assembly bill-of-materials ratio (`quantity_per_unit`).
- `FulfillsEdge` ($T_3 \rightarrow T_4$): Maps finished assemblies to target customer orders.

### 🟡 Practical RE:Flow Example
```python
from backend.app.models.edges import SuppliesEdge, UsedInEdge, FulfillsEdge
from backend.app.core.constants import EdgeType

e1 = SuppliesEdge(source="SUP-01", target="PART-01", relation=EdgeType.SUPPLIES, lead_time_hours=48)
e2 = UsedInEdge(source="PART-01", target="PROD-01", relation=EdgeType.USED_IN, quantity_per_unit=2)
e3 = FulfillsEdge(source="PROD-01", target="ORD-01", relation=EdgeType.FULFILLS)

# Validation: Self-loops are strictly rejected!
# SuppliesEdge(source="SUP-01", target="SUP-01", relation=EdgeType.SUPPLIES) -> Raises InvalidEdgeError!
```

---

## 4. Directed Graphs (DAGs) and Topological Order

### 🟢 Beginner-Friendly Explanation
Think of academic prerequisites in a degree program: you must complete Year 1 before Year 2, and Year 2 before Year 3. You can never have a circular dependency where passing Year 3 requires having already graduated from Year 4. That clean, non-repeating, forward-moving flow is called a **Directed Acyclic Graph (DAG)**.

### 🔵 Technical Explanation
A Directed Acyclic Graph $G = (V, E)$ has no directed cycles: there is no non-empty path $v_1 \rightarrow v_2 \rightarrow \dots \rightarrow v_n$ such that $v_1 = v_n$.
- **Why DAG is required in RE:Flow**: Topological sorting allows deterministically computing the blast radius and lead-time accumulation. If a cycle existed, a part would depend on itself, causing infinite loops in traversal algorithms.
- **Topological Invariant**: For every directed edge $(u, v)$, $\text{tier}(u) < \text{tier}(v)$.

### 🟡 Practical RE:Flow Example
```text
(SUP-01) ---> [PART-01] ---> [PROD-01] ---> (ORD-01)
   |                             ^
   +--------> [PART-02] ---------+

Every path strictly flows from Left (Tier 1) to Right (Tier 4).
Cycles (e.g. PART-01 -> PROD-01 -> PART-01) are impossible in a valid DAG.
```

---

## 5. NetworkX DiGraph Integration

### 🟢 Beginner-Friendly Explanation
Domain entities (`SupplyChainGraph`) provide the structured building blocks and business blueprints, while `networkx.DiGraph` acts as a specialized high-speed calculation engine used to execute complex graph algorithms with optimal efficiency.

### 🔵 Technical Explanation
`networkx.DiGraph` is a specialized graph data structure in Python using nested dictionaries for adjacency representation, providing $O(1)$ edge lookup and out-degree traversal.
- `SupplyChainGraph` maintains strongly typed domain objects and custom business properties.
- The graph builder constructs a `networkx.DiGraph`:
  ```python
  import networkx as nx
  G = nx.DiGraph()
  for node in domain_graph.nodes:
      G.add_node(node.id, **node.to_dict())
  for edge in domain_graph.edges:
      G.add_edge(edge.source, edge.target, **edge.to_dict())
  ```
- This allows NetworkX to run cycle detection (`nx.is_directed_acyclic_graph(G)`) and topological sorts effortlessly.

---

## 6. JSON Serialization and Deserialization

### 🟢 Beginner-Friendly Explanation
Think of shipping a physical parcel: you pack the item securely into a cardboard box before mailing it (**Serialization** / Packing). When the recipient receives the package, they open the box and unpack the item for use (**Deserialization** / Unpacking).
Similarly, in software, in-memory Python objects must be packaged into standardized text format (JSON) before they can be transmitted across the network.

### 🔵 Technical Explanation
- **Serialization** (`to_dict()` and Pydantic `.model_dump()`): Converts in-memory Python instances (`BaseNode`, `BaseEdge`, `SupplyChainGraph`) into primitive Python dictionaries composed strictly of strings, ints, floats, lists, and dicts, which `json.dumps()` or Flask `jsonify()` can format into JSON text.
- **Deserialization** (`from_dict()` and Pydantic `.model_validate()`): Parses raw JSON payloads, validates structure, resolves enum types, and instantiates typed domain objects in memory.

### 🟡 Practical RE:Flow Example
```python
from backend.app.models.graph import SupplyChainGraph

# Deserialization from dictionary
graph = SupplyChainGraph.from_dict({
    "nodes": [{"id": "SUP-01", "name": "Apex", "tier": "supplier"}],
    "edges": []
})

# Serialization to dictionary
payload = graph.to_dict()
assert "summary" in payload
assert payload["nodes"][0]["id"] == "SUP-01"
```

---

## 7. Data Validation and Integrity Constraints

### 🟢 Beginner-Friendly Explanation
Think of an airport security checkpoint: passengers cannot enter the departure terminal without a verified passport and a valid boarding pass. Our validation layers ensure that incomplete records, blank IDs, or invalid quantities (such as negative inventory counts) are caught and rejected before entering memory.

### 🔵 Technical Explanation
RE:Flow enforces validation at two distinct architectural levels:
1. **Syntactic / Attribute Validation**: Handled by Pydantic schemas and dataclass `__post_init__` checks. Ensures non-empty strings, positive integers, regex matching (e.g. `^SUP-[0-9A-Za-z_-]+$`), and valid enum types.
2. **Semantic / Topological Validation**: Handled by domain models (`validate_endpoints`) and the validation module. Ensures no self-loops, no illegal tier jumps, and strict acyclicity.

---

## 8. Type Hints and Static Typing in Python

### 🟢 Beginner-Friendly Explanation
Think of a three-prong electrical power plug: it fits exclusively into a matching grounded three-prong wall socket. Type hints in Python label variables and function signatures clearly (such as expecting a `str` or an `int`), preventing bugs caused by accidentally passing text where a numeric value is expected.

### 🔵 Technical Explanation
Python is dynamically typed at runtime, but PEP 484 type annotations (`typing.Optional`, `typing.List`, `typing.Dict`, `typing.Union`) provide static type clarity.
- **Benefits**:
  1. Catches potential `TypeError` bugs before running the code (via linters like Ruff).
  2. Enables IDE auto-completion and inline documentation.
  3. Acts as self-documenting code for team members.
  4. Powers Pydantic V2 runtime type coercion and validation.

---

## 9. Pydantic V2 for API Contracts

### 🟢 Beginner-Friendly Explanation
Think of Pydantic as a strict security officer stationed at the entrance of an API. It inspects every incoming data payload from the frontend. If the data satisfies all rules, it formats it cleanly and admits it into the application; if anything is invalid, it promptly turns the request away with a clear, helpful error explanation.

### 🔵 Technical Explanation
Pydantic V2 is a high-performance data validation library written with a Rust core (`pydantic-core`).
- In RE:Flow, every REST endpoint uses Pydantic `BaseModel` classes:
  - `NodeResponseSchema`, `EdgeResponseSchema`, `GraphResponseSchema`
  - `TraversalRequestSchema`, `TraversalResponseSchema`
  - `ValidationResponseSchema`
- Enforces runtime schema adherence, type casting, field constraints (`ge=1`, `min_length=1`), and fast `.model_dump()` serialization.

---

## 10. Domain Graph Model vs. Graph Builder

### 🟢 Beginner-Friendly Explanation
- **Domain Graph Model (`SupplyChainGraph`)**: The recipe book and ingredient list describing what items exist and how they are defined.
- **Graph Builder (`SupplyChainGraphBuilder`)**: The chef who reads the recipe book, gathers the raw ingredients from the dataset, and methodically constructs the final dish.

### 🔵 Technical Explanation
- **`SupplyChainGraph`** (`backend/app/models/graph.py`): Passive domain entity container. It defines data structures, node/edge collections, getters, and serialization methods. It does not know where files live on the hard drive or how NetworkX builds graphs.
- **`SupplyChainGraphBuilder`** (`backend/app/graph/builder.py`): Active service/builder class. It receives loaded datasets, orchestrates domain instantiation, populates the NetworkX graph, and manages builder lifecycles.

---

## 11. Why Architecture Separates Models and Schemas

### 🟢 Beginner-Friendly Explanation
When a bank issues an account statement to a customer, the document displays the account balance and recent transactions. However, it never discloses the bank's internal database passwords, encryption keys, or private audit records.
In the same way, keeping internal memory models (`models/`) decoupled from external network response schemas (`schemas/`) protects internal application state and ensures public contracts remain clean and stable.

### 🔵 Technical Explanation
Separation of Concerns and Clean Architecture principles (Martin Fowler / Hexagonal Architecture):
1. **Decoupling from Transport Layer**: Internal models can change (e.g. adding caching or private attributes like `_adjacency_out`) without breaking the REST API contract consumed by the frontend.
2. **Security & Data Sanitization**: Internal domain models may contain operational attributes that should not be exposed directly in public API responses.
3. **Single Responsibility Principle**: Domain models are responsible for business logic; API schemas are responsible for serialization, deserialization, and HTTP payload validation.

---

## 12. Cross-Team Integration Matrix

Here is how the shared contracts provide the foundation for all Sprint 1 modules:

| Team Member | Module / File | Responsibility & Integration |
|---|---|---|
| **Mishti** | `docs/sprint/sprint_1.md` | Tracks delivery of 4 node models, 3 edge models, and JSON schema. |
| **Deep** | `backend/app/models/`, `schemas/` | Implemented domain models, API schemas, canonical JSON schema (Sprint 1 scope completed). |
| **Anushka** | `data/raw/scenario_dataset.json` | Populates the approved 19-node, 21-edge baseline scenario. |
| **Aadee** | `backend/app/data/loader.py` | Uses `create_node()` and `create_edge()` factories to parse raw JSON into domain instances. |
| **Ansh** | `backend/app/graph/builder.py` | Takes `SupplyChainGraph` domain objects to populate the NetworkX `DiGraph`. |
| **Preetam** | `backend/app/graph/traversal.py` | BFS traversal output maps directly into `TraversalResponseSchema`. |
| **Sonal** | `docs/reports/mapping_verification.md` | Verifies the 21 directed edges against domain transition rules. |
| **Soumya** | `backend/app/validation/` | Uses `validate_endpoints()` rules and formats audit reports into `ValidationResponseSchema`. |
| **Divyanshu** | `backend/app/api/router.py`, `test_edge_cases.py` | Manages API routing and edge-case complexity analysis. |
| **Shanu** | `backend/tests/` | Automated test suite and Pytest fixture harness. |
| **Kanak** | `backend/app/benchmarks/` | Performance benchmark harness measuring <10ms traversal SLA. |
| **Sumit** | `frontend/static/js/api.js`, `README.md` | Consumes canonical JSON response payloads (`GET /api/graph`, `POST /api/traversal`). |

---

## Technical Review Summary Statement

> *"In Sprint 1, our team established the foundation of RE:Flow through collaborative system architecture discussions. The domain model and data contract layer strictly enforces the 4-tier supply chain hierarchy (Supplier $\rightarrow$ BOM Part $\rightarrow$ Finished Product $\rightarrow$ Customer Order) and ensures that all dependencies are valid directed relationships. By separating internal domain entities from Pydantic API schemas, our architecture achieves clean decoupling, type safety, and zero-defect serialization across all endpoints. All 34 unit tests pass in 0.06 seconds, verifying 100% compatibility with our canonical 19-node, 21-edge supply chain scenario."*
