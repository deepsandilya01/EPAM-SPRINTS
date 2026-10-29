# Team Photon — Integration Guide

## 1. Executive Summary & Architecture Overview

The **Proactive Supply-Chain Decision, Ripple & Recovery Intelligence System** (Team Photon — LNCT) models multi-tier supply-chain dependencies as a directed acyclic graph (DAG):

$$\text{Supplier} \longrightarrow \text{Part} \longrightarrow \text{Finished Product} \longrightarrow \text{Customer Order}$$

The system architecture cleanly separates graph data storage, core validation, high-resolution tracing benchmarks, Flask API endpoints, and the D3.js visualization frontend.

```
                      +-----------------------------------+
                      |   photon_sprint1_graph_data.json  |
                      +-----------------+-----------------+
                                        |
                            JSON Load & Startup Audit
                                        v
                 +--------------------------------------------+
                 |          graph_validation Package          |
                 |  - validate_raw_graph_data() (pre-DiGraph) |
                 |  - validate_networkx_graph()               |
                 |  - trace_downstream_with_metrics()         |
                 +----------------------+---------------------+
                                        |
                            In-Memory DiGraph Init
                                        v
+-----------------------+      +--------+--------+      +---------------------------+
|    benchmarks/        | ---> |     app.py      | <--- |   pytest Test Suite       |
| benchmark_tracing.py  |      |   Flask API     |      |  (73 tests, 91% coverage) |
+-----------------------+      +--------+--------+      +---------------------------+
                                        |
                               HTTP JSON Endpoints
                                        v
                      +-----------------------------------+
                      |       static/index.html           |
                      |   (D3.js Force & Tier Canvas)     |
                      +-----------------------------------+
```

---

## 2. Core Modules & Responsibilities

| Component | Path | Primary Responsibilities | Status |
|---|---|---|---|
| **Flask API Server** | [`app.py`](../backend/app.py) | Exposes graph data, handles downstream BFS tracing, cascades node deletion with undo snapshots, provides reset, validation, and tracing benchmark endpoints. | **Implemented & Verified** |
| **Validation Package** | [`graph_validation/`](../backend/graph_validation/) | Standalone module providing schema models, policy configurations, pre-construction raw JSON validation, NetworkX structural validation, and high-resolution latency timers. | **Implemented & Verified** |
| **Benchmark Engine** | [`benchmarks/benchmark_tracing.py`](../backend/benchmarks/benchmark_tracing.py) | CLI statistical benchmarking tool (warm-up + 1000 runs per target) measuring pure graph traversal latencies against the 10 ms SLA. | **Implemented & Verified** |
| **Canonical Dataset** | [`photon_sprint1_graph_data.json`](../backend/data/photon_sprint1_graph_data.json) | Ground-truth baseline dataset (19 nodes, 21 edges) detailing suppliers, parts, products, orders, and their relationships. | **Implemented & Verified** |
| **Interactive Frontend** | [`static/index.html`](../backend/static/index.html) | D3.js v7 canvas rendering 4-column supply-chain tiers, drag mechanics, downstream cascade highlighting, impact preview panel, undo countdown toast, and deletion logs. | **Implemented & Verified** |
| **Frontend Validation Panel** | `static/index.html` (UI Panel) | Dedicated slide-out UI panel to render live `/api/validation` reports and trigger `/api/benchmark/tracing` runs from the browser. | **Proposed Enhancement** (Backend API & Contract Tests Verified) |

---

## 3. Flask & NetworkX Integration Details

