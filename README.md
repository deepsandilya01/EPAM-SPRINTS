# RE:Flow — Supply Chain Graph & Scenario Generator

RE:Flow is a high-performance supply chain dependency mapping and impact analysis platform. It models multi-tier supply chain networks as directed acyclic graphs (DAGs) using NetworkX, simulating disruption cascades, computing real-time blast radii, and executing topological validations.

---

## 1. Project Overview & Technology Stack

- **Backend Framework**: Python 3.11+ with Flask
- **Graph Processing Engine**: NetworkX (`DiGraph`)
- **Domain Modeling & Contracts**: Dataclasses and Pydantic v2
- **Frontend Visualization**: Interactive D3.js (v7) with SVG force-directed layout, zoom, drag, and live blast-radius preview
- **Static Asset Serving**: Native Flask static serving directly from `backend/app/static/`
- **Deployment Platform**: **Render** (unified web service, zero database dependencies, zero Vercel configuration)
- **Data Architecture**: Self-contained JSON datasets inside `backend/app/data/` (no root-level `data/` directory)

---

## 2. Core Functional Capabilities

### Graph Construction & 4-Tier Topology
- Loads canonical baseline scenario with **19 nodes** and **21 directed edges**:
  - **Tier 1 (Suppliers)**: 2 primary component & material vendors (`SUP-01`, `SUP-02`)
  - **Tier 2 (BOM Parts)**: 5 bill of materials items (`PART-01` through `PART-05`)
  - **Tier 3 (Finished Products)**: 2 manufactured assemblies (`PROD-01`, `PROD-02`)
  - **Tier 4 (Customer Orders)**: 10 customer demand orders (`ORD-01` through `ORD-10`)
- Validates 3 strict relationship types:
  - `SUPPLIES`: Supplier $\rightarrow$ BOM Part
  - `USED_IN`: BOM Part $\rightarrow$ Finished Product
  - `FULFILLS`: Finished Product $\rightarrow$ Customer Order

### Real-Time Traversal & Blast-Radius Impact Analysis
- High-performance Breadth-First Search (BFS) reachability traversal (`< 10ms` SLA verified, typical runtime `< 0.05ms`).
- Blast radius calculations displaying direct downstream dependencies, affected orders, and complexity metrics ($O(V + E)$).

### Mutation Operations & State Preservation
- **Cascading Deletion**: Deleting a node automatically cascades through all downstream dependent parts, assemblies, and customer orders.
- **Undo Operation**: Restores previously deleted nodes and edges with attribute integrity in under 0.1ms.
- **Reset Operation**: Idempotently resets graph topology back to the canonical 19-node baseline.
- **Session State Synchronization**: Seamless state preservation across HTTP sessions via client state cookies.

### Multi-Level Graph & Schema Validation
- Pre-construction JSON schema and unique ID validation.
- Live graph DAG acyclicity verification with exact cycle path detection.
- Baseline entity count verification against SLA metrics.

---

## 3. Final Repository Architecture

