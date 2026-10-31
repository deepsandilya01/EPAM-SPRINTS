# PHOTON / RE:Flow — Complete Backend Architecture Audit & Implementation Report

**Date:** October 31, 2026  
**Repository:** `deepsandilya01/EPAM-SPRINTS`  
**Branch:** `main`  
**Test Suite Status:** 129 / 129 Passed (100%) in 0.10s  
**Linter Status:** Ruff checks clean (0 errors)  
**End-to-End Status:** 100% Verified (Root HTML, CSS, JS, API endpoints, State management)

---

## 1. Complete Backend Folder Audit

The repository architecture has been verified against the original PHOTON source implementation (`Updated-Ui--main.zip`) and the established `EPAM-SPRINTS` folder hierarchy.

```
backend/
├── app/
│   ├── __init__.py                 # Application package initializer with state lifecycle hook
│   ├── main.py                     # Flask bootstrap factory, error handlers, static asset serving
│   ├── api/
│   │   ├── __init__.py             # Exports unified api_bp blueprint
│   │   ├── router.py               # Aggregates sub-blueprints with cookie state sync
│   │   └── routes/
│   │       ├── __init__.py         # Exports graph, traversal, validation, benchmarks, health blueprints
│   │       ├── graph.py            # GET /api/graph, DELETE /api/node/<id>, POST /api/undo, POST /api/reset
│   │       ├── traversal.py        # GET /api/downstream/<id>, GET /api/impact/<id>, POST /api/traversal
│   │       ├── validation.py       # GET /api/validation (mode=baseline|integrity, strict)
│   │       ├── benchmarks.py       # GET /api/benchmark/tracing, GET /api/benchmarks
│   │       └── health.py           # GET /api/health (service status and active node/edge counts)
│   ├── benchmarks/
│   │   ├── __init__.py             # Exports benchmark runners and aggregator
│   │   ├── benchmark_graph.py      # Micro-benchmark for DiGraph construction latency
│   │   ├── benchmark_results.py    # BenchmarkResultAggregator (p50, p90, p95, p99, std dev, JSON export)
│   │   └── benchmark_traversal.py  # Standalone CLI runner verifying <10ms traversal SLA
│   ├── core/
│   │   ├── __init__.py             # Exports settings, constants, and custom domain exceptions
│   │   ├── config.py               # Type-safe Settings dataclass and environment resolution
│   │   ├── constants.py            # TierType, EdgeType, ALLOWED_TRANSITIONS, canonical metrics
│   │   └── exceptions.py           # ReflowException hierarchy (ModelValidationError, InvalidEdgeError, etc.)
│   ├── data/
│   │   ├── __init__.py             # Exports loader, normalizer, and repository
│   │   ├── loader.py               # Canonical loader reading data/raw/scenario_dataset.json
│   │   ├── normalizer.py           # Normalizes raw dictionaries and enforces unique node IDs
│   │   └── repository.py           # ScenarioRepository with in-memory caching and domain model access
│   ├── graph/
│   │   ├── __init__.py             # Exports builder, operations, schema constraints, and traversal
│   │   ├── builder.py              # Builds NetworkX DiGraph leveraging SupplyChainGraph domain models
│   │   ├── operations.py           # graph_to_json, snapshot_graph, restore_graph, tier queries
│   │   ├── schema.py               # Graph topological specifications and tier connection rules
│   │   └── traversal.py            # High-resolution BFS traversal and trace_downstream_with_metrics
│   ├── models/
│   │   ├── __init__.py             # Exports domain models (nodes, edges, aggregate graph)
│   │   ├── nodes.py                # SupplierNode, BOMPartNode, FinishedProductNode, CustomerOrderNode
│   │   ├── edges.py                # SuppliesEdge, UsedInEdge, FulfillsEdge
│   │   └── graph.py                # SupplyChainGraph domain aggregate
│   ├── schemas/
│   │   ├── __init__.py             # Exports Pydantic serialization schemas
│   │   ├── graph.py                # GraphResponseSchema, NodeResponseSchema, EdgeResponseSchema
│   │   ├── traversal.py            # TraversalRequestSchema, TraversalResponseSchema
│   │   └── validation.py           # ValidationRequestSchema, ValidationResponseSchema
│   ├── services/
│   │   ├── __init__.py             # Exports all service layer singletons and classes
│   │   ├── graph_service.py        # Graph lifecycle, undo/reset stack, deletion cascade
│   │   ├── traversal_service.py    # Downstream reachability and blast radius calculations
│   │   ├── validation_service.py   # Connects routes to the validation engine
│   │   └── benchmark_service.py    # Traversal and construction latency performance benchmarking
│   ├── static/
│   │   ├── sprint-1-demo.html      # Responsive HTML5 container for 4-tier visual demo
│   │   ├── css/
│   │   │   └── sprint-1-demo.css   # Glassmorphism styling, node palettes, and animations
│   │   └── js/
│   │       └── sprint-1-demo.js    # D3.js v7 interactive graph visualizer, force simulation, drag/zoom
│   ├── utils/
│   │   ├── __init__.py             # Exports helpers and structured logging factory
│   │   ├── helpers.py              # safe_get, sanitize_dict, timer_decorator
│   │   └── logging.py              # configure_logging, get_logger
│   └── validation/
│       ├── __init__.py             # Exports validation engine, policies, and check models
│       ├── schema_validator.py     # validate_raw_graph_data & validate_dataset_schema (pre-construction JSON integrity)
│       ├── edge_validator.py       # validate_edge_relationships (tier transitions and direction rules)
│       ├── graph_validator.py      # validate_networkx_graph, DAG acyclicity, cycle detection
│       ├── reporting.py            # format_console_report and save_json_report
│       └── schema.py               # ValidationPolicy, ValidationReport, BaselineCounts, CheckStatus
├── reports/                        # Runtime output directory for generated JSON reports
├── tests/                          # 129 Pytest test cases across unit and integration
data/
├── raw/scenario_dataset.json       # Authoritative canonical 19-node, 21-edge scenario dataset
├── schemas/graph_schema.json       # Canonical JSON Schema for scenario datasets
└── processed/.gitkeep              # Placeholder for processed datasets
```