### 3.1 Startup Validation
During server initialization in [`app.py`](../backend/app.py#L50-L57), the raw JSON payload is audited by `validate_raw_graph_data(RAW)` before the NetworkX graph object is constructed:

```python
RAW = _load_raw_data()

# Validate raw JSON schema and entities before graph construction
_startup_report = validate_raw_graph_data(RAW)
if not _startup_report.valid:
    import sys
    print(f"[VALIDATION WARNING] Baseline graph validation failed on startup: {len(_startup_report.errors)} errors.", file=sys.stderr)
```

> [!IMPORTANT]
> **Pre-construction validation is essential.** NetworkX's `nx.DiGraph.add_node()` silently overwrites node attributes when encountering duplicate IDs. Validating the raw JSON upfront catches duplicate identifiers (`ERR_DUPLICATE_NODE_ID`) that would otherwise go unnoticed once ingested into the graph structure.

### 3.2 Live Graph & Undo Stack
- **Graph State**: Stored in module-level `GRAPH: nx.DiGraph = _build_graph(RAW)`.
- **Undo History**: Maintained in `UNDO_STACK: list[dict] = []`, which stores deep copies of nodes, edges, deletion metadata, and execution timestamps for rollbacks.
- **Dynamic Validation**: `/api/validation` validates the live in-memory `GRAPH` instance at runtime, allowing verification before and after graph mutations (deletions, undos, and resets).

---

## 4. API Endpoints Reference

All endpoints return JSON responses with standard HTTP status codes.

### 4.1 Frontend Delivery
- **Route**: `GET /`
- **Handler**: `index()`
- **Status**: `200 OK`
- **Description**: Serves the D3.js visualization single-page application from `static/index.html`.

---

### 4.2 Full Graph Retrieval
- **Route**: `GET /api/graph`
- **Handler**: `api_graph()`
- **Status**: `200 OK`
- **Response Format**:
```json
{
  "nodes": [
    {
      "id": "SUP-01",
      "kind": "supplier",
      "label": "Apex Components",
      "location": "Pune",
      "name": "Apex Components",
      "note": "Primary supplier, electronics",
      "supplier_id": "SUP-01"
    }
  ],
  "edges": [
    {
      "source": "SUP-01",
      "target": "PART-01",
      "relation": "SUPPLIES",
      "lead_time_hours": 48,
      "max_capacity_units_per_day": 500
    }
  ]
}
```

---

### 4.3 Downstream Trace
- **Route**: `GET /api/downstream/<node_id>`
- **Handler**: `api_downstream(node_id)`
- **Status**: `200 OK`
- **Parameters**: `node_id` (string path parameter, e.g., `SUP-01`)
- **Behavior**: Uses `nx.descendants(GRAPH, node_id)` to collect all downstream reachable nodes.
- **Response Format**:
```json
{
  "root": "SUP-01",
  "downstream": [
    "ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05", "ORD-06",
    "PART-01", "PART-02", "PART-05", "PROD-01"
  ]
}
```

---

### 4.4 Impact Analysis Preview
- **Route**: `GET /api/impact/<node_id>`
- **Handler**: `api_impact(node_id)`
- **Status**: `200 OK` (or `404 Not Found` if `node_id` does not exist)
- **Behavior**: Non-mutating simulation of deleting `node_id`. Identifies incident edges, downstream cascades, and returns time complexity metadata.
- **Response Format**:
```json
{
  "node": {"id": "PART-05", "kind": "part", "label": "Fastener Kit"},
  "incoming_edges": [{"source": "SUP-01", "target": "PART-05", "relation": "SUPPLIES"}],
  "outgoing_edges": [{"source": "PART-05", "target": "PROD-01", "relation": "USED_IN"}],
  "downstream_nodes": ["PROD-01", "ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05", "ORD-06"],
  "total_nodes_affected": 8,
  "total_edges_affected": 10,
  "time_complexity": "O(V + E)",
  "time_complexity_explanation": "Traversal & cascade removal visits 8 vertices and inspects 10 edges in O(V + E) time."
}
```

---

### 4.5 Cascading Node Deletion
- **Route**: `DELETE /api/node/<node_id>`
- **Handler**: `api_delete_node(node_id)`
- **Status**: `200 OK` (or `404 Not Found` if `node_id` does not exist)
- **Behavior**: Computes downstream reachability set $R = \text{descendants}(node\_id) \cup \{node\_id\}$, snapshots current graph to `UNDO_STACK`, removes all $v \in R$ from `GRAPH`, and returns updated graph payload.
- **Response Format**:
```json
{
  "deleted_node_id": "PART-05",
  "deleted_label": "Fastener Kit",
  "deleted_kind": "part",
  "deleted": ["PART-05", "PROD-01", "ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05", "ORD-06"],
  "edges_removed": 10,
  "elapsed_ms": 0.312,
  "time_complexity": "O(V + E)",
  "graph": {"nodes": [...], "edges": [...]}
}
```

---

### 4.6 Undo Deletion
- **Route**: `POST /api/undo`
- **Handler**: `api_undo()`
- **Status**: `200 OK` (or `400 Bad Request` if `UNDO_STACK` is empty)
- **Behavior**: Pops the most recent graph snapshot from `UNDO_STACK`, restores nodes and edges into `GRAPH`, and returns restoration metrics.

---

### 4.7 Reset Graph
- **Route**: `POST /api/reset`
- **Handler**: `api_reset()`
- **Status**: `200 OK`
- **Behavior**: Clears `UNDO_STACK`, rebuilds `GRAPH` from the original `RAW` dataset, and returns canonical 19-node graph.

---

### 4.8 Graph Validation Endpoint
- **Route**: `GET /api/validation`
- **Handler**: `api_validation()`
- **Query Parameters**:
  - `mode`: `"baseline"` (asserts exact 19-node / 21-edge counts) or `"integrity"` (allows partial graphs but verifies structural consistency, valid endpoints, edge directions, and DAG property). Defaults automatically to `"baseline"` if $V=19 \land E=21$, else `"integrity"`.
  - `strict`: `"true"` returns `422 Unprocessable Entity` if `valid == false`; default `"false"` returns `200 OK` with full report JSON.
- **Response Format**:
```json
{
  "valid": true,
  "graph_name": "Team Photon - Sprint 1",
  "mode": "baseline",
  "summary": {
    "node_count": 19,
    "edge_count": 21,
    "supplier_count": 2,
    "part_count": 5,
    "product_count": 2,
    "order_count": 10,
    "supplies_count": 6,
    "used_in_count": 5,
    "fulfills_count": 10
  },
  "checks": [
    {"check_id": "SCHEMA_TOP_LEVEL", "status": "PASS", "message": "Top-level data structure is valid with 'nodes' and 'edges'."},
    {"check_id": "NODE_DUPLICATES", "status": "PASS", "message": "All node identifiers are unique across raw records."},
    {"check_id": "EDGE_REFERENCES", "status": "PASS", "message": "All edges connect valid existing nodes."},
    {"check_id": "EDGE_DIRECTIONS", "status": "PASS", "message": "All edges follow the agreed supply-chain direction (Supplier -> Part -> Product -> Order)."},
    {"check_id": "BASELINE_NODE_COUNTS", "status": "PASS", "message": "Expected baseline node counts match exactly (19 nodes: 2 sup, 5 part, 2 prod, 10 ord)."},
    {"check_id": "BASELINE_EDGE_COUNTS", "status": "PASS", "message": "Expected baseline edge counts match exactly (21 edges: 6 supplies, 5 used_in, 10 fulfills)."},
    {"check_id": "GRAPH_DIRECTED", "status": "PASS", "message": "Graph is a valid directed graph (DiGraph)."},
    {"check_id": "GRAPH_ACYCLICITY", "status": "PASS", "message": "Graph is a verified Directed Acyclic Graph (DAG) with zero cycles."}
  ],
  "errors": [],
  "warnings": [],
  "timestamp": "2026-10-28T16:28:20.100517+00:00"
}
```

---

### 4.9 Downstream Tracing Benchmark Endpoint
- **Route**: `GET /api/benchmark/tracing`
- **Handler**: `api_benchmark_tracing()`
- **Query Parameters**:
  - `node_id`: Target root node to trace (default: `"SUP-01"`).
  - `threshold_ms`: Target performance threshold in milliseconds (default: `10.0`).
- **Response Format**:
```json
{
  "source_node_id": "SUP-01",
  "source_exists": true,
  "downstream_node_ids": [
    "ORD-01", "ORD-02", "ORD-03", "ORD-04", "ORD-05", "ORD-06",
    "PART-01", "PART-02", "PART-05", "PROD-01"
  ],
  "visited_count": 10,
  "graph_node_count": 19,
  "graph_edge_count": 21,
  "elapsed_ns": 18400,
  "elapsed_ms": 0.0184,
  "threshold_ms": 10.0,
  "under_threshold": true,
  "status": "PASS",
  "algorithm": "NetworkX BFS descendants",
  "time_complexity": "O(V + E)"
}
```

---

## 5. Repository Files and Their Roles

```
EPAM-SPRINTS/
├── backend/                              # Flask application and validation package
│   ├── app.py                            # Flask application and REST API endpoints
│   ├── photon_sprint1_graph_data.json   # Baseline supply-chain graph dataset
│   ├── requirements.txt                  # Dependencies (Flask, NetworkX, pytest, pytest-cov, ruff)
│   ├── pytest.ini                        # Pytest configuration and markers
│   ├── static/
│   │   └── index.html                    # D3.js visualization and interactive client
│   ├── graph_validation/                 # Graph Validation Package
│   │   ├── __init__.py                   # Package exports
│   │   ├── schema.py                     # Dataclasses, Enums, and Policies
│   │   ├── validator.py                  # Multi-rule validation engine
│   │   ├── tracing.py                    # High-resolution downstream traversal timer
│   │   └── reporting.py                  # Console & JSON report generators
│   ├── benchmarks/
│   │   ├── __init__.py                   # Benchmark module
│   │   └── benchmark_tracing.py          # Statistical benchmark CLI
│   └── tests/
│       ├── conftest.py                       # Fixtures (raw data, canonical graph, app client)
│       ├── test_acyclicity.py                # DAG enforcement and cycle detection tests
│       ├── test_api_integration.py          # Flask route integration & state tests
│       ├── test_duplicate_ids.py             # Duplicate ID detection & collapse proof
│       ├── test_edge_direction.py           # Valid and invalid edge transition tests
│       ├── test_edge_integrity.py           # Endpoint reference & edge count tests
│       ├── test_frontend_validation_contract.py # API schema contract tests
│       ├── test_malformed_data.py            # Corrupt payloads and type tests
│       ├── test_missing_entities.py          # Missing keys and invalid values tests
│       ├── test_node_counts.py              # Category and total node count tests
│       ├── test_reporting.py                 # Report formatting and disk output tests
│       └── test_tracing.py                   # Reachability and traversal latency tests
│   └── data/                                 # Canonical graph dataset
│       └── photon_sprint1_graph_data.json
├── reports/                              # Generated JSON benchmark and validation reports
└── docs/
    ├── INTEGRATION_GUIDE.md              # Architecture and integration specification (this file)
    ├── FRONTEND_VALIDATION_GUIDE.md       # Frontend UI interaction & validation contract
    ├── GRAPH_SCHEMA.md                   # Formal entity & relationship schema
    ├── TESTING_AND_BENCHMARKING.md       # Test suite & benchmark execution details
    ├── ACCEPTANCE_CHECKLIST.md           # Acceptance criteria verification table
    └── SETUP.md                          # Step-by-step environment setup and execution guide
```

---

## 6. Installation, Execution, and Verification Steps

### Step 1: Environment Setup
```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Full Pytest Suite
```powershell
pytest tests/ -v
```
*Expected Result: 73 passed in ~0.8s.*

### Step 3: Run Benchmark Execution
```powershell
python -m benchmarks.benchmark_tracing
```
*Expected Result: Overall Status: [PASS], p95 latency < 0.04 ms (well below 10.0 ms).*

### Step 4: Start Application Server
```powershell
python app.py
```
*Access in browser at `http://localhost:5000`.*

---

## 7. Compatibility Considerations & Regression Checks

1. **Zero Breaking Changes on Legacy Routes**:
   - `GET /api/graph`, `GET /api/downstream/<id>`, `GET /api/impact/<id>`, `DELETE /api/node/<id>`, `POST /api/undo`, and `POST /api/reset` maintain 100% parameter and schema compatibility with Sprint 1 specifications.
2. **Post-Deletion State Handling**:
   - When a node is deleted, downstream nodes are cascaded away. A validation check in `baseline` mode will naturally report a count mismatch ($V < 19$). To accommodate this, the `/api/validation` endpoint supports `mode=integrity`, which relaxes strict baseline counts while maintaining strict DAG, direction, and reference integrity checks.
3. **Regression Safety**:
   - Automated regression test `tests/test_api_integration.py::test_deletion_and_validation_lifecycle` verifies the complete lifecycle: baseline $\to$ deletion $\to$ integrity validation $\to$ undo $\to$ baseline restoration.