```text
EPAM-SPRINTS/
├── backend/
│   ├── app/
│   │   ├── __init__.py                 # Application package initializer
│   │   ├── main.py                     # Flask entry point, error handlers & static serving
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py             # Unified API blueprint (`api_bp`) & session state hooks
│   │   │   └── routes/
│   │   │       ├── __init__.py         # Routes package initializer
│   │   │       ├── graph.py            # GET /api/graph, DELETE /api/node/<id>, POST /undo, POST /reset
│   │   │       ├── traversal.py        # GET /api/downstream/<id>, GET /api/impact/<id>, POST /api/traversal
│   │   │       ├── validation.py       # GET /api/validation (baseline & integrity modes)
│   │   │       ├── benchmarks.py       # GET /api/benchmark/tracing (SLA performance telemetry)
│   │   │       └── health.py           # GET /api/health (service health & entity counts)
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py             # Core package initializer
│   │   │   ├── config.py               # Type-safe Settings dataclass
│   │   │   ├── constants.py            # TierType, EdgeType, ALLOWED_TRANSITIONS, baseline counts
│   │   │   └── exceptions.py           # ReflowException domain exception hierarchy
│   │   │
│   │   ├── data/
│   │   │   ├── __init__.py             # Data package initializer
│   │   │   ├── loader.py               # Canonical JSON dataset loader & path resolver
│   │   │   ├── datasets/
│   │   │   │   └── scenario_dataset.json  # Authoritative canonical 19-node dataset
│   │   │   └── schemas/
│   │   │       └── graph_schema.json      # Formal JSON Schema specification
│   │   │
│   │   ├── graph/
│   │   │   ├── __init__.py             # Graph package initializer
│   │   │   ├── builder.py              # NetworkX DiGraph construction from domain aggregate
│   │   │   ├── operations.py           # graph_to_json, snapshot_graph, restore_graph
│   │   │   └── traversal.py            # High-resolution BFS traversal & monotonic timer
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py             # Domain models initializer
│   │   │   ├── nodes.py                # SupplierNode, BOMPartNode, FinishedProductNode, CustomerOrderNode
│   │   │   ├── edges.py                # SuppliesEdge, UsedInEdge, FulfillsEdge
│   │   │   └── graph.py                # SupplyChainGraph domain aggregate container
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py             # Pydantic schemas initializer
│   │   │   ├── graph.py                # GraphResponseSchema, NodeResponseSchema, EdgeResponseSchema
│   │   │   ├── traversal.py            # TraversalRequestSchema, TraversalResponseSchema
│   │   │   └── validation.py           # ValidationRequestSchema, ValidationResponseSchema
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py             # Services package initializer
│   │   │   ├── graph_service.py        # Graph lifecycle, reachability, blast-radius & undo stack
│   │   │   ├── validation_service.py   # Connects API routes to validation engine
│   │   │   └── benchmark_service.py    # Traversal & graph construction telemetry
│   │   │
│   │   ├── static/
│   │   │   ├── sprint-1-demo.html      # Responsive HTML5 UI application shell
│   │   │   ├── css/
│   │   │   │   └── sprint-1-demo.css   # Dark glassmorphism stylesheet & animations
│   │   │   └── js/
│   │   │       └── sprint-1-demo.js    # D3.js force layout, drag/zoom, interactive demo
│   │   │
│   │   └── validation/
│   │       ├── __init__.py             # Clean public validation exports
│   │       ├── models.py               # Validation dataclasses, policies, and enums
│   │       ├── cycles.py               # Pure cycle detection and DAG acyclicity evaluation
│   │       ├── nodes.py                # Node records, category, and field validation
│   │       ├── edges.py                # Edge records, endpoint references, and direction rules
│   │       ├── validator.py            # High-level validation orchestrator
│   │       └── reporting.py            # ASCII console & JSON file report formatters
│   │
│   ├── reports/                        # Local output directory for benchmark & validation reports
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                 # Pytest fixtures and test graph instances
│   │   ├── fixtures/
│   │   │   └── sample_scenario.json    # Isolated unit test fixture
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_domain_models.py   # Domain model unit tests
│   │   │   ├── test_api_schemas.py     # Pydantic schema unit tests
│   │   │   ├── test_graph.py           # Graph construction & count unit tests
│   │   │   ├── test_traversal.py       # BFS reachability & cycle tests
│   │   │   ├── test_validation.py      # DAG & topological audit tests
│   │   │   └── test_edge_cases.py      # Boundary, malformed JSON & error tests
│   │   └── integration/
│   │       ├── __init__.py
│   │       └── test_api.py             # 25 end-to-end Flask API integration tests
│   └── pytest.ini                      # Pytest runner configuration
│
├── docs/                               # Comprehensive project documentation
│   ├── README.md                       # Documentation index
│   ├── architecture.md                 # System architecture and Mermaid flow diagram
│   ├── project-structure.md            # Detailed file and directory inventory
│   ├── installation-and-setup.md       # Setup, prerequisites, and virtualenv guide
│   ├── running-locally.md              # Local execution options and server commands
│   ├── configuration.md                # Environment variables and configuration
│   ├── graph-model.md                  # 4-tier DAG domain model and invariants
│   ├── validation.md                   # Modular validation engine guide
│   ├── api-reference.md                # Exhaustive REST API endpoint documentation
│   ├── frontend.md                     # D3.js frontend visualization architecture
│   ├── testing.md                      # Pytest test suite architecture and execution
│   ├── benchmarking.md                 # Traversal latency benchmarks and SLA
│   ├── deployment.md                   # Render PaaS configuration and guide
│   └── troubleshooting.md              # Debugging procedures and common issues
│
├── scripts/
│   ├── run_local.py                    # Local development server launcher
│   ├── validate_graph.py               # Standalone graph validation CLI
│   └── run_benchmarks.py               # Performance benchmarking CLI harness
├── .env.example                        # Template environment variables
├── .gitignore                          # Standard git ignore specification
├── pyproject.toml                      # Build system, package metadata & linter configuration
├── render.yaml                         # Production Render cloud deployment blueprint
└── README.md                           # Main repository documentation
```