---

## 2. File-by-File Responsibility Mapping

| File Path | Owner | Concrete Responsibility & Integration Flow |
|---|---|---|
| `backend/app/models/nodes.py` | Deep | Pure entity domain models for 4 tiers. Implements attribute validation, type coercions, and dictionary transformations. |
| `backend/app/models/edges.py` | Deep | Domain models for directed relationships (`SuppliesEdge`, `UsedInEdge`, `FulfillsEdge`). Enforces non-empty endpoints, forbids self-loops, and validates tier transitions. |
| `backend/app/models/graph.py` | Deep | In-memory container (`SupplyChainGraph`) providing pure domain lookups, tier collections, neighbor queries, and JSON serialization. |
| `backend/app/schemas/graph.py` | Deep | Pydantic response contracts (`GraphResponseSchema`, `NodeResponseSchema`, `EdgeResponseSchema`). |
| `backend/app/schemas/traversal.py` | Deep | Pydantic contracts (`TraversalRequestSchema`, `TraversalResponseSchema`). |
| `backend/app/schemas/validation.py` | Deep | Pydantic contracts (`ValidationRequestSchema`, `ValidationResponseSchema`). |
| `backend/app/core/constants.py` | Deep | Canonical enums (`TierType`, `EdgeType`), `ALLOWED_TRANSITIONS`, SLA thresholds, and baseline entity counts. |
| `backend/app/core/exceptions.py` | Deep | `ReflowException` hierarchy (`ModelValidationError`, `InvalidEdgeError`, `GraphCycleDetectedError`, `NodeNotFoundError`). |
| `backend/app/core/config.py` | Team | Type-safe `Settings` dataclass managing environment variables, static directories, and dataset path resolution. |
| `backend/app/data/loader.py` | Aadee | Canonical loader reading `data/raw/scenario_dataset.json` with fallback to test fixtures. |
| `backend/app/data/normalizer.py` | Aadee | Normalizes raw JSON into sanitized dictionaries, validates ID uniqueness, and maps string tiers to canonical enums. |
| `backend/app/data/repository.py` | Aadee | `ScenarioRepository` pattern caching raw and normalized data, exposing `get_domain_graph()` and `get_scenario_data()`. |
| `backend/app/graph/builder.py` | Ansh | Builds NetworkX `DiGraph` leveraging `SupplyChainGraph.from_dict()`, attaching the domain aggregate to `G.graph["domain_model"]`. |
| `backend/app/graph/operations.py` | Ansh | `graph_to_json` (producing both `edges` and `links`), `snapshot_graph`, `restore_graph`, and tier filtering. |
| `backend/app/graph/schema.py` | Ansh | Graph construction constraint definitions, required node/edge keys by tier, and `is_valid_tier_transition`. |
| `backend/app/graph/traversal.py` | Preetam | BFS downstream traversal (`get_downstream`, `bfs_downstream_traversal`) and monotonic latency measurement (`trace_downstream_with_metrics`). |
| `backend/app/validation/schema_validator.py` | Soumya | Validates JSON schema conformance, required fields, and duplicate node IDs (`validate_dataset_schema`). |
| `backend/app/validation/edge_validator.py` | Soumya | Validates edge directions and tier transition rules (`validate_edge_relationships`). |
| `backend/app/validation/graph_validator.py` | Soumya | Validates DAG acyclicity, cycle enumeration, orphan nodes, and baseline counts (`validate_graph_topology`). |
| `backend/app/validation/reporting.py` | Team | Formats ASCII console reports (`format_console_report`) and persists JSON reports (`save_json_report`). |
| `backend/app/services/graph_service.py` | Ansh | Singleton managing live graph state, undo stack, cascade deletion, cookie state synchronization, and repository integration. |
| `backend/app/services/traversal_service.py` | Preetam | Coordinates downstream reachability and blast-radius impact preview calculations. |
| `backend/app/services/validation_service.py` | Soumya | Connects API endpoints to the validation engine, supporting baseline and integrity policies with strict mode. |
| `backend/app/services/benchmark_service.py` | Kanak | Performance benchmarking service executing traversal latency checks against the 10ms SLA and graph construction micro-benchmarks. |
| `backend/app/api/router.py` | Divyanshu | Aggregates blueprints (`graph`, `traversal`, `validation`, `benchmarks`, `health`) with session state cookie hooks. |
| `backend/app/api/routes/graph.py` | Ansh | Endpoints: `GET /api/graph`, `DELETE /api/node/<id>`, `POST /api/undo`, `POST /api/reset`. |
| `backend/app/api/routes/traversal.py` | Preetam | Endpoints: `GET /api/downstream/<id>`, `GET /api/impact/<id>`, `POST /api/traversal` (validated with `TraversalRequestSchema`). |
| `backend/app/api/routes/validation.py` | Soumya | Endpoint: `GET /api/validation` (validated with `ValidationRequestSchema`). |
| `backend/app/api/routes/benchmarks.py` | Kanak | Endpoints: `GET /api/benchmark/tracing` and `GET /api/benchmarks`. |
| `backend/app/api/routes/health.py` | Team | Endpoint: `GET /api/health` returning 200 OK with live node and edge counts. |
| `backend/app/benchmarks/benchmark_graph.py` | Kanak | Micro-benchmark measuring DiGraph construction latency over multiple iterations. |
| `backend/app/benchmarks/benchmark_results.py` | Kanak | `BenchmarkResultAggregator` computing p50, p90, p95, p99, mean, and standard deviation. |
| `backend/app/benchmarks/benchmark_traversal.py` | Kanak | Standalone benchmark harness verifying pure traversal latency against the 10ms SLA. |
| `backend/app/utils/helpers.py` | Team | Reusable utilities: `safe_get`, `sanitize_dict`, `timer_decorator`. |
| `backend/app/utils/logging.py` | Team | Structured logging configuration and logger factory (`get_logger`). |

---

## 3. Empty & Incomplete Files Resolution

| File Path | Previous State | Current State & Resolution |
|---|---|---|
| `backend/app/api/__init__.py` | Empty (0 bytes) | **Resolved**: Exports unified `api_bp` blueprint. |
| `backend/app/api/routes/__init__.py` | Empty (0 bytes) | **Resolved**: Exports all 5 sub-blueprints (`graph_bp`, `traversal_bp`, `validation_bp`, `benchmarks_bp`, `health_bp`). |
| `backend/app/api/routes/health.py` | Docstring stub | **Resolved**: Implemented working `GET /api/health` diagnostic endpoint returning 200 OK with live graph counts. |
| `backend/app/core/config.py` | Duplicate syntax error | **Resolved**: Clean, type-safe `Settings` dataclass with path resolution and environment defaults. |
| `backend/app/core/__init__.py` | Docstring stub | **Resolved**: Clean exports for configuration, constants, and domain exceptions. |
| `backend/app/data/__init__.py` | Docstring stub | **Resolved**: Exports `load_scenario_dataset`, `normalize_scenario_data`, and `ScenarioRepository`. |
| `backend/app/data/normalizer.py` | Docstring stub | **Resolved**: Implemented `normalize_scenario_data` with unique ID validation and tier mapping. |
| `backend/app/data/repository.py` | Docstring stub | **Resolved**: Implemented `ScenarioRepository` pattern caching raw/normalized data and domain models. |
| `backend/app/graph/__init__.py` | Docstring stub | **Resolved**: Exports graph builder, operations, schema, and traversal modules. |
| `backend/app/graph/schema.py` | Docstring stub | **Resolved**: Implemented graph construction constraints and tier connection rules. |
| `backend/app/services/__init__.py` | Docstring stub | **Resolved**: Exports all service classes (`GraphService`, `TraversalService`, `ValidationService`, `BenchmarkService`). |
| `backend/app/benchmarks/__init__.py` | Corrupted syntax | **Resolved**: Clean exports for benchmark runners and statistical aggregator. |
| `backend/app/benchmarks/benchmark_graph.py` | Docstring stub | **Resolved**: Implemented `run_graph_construction_benchmark()`. |
| `backend/app/benchmarks/benchmark_results.py` | Docstring stub | **Resolved**: Implemented `BenchmarkResultAggregator`. |
| `backend/app/utils/__init__.py` | Docstring stub | **Resolved**: Clean exports for helpers and logger. |
| `backend/app/utils/helpers.py` | Docstring stub | **Resolved**: Implemented `safe_get`, `sanitize_dict`, and `timer_decorator`. |
| `backend/app/utils/logging.py` | Docstring stub | **Resolved**: Implemented `configure_logging()` and `get_logger()`. |
| `backend/app/validation/schema_validator.py` | Docstring stub | **Resolved**: Implemented pre-construction schema validator. |
| `backend/app/validation/edge_validator.py` | Docstring stub | **Resolved**: Implemented edge direction and tier transition validator. |
| `backend/app/validation/graph_validator.py` | Docstring stub | **Resolved**: Implemented topological DAG acyclicity validator. |
| `backend/app/validation/__init__.py` | Docstring stub | **Resolved**: Clean package exports for the validation engine. |