---

## 4. Getting Started Locally

### Prerequisites
- Python 3.11+
- pip

### Installation & Environment Setup
```bash
# 1. Clone repository
git clone https://github.com/deepsandilya01/EPAM-SPRINTS.git
cd EPAM-SPRINTS

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies in editable mode
pip install -e .
```

### Running the Application
Launch the local development server:
```bash
python scripts/run_local.py
```
Or run directly through the Flask application module:
```bash
python backend/app/main.py
```
Access the application:
- **Interactive UI Demo**: [http://127.0.0.1:5050/](http://127.0.0.1:5050/)
- **Health Diagnostic Endpoint**: [http://127.0.0.1:5050/api/health](http://127.0.0.1:5050/api/health)
- **Graph Topology API**: [http://127.0.0.1:5050/api/graph](http://127.0.0.1:5050/api/graph)

---

## 5. Testing & Quality Verification

### Run Full Test Suite (129 Tests)
Execute all unit and integration tests via pytest:
```bash
pytest backend/tests -v
```

### Run Static Analysis (Ruff)
Validate formatting and linting:
```bash
ruff check backend/ scripts/
```

### Run Standalone Graph Validation CLI
Validate dataset schema, DAG acyclicity, and baseline counts from the terminal:
```bash
python scripts/validate_graph.py
```

### Run Traversal Benchmark CLI
Execute performance benchmarking across iterations:
```bash
python scripts/run_benchmarks.py --iterations 100 --warmup 10
```

---

## 6. REST API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the interactive D3.js visualization UI (`sprint-1-demo.html`). |
| `GET` | `/api/health` | Service health status, version, and live node/edge counts. |
| `GET` | `/api/graph` | Active NetworkX graph formatted for UI rendering (`nodes`, `edges`, `links`). |
| `GET` | `/api/downstream/<id>` | Downstream reachable node IDs computed via BFS traversal. |
| `GET` | `/api/impact/<id>` | Blast-radius preview, affected categories, and complexity details. |
| `POST` | `/api/traversal` | JSON request-body driven downstream reachability traversal. |
| `DELETE` | `/api/node/<id>` | Deletes node and triggers cascading removal of dependent downstream entities. |
| `POST` | `/api/undo` | Restores the previous graph state from the undo stack. |
| `POST` | `/api/reset` | Resets graph state back to the canonical 19-node baseline dataset. |
| `GET` | `/api/validation` | Runs structural validation audit (`mode=baseline` or `mode=integrity`). |
| `GET` | `/api/benchmark/tracing` | Measures traversal latency for a given node against the 10ms SLA. |
| `GET` | `/api/benchmarks` | Micro-benchmark alias for performance telemetry. |

---

## 7. Render Cloud Deployment

The application is configured for deployment exclusively on **Render** via `render.yaml`.

### Render Deployment Configuration (`render.yaml`)
```yaml
services:
  - type: web
    name: reflow
    env: python
    buildCommand: "pip install -e ."
    startCommand: "python backend/app/main.py"
    envVars:
      - key: PORT
        value: 10000
      - key: FLASK_ENV
        value: production
```

### Render Deployment Steps
1. Push repository changes to GitHub (`main` branch).
2. Connect repository to Render dashboard as a **Blueprint** or **Web Service**.
3. Render automatically executes `pip install -e .` and starts `python backend/app/main.py`.
4. The service will bind to the assigned port and serve both the REST API and the interactive D3 frontend with zero external database dependencies.