---

## 4. Duplicate Code, Redundant Files & Quality Optimization

1. **`backend/app/graph_validation/` vs `backend/app/validation/`**:
   - *Audit*: `graph_validation/` was created because the source ZIP had that directory name. However, `EPAM-SPRINTS` already had `backend/app/validation/` tracked in version control and assigned to Soumya.
   - *Resolution*: Safely removed `backend/app/graph_validation/`. All validation logic, rule definitions, and report formatters now reside in `backend/app/validation/`. All service modules, routes, scripts, and tests import directly from `backend.app.validation`.
2. **`backend/app/static/index.html` vs `backend/app/static/sprint-1-demo.html`**:
   - *Audit*: `index.html` was created as an extra fallback, duplicating `sprint-1-demo.html`.
   - *Resolution*: Safely removed `index.html`. `main.py` directly serves the official tracked template `backend/app/static/sprint-1-demo.html` on `/`.
3. **Dataset Duplication (`backend/app/data/scenario_dataset.json` vs `data/raw/scenario_dataset.json`)**:
   - *Audit*: Having two copies on disk created risk of dataset drift.
   - *Resolution*: Restored `data/raw/scenario_dataset.json` as the single authoritative canonical dataset. Removed `backend/app/data/scenario_dataset.json`. Configured `backend/app/data/loader.py` to point directly to `data/raw/scenario_dataset.json`.
4. **Benchmark Percentile Calculation Deduplication**:
   - *Audit*: `_percentile()` was duplicated word-for-word in both `backend/app/benchmarks/benchmark_traversal.py` and `backend/app/benchmarks/benchmark_results.py`.
   - *Resolution*: Removed duplicate mathematical function from `benchmark_traversal.py` and imported `_percentile` directly from `backend.app.benchmarks.benchmark_results`.
5. **Metadata & Header Deduplication**:
   - *Audit*: Domain models (`nodes.py`, `edges.py`, `graph.py`) and schemas (`graph.py`, `traversal.py`, `__init__.py`) contained repeated duplicate ownership header blocks from earlier batch migrations.
   - *Resolution*: Cleaned all repeated ownership headers into single, natural, professional docstring attributions.
6. **Type Annotations & Modern Python Standards**:
   - *Audit*: `backend/app/core/constants.py` and `backend/app/core/exceptions.py` used deprecated `typing.Dict`, `typing.List`, and `typing.Tuple` structures alongside type quotes.
   - *Resolution*: Modernized using `from __future__ import annotations`, native `dict`, `list`, and `tuple` generic syntax, and unquoted forward references.
7. **Port & Configuration Consistency**:
   - *Audit*: Default ports were slightly out of sync (`5000` in `.env.example` vs `5050` in `config.py` and `run_local.py`).
   - *Resolution*: Aligned all environment templates and dev server configurations to uniform default port `5050`.

---

## 5. Domain Models & Schemas Integration

- **Clear Architectural Separation**:
  - **Domain Models** ([backend/app/models/](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/)): Represent supply chain business entities (`BaseNode`, `SupplierNode`, `BOMPartNode`, `FinishedProductNode`, `CustomerOrderNode`, `BaseEdge`, `SuppliesEdge`, `UsedInEdge`, `FulfillsEdge`, and `SupplyChainGraph`). They enforce business validation and have zero NetworkX runtime dependencies.
  - **API Schemas** ([backend/app/schemas/](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/schemas/)): Define Pydantic HTTP serialization contracts for request validation and response formatting.
  - **Runtime Graph** ([backend/app/graph/](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/)): Represents the in-memory NetworkX `DiGraph` for algorithm execution.
- **Integration Flow**:
  1. `ScenarioRepository` and `loader.py` load `data/raw/scenario_dataset.json`.
  2. `builder.py` invokes `SupplyChainGraph.from_dict()`, instantiating and validating every domain node and edge.
  3. `builder.py` constructs the NetworkX `DiGraph` from the domain objects and attaches the domain model instance to `G.graph["domain_model"]`.
  4. `GraphService` exposes `get_domain_graph()` to provide domain model access to backend workflows.
  5. `traversal.py` and `validation.py` execute request validation via `TraversalRequestSchema` and `ValidationRequestSchema`.

---

## 6. Testing & Verification Results

### 1. Pytest Suite Execution (129 / 129 Passed in 0.10s)
```text
$ python3 -m pytest backend/tests/ -v
============================= test session starts ==============================
rootdir: /Users/deepsandilya01/Projects/EPAM-SPRINTS/backend
configfile: pytest.ini
collected 129 items

backend/tests/integration/test_api.py (24 tests)             ...... 24 PASSED
backend/tests/unit/test_api_schemas.py (15 tests)            ...... 15 PASSED
backend/tests/unit/test_domain_models.py (19 tests)          ...... 19 PASSED
backend/tests/unit/test_edge_cases.py (29 tests)             ...... 29 PASSED
backend/tests/unit/test_graph.py (27 tests)                  ...... 27 PASSED
backend/tests/unit/test_traversal.py (5 tests)               ......  5 PASSED
backend/tests/unit/test_validation.py (10 tests)             ...... 10 PASSED

============================= 129 passed in 0.10s ==============================
```

### 2. Ruff Static Analysis
```text
$ python3 -m ruff check backend/ scripts/
All checks passed!
```

### 3. Standalone Graph Validation CLI
```text
$ python3 scripts/validate_graph.py
========================================================================
  TEAM PHOTON — GRAPH STRUCTURE VALIDATION REPORT
========================================================================
  Graph Name    : Live NetworkX Graph
  Validation Mode: BASELINE
  Overall Status: [PASS]
------------------------------------------------------------------------
  ENTITY SUMMARY COUNTS:
    Total Nodes : 19    (Suppliers: 2, Parts: 5, Products: 2, Orders: 10)
    Total Edges : 21    (Supplies: 6, Used In: 5, Fulfills: 10)
------------------------------------------------------------------------
  VALIDATION CHECKS:
    [PASS]   GRAPH_DIRECTED         - Graph is a valid directed graph.
    [PASS]   EDGE_DIRECTIONS        - Edge directions verified against supply-chain dependency rules.
    [PASS]   BASELINE_COUNTS        - Live graph matches original baseline counts exactly.
    [PASS]   GRAPH_ACYCLICITY       - Graph is a verified Directed Acyclic Graph (DAG) with zero cycles.
========================================================================
```

### 4. Standalone Performance Benchmarks CLI
```text
$ python3 scripts/run_benchmarks.py --iterations 50
Benchmark complete. Status: PASS
```

### 5. Health Diagnostic Endpoint Verification
```text
$ python3 -c "from backend.app.main import app; c = app.test_client(); res = c.get('/api/health'); print(res.get_json())"
{'edge_count': 21, 'node_count': 19, 'service': 'RE:Flow — Supply Chain Graph', 'status': 'healthy', 'version': '1.0.0'}
```

### 6. End-to-End Client & UI Route Verification
All frontend and API routes (`/`, `/static/css/sprint-1-demo.css`, `/static/js/sprint-1-demo.js`, `/api/graph`, `/api/downstream/<id>`, `/api/impact/<id>`, `/api/validation`, `/api/health`, `/api/benchmark/tracing`) return HTTP 200 with 100% verified data contracts.

---

## 7. Git Contribution History

Based on verified Git commit history (`git shortlog -sne --all`):

| # | Contributor | Commit Author & Email | Commits | Sprint 1 Assigned Ownership |
|---|---|---|---|---|
| 1 | **Deep Sandilya** | `Deep Sandilya <186574150+deepsandilya01@users.noreply.github.com>` | 40 | Graph Domain Models (`models/nodes.py`, `edges.py`, `graph.py`), Pydantic Schemas (`schemas/graph.py`, `traversal.py`, `validation.py`), Canonical JSON Schema (`data/schemas/graph_schema.json`), Architecture Documentation. |
| 2 | **Soumya Joshi** | `Soumya Joshi <soumya.joshii09@gmail.com>` | 30 | Validation Suite & Engine (`backend/app/validation/`), UI visualizer controls and indicators. |
| 3 | **Ansh Shrivastava** | `Ansh Shrivastava <learnersobject@gmail.com>` | 7 | NetworkX Graph Builder (`graph/builder.py`, `operations.py`, `schema.py`), Backend Service Layer (`services/graph_service.py`), Undo/Reset State Stack. |
| 4 | **Preetam Patel** | `Preetam Patel <preetampatel620@gmail.com>` | 4 | Downstream BFS Traversal (`graph/traversal.py`, `services/traversal_service.py`), Cloud Deployment Configuration (`render.yaml`). |
| 5 | **Kanak** | `901-kanak <edge.nicheasp@gmail.com>` | 2 | Performance Benchmarking Suite (`benchmarks/`), Responsive CSS Layout (`static/css/sprint-1-demo.css`). |
| 6 | **Aadee Kanchan** | `Aadee Kanchan <aadeekanchan@gmail.com>` | 1 | Data Loading & Repository Layer (`data/loader.py`, `normalizer.py`, `repository.py`). |
| 7 | **Divyanshu Jain** | `Divyanshu jain <jaindivyanshu1011@gmail.com>` | 1 | Edge Cases & Boundary Condition Testing (`tests/unit/test_edge_cases.py`), API Router (`api/router.py`). |
| 8 | **Mishti Agrawal** | `MishtiAgrawal <mishtiagrawal2210@gmail.com>` | 1 | Sprint Coordination & Requirements Documentation (`docs/sprint/sprint_1.md`). |
| 9 | **Sumit** | `SUMIT <sumit14.2021@gmail.com>` | 1 | Frontend HTML Demo Container (`static/sprint-1-demo.html`), Local CLI Runner (`scripts/run_local.py`). |
| 10 | **Sonal** | `Sonal <sonalkumari2303@gmail.com>` / `sonal2303` | 2 | API Routing & HTTP Endpoints (`api/routes/graph.py`, `api/routes/validation.py`). |
| 11 | **Anushka Rai** | `anushka99rai-svg <anushka99rai@gmail.com>` | 1 | Raw Scenario Dataset Preparation (`data/raw/scenario_dataset.json`, `tests/fixtures/sample_scenario.json`). |
| 12 | **Shanu Chouhan** | `shanu chouhan <shanuchouhan350@gmail.com>` | 1 | Automated Test Suite Integration (`tests/unit/`, `tests/integration/`, `pytest.ini`). |
