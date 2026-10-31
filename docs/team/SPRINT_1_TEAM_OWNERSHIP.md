# RE:Flow — Sprint 1 Central Team Ownership Document

> **Document Version**: 1.0.0  
> **Sprint**: Sprint 1 — Supply Chain Graph & Scenario Generator  
> **Status**: APPROVED / ACTIVE  
> **Last Updated**: 2026-10-31  

---

## 1. Executive Summary

This central document defines the roles, file ownership, primary responsibilities, deliverables, dependencies, and execution status for all **12 team members** participating in **RE:Flow Sprint 1**.

RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.

Sprint 1 focuses on building the core Supply Chain Graph representation (NetworkX `DiGraph`), dataset ingestion, BFS downstream impact traversal, multi-tier validation, automated testing, benchmarking, and a static browser demonstration.

---

## 2. Team Member Ownership Profiles

### Member 1 — Mishti
- **Role**: Sprint Coordinator and Requirements Management
- **Primary Assigned Files**:
  - `docs/sprint/sprint_1.md`
- **Supporting Areas**:
  - Task progress tracking, dependency unblocking, acceptance verification across all phases.
- **Exact Responsibilities**:
  1. Document and maintain Sprint 1 objectives, scope, and timeline.
  2. Define rigorous acceptance criteria for all 12 modules.
  3. Maintain task progress, daily burndown tracking, and blocker resolution.
  4. Coordinate inter-member handoffs across all 7 execution phases.
  5. Audit overall Sprint 1 completion readiness prior to final sign-off.
- **Expected Deliverables**:
  - Completed `docs/sprint/sprint_1.md` with finalized scope and acceptance checklist.
  - Weekly task alignment and dependency log.
- **Dependencies**:
  - Deep (Domain Models & Data Contracts).
  - Sumit (Documentation and Demo Guide).
- **Task Status**: `NOT STARTED`

---

### Member 2 — Deep
- **Role**: Graph Domain Models and Data Contracts (Sprint 1 Implementation Completed)
- **Completed Implementation Files**:
  - `backend/app/models/nodes.py`
  - `backend/app/models/edges.py`
  - `backend/app/models/graph.py`
  - `backend/app/models/__init__.py`
  - `backend/app/schemas/graph.py`
  - `backend/app/schemas/traversal.py`
  - `backend/app/schemas/validation.py`
  - `backend/app/schemas/__init__.py`
  - `backend/app/core/constants.py`
  - `backend/app/core/exceptions.py`
  - `data/schemas/graph_schema.json` *(companion: `data/schemas/README.md`)*
  - `docs/architecture/graph_schema.md`
- **Current Maintenance Ownership**:
  - `Team Maintained`
- **Core Repository Scaffolding (Team Maintained)**:
  - `backend/app/core/config.py`
  - `backend/app/core/__init__.py`
  - `backend/app/main.py`
  - `backend/app/api/router.py`
  - `backend/app/api/routes/health.py`
  - `backend/app/api/__init__.py`
  - `backend/app/api/routes/__init__.py`
  - `backend/app/utils/logging.py`
  - `backend/app/utils/helpers.py`
  - `backend/app/utils/__init__.py`
  - `backend/app/__init__.py`
  - `.env.example`
  - `.gitignore`
  - `pyproject.toml`
  - `render.yaml`
  - `scripts/run_local.py`
- **Supporting Areas**:
  - Graph construction contracts with Ansh.
  - Data ingestion normalization with Aadee.
  - Traversal schemas with Preetam.
  - Validation schemas with Soumya.
  - Render deployment and server configuration.
- **Exact Responsibilities (Completed in Sprint 1)**:
  1. Defined domain models for Suppliers, BOM Parts, Finished Products, and Customer Orders.
  2. Defined directed dependency edge models (`SUPPLIES`, `USED_IN`, `FULFILLS`).
  3. Defined unified graph domain representation (`SupplyChainGraph`).
  4. Defined Pydantic request and response serialization schemas for all REST endpoints.
  5. Authored the canonical JSON Schema (`data/schemas/graph_schema.json`).
  6. Documented the canonical graph specification in `docs/architecture/graph_schema.md`.
  7. Contributed to core domain constants and custom exceptions.
- **Deliverables**:
  - Complete, strongly-typed domain model layer in `backend/app/models/` (COMPLETED).
  - Complete request/response schemas in `backend/app/schemas/` (COMPLETED).
  - JSON schema specification in `data/schemas/graph_schema.json` (COMPLETED).
  - 34 passing unit tests verifying models and schemas (COMPLETED).
- **Dependencies**:
  - Anushka (Approved scenario dataset attributes).
  - Mishti (Baseline requirements: 19 nodes, 21 edges).
- **Task Status**: `COMPLETED` (Sprint 1 Implementation Delivered; Ongoing maintenance: Team Maintained)

---

### Member 3 — Anushka
- **Role**: Scenario Dataset Preparation
- **Primary Assigned Files**:
  - `data/raw/scenario_dataset.json` *(companion: `data/raw/README.md`)*
  - `backend/tests/fixtures/sample_scenario.json` *(companion: `backend/tests/fixtures/README.md`)*
  - `data/processed/.gitkeep`
- **Supporting Areas**:
  - Mapping verification with Sonal.
  - Ingestion formatting with Aadee.
  - Test fixture provisioning with Shanu.
- **Exact Responsibilities**:
  1. Prepare the canonical Sprint 1 baseline supply chain dataset.
  2. Populate exactly:
     - 2 Suppliers
     - 5 BOM Parts
     - 2 Finished Products
     - 10 Customer Orders
     - Total: 19 Nodes
     - Total: 21 Directed Edges
  3. Strictly verify directed relationship types:
     - `SUPPLIES`: Supplier -> BOM Part
     - `USED_IN`: BOM Part -> Finished Product
     - `FULFILLS`: Finished Product -> Customer Order
  4. Ensure all node and edge attribute dictionaries match Deep's schema contracts.
  5. Do NOT invent unapproved records or arbitrary relationships.
- **Expected Deliverables**:
  - Syntactically valid, validated `data/raw/scenario_dataset.json`.
  - Immutable test fixture `backend/tests/fixtures/sample_scenario.json`.
- **Dependencies**:
  - Deep (Schema and attribute requirements).
  - Aadee (Loader format expectations).
- **Task Status**: `NOT STARTED`

---

### Member 4 — Ansh
- **Role**: NetworkX Graph Builder
- **Primary Assigned Files**:
  - `backend/app/graph/schema.py`
  - `backend/app/graph/builder.py`
  - `backend/app/graph/operations.py`
  - `backend/app/services/graph_service.py`
  - `backend/app/api/routes/graph.py`
  - `backend/app/graph/__init__.py`
- **Supporting Areas**:
  - Traversal engine graph integration with Preetam.
  - Topological validation with Soumya.
  - Graph construction benchmarking with Kanak.
- **Exact Responsibilities**:
  1. Define graph construction constraints and tier transition rules.
  2. Assemble a `networkx.DiGraph` from normalized scenario records.
  3. Attach all node attributes and edge metadata accurately.
  4. Implement reusable graph operations (subgraph extraction, degree calculation, tier filtering).
  5. Implement `GraphService` managing graph singleton lifecycle and caching.
  6. Implement `GET /api/graph` endpoint returning serialized graph topology.
- **Expected Deliverables**:
  - Verified `build_supply_chain_graph()` returning populated `nx.DiGraph`.
  - Complete `GraphService` with thread-safe cached access.
  - Working `GET /api/graph` REST API route.
- **Dependencies**:
  - Deep (Graph models and response schemas).
  - Aadee (Normalized data from repository).
  - Anushka (Canonical scenario dataset).
- **Task Status**: `NOT STARTED`

---

### Member 5 — Aadee
- **Role**: Data Loading and Normalization
- **Primary Assigned Files**:
  - `backend/app/data/loader.py`
  - `backend/app/data/normalizer.py`
  - `backend/app/data/repository.py`
  - `backend/app/data/__init__.py`
- **Supporting Areas**:
  - Dataset formatting with Anushka.
  - Builder input contracts with Ansh.
  - Schema validation integration with Soumya.
- **Exact Responsibilities**:
  1. Implement robust file loading from `data/raw/scenario_dataset.json` with JSON error handling.
  2. Implement data normalizer sanitizing raw keys, casting types, and validating ID uniqueness.
  3. Implement `ScenarioRepository` pattern decoupling data storage from business logic.
  4. Handle missing files, malformed JSON, and empty records with informative exceptions.
- **Expected Deliverables**:
  - Reliable `load_scenario_dataset()` and `normalize_scenario_data()` modules.
  - Complete `ScenarioRepository` providing cached, validated record access.
- **Dependencies**:
  - Anushka (Raw JSON dataset).
  - Deep (Domain constants and model definitions).
- **Task Status**: `NOT STARTED`

---

### Member 6 — Preetam
- **Role**: Graph Traversal and BFS
- **Primary Assigned Files**:
  - `backend/app/graph/traversal.py`
  - `backend/app/services/traversal_service.py`
  - `backend/app/api/routes/traversal.py`
- **Supporting Areas**:
  - Traversal complexity analysis with Divyanshu.
  - Latency SLA benchmarking (<10ms) with Kanak.
  - Traversal unit test coverage with Shanu.
- **Exact Responsibilities**:
  1. Implement breadth-first search (BFS) downstream traversal on `nx.DiGraph`.
  2. Discover all reachable downstream dependencies from any starting node (supplier, part, or product).
  3. Track directed dependency paths and hop depth.
  4. Categorize blast-radius results by tier (BOM parts, finished products, customer orders).
  5. Handle unknown/invalid starting node IDs by raising `NodeNotFoundError`.
  6. Implement `POST /api/traversal` endpoint returning structured impact analysis.
- **Expected Deliverables**:
  - High-performance BFS traversal engine executing in <10 ms.
  - Complete `TraversalService` and `POST /api/traversal` endpoint.
- **Dependencies**:
  - Ansh (Populated NetworkX graph object).
  - Deep (Traversal request/response schemas).
- **Task Status**: `NOT STARTED`

---

### Member 7 — Sonal
- **Role**: Supply Chain Mapping Verification
- **Primary Assigned Files**:
  - `docs/reports/mapping_verification.md`
- **Supporting Areas**:
  - Scenario dataset auditing with Anushka.
  - Edge validation rules with Soumya.
  - Schema contract consistency with Deep.
- **Exact Responsibilities**:
  1. Audit all 21 directed edges in the baseline scenario against physical supply chain logic.
  2. Verify Supplier -> BOM Part (`SUPPLIES`) links.
  3. Verify BOM Part -> Finished Product (`USED_IN`) links.
  4. Verify Finished Product -> Customer Order (`FULFILLS`) links.
  5. Detect and log any inverted edges, cross-tier skipping, or missing connections.
  6. Maintain comprehensive mapping verification matrices.
- **Expected Deliverables**:
  - Completed `docs/reports/mapping_verification.md` with complete edge verification matrix and sign-off.
- **Dependencies**:
  - Anushka (Dataset records).
  - Deep (Graph schema definition).
  - Ansh (Graph construction logic).
- **Task Status**: `NOT STARTED`

---

### Member 8 — Soumya
- **Role**: Graph and Data Validation
- **Primary Assigned Files**:
  - `backend/app/validation/graph_validator.py`
  - `backend/app/validation/schema_validator.py`
  - `backend/app/validation/edge_validator.py`
  - `backend/app/services/validation_service.py`
  - `backend/app/api/routes/validation.py`
  - `backend/app/validation/__init__.py`
  - `docs/reports/validation_report.md`
  - `scripts/validate_graph.py`
- **Supporting Areas**:
  - Validation unit tests with Shanu.
  - Topological cycle detection with Ansh.
  - Validation schemas with Deep.
- **Exact Responsibilities**:
  1. Implement DAG acyclicity verification and exact cycle detection.
  2. Implement JSON schema conformance validator against `graph_schema.json`.
  3. Implement edge constraint validator enforcing strict tier-to-tier connections.
  4. Implement `ValidationService` aggregating all audit rules into a structured report.
  5. Implement `GET /api/validation` REST endpoint.
  6. Author `scripts/validate_graph.py` CLI script and `docs/reports/validation_report.md`.
- **Expected Deliverables**:
  - Complete validation suite (`graph_validator`, `schema_validator`, `edge_validator`).
  - `ValidationService` and `GET /api/validation` endpoint.
  - Standalone validation CLI runner and formal documentation report.
- **Dependencies**:
  - Deep (Validation schemas and graph schema JSON).
  - Ansh (NetworkX graph object).
  - Anushka (Raw dataset).
- **Task Status**: `NOT STARTED`

---

### Member 9 — Divyanshu
- **Role**: Edge Cases and Complexity Analysis
- **Primary Assigned Files**:
  - `backend/tests/unit/test_edge_cases.py`
  - `docs/reports/complexity_analysis.md`
- **Supporting Areas**:
  - Traversal boundary handling with Preetam.
  - Validation edge cases with Soumya.
  - Test harness integration with Shanu.
- **Exact Responsibilities**:
  1. Identify boundary conditions and failure modes for graph construction, traversal, and validation.
  2. Write unit tests covering:
     - Empty graphs and empty datasets.
     - Non-existent or malformed start node IDs.
     - Disconnected components and isolated nodes.
     - Injected circular dependencies and self-loops.
  3. Perform formal algorithmic asymptotic analysis for time and space complexity:
     - BFS Traversal: O(V + E) time, O(V) space.
     - Graph Construction: O(V + E) time, O(V + E) space.
     - Cycle Detection: O(V + E) time.
  4. Author `docs/reports/complexity_analysis.md`.
- **Expected Deliverables**:
  - Robust edge case test suite in `backend/tests/unit/test_edge_cases.py`.
  - Comprehensive complexity analysis documentation.
- **Dependencies**:
  - Preetam (Traversal algorithm).
  - Ansh (Graph builder).
  - Soumya (Validation rules).
  - Shanu (Test fixtures).
- **Task Status**: `NOT STARTED`

---

### Member 10 — Shanu
- **Role**: Automated Testing and Integration Testing
- **Primary Assigned Files**:
  - `backend/tests/conftest.py`
  - `backend/tests/unit/test_graph.py`
  - `backend/tests/unit/test_traversal.py`
  - `backend/tests/unit/test_validation.py`
  - `backend/tests/integration/test_api.py`
  - `backend/pytest.ini`
  - `backend/tests/__init__.py`
  - `backend/tests/unit/__init__.py`
  - `backend/tests/integration/__init__.py`
- **Supporting Areas**:
  - Test fixtures for all module developers.
  - CI test automation and failure reporting.
- **Exact Responsibilities**:
  1. Configure `backend/pytest.ini` with testpaths, markers, and options.
  2. Build reusable Pytest fixtures in `conftest.py` (graph fixture, raw data fixture, Flask test client).
  3. Author unit tests for graph structure, node/edge counts (19 nodes, 21 edges).
  4. Author unit tests for BFS downstream traversal accuracy.
  5. Author unit tests for topological, schema, and edge validators.
  6. Author end-to-end integration tests for all REST API routes (`/api/health`, `/api/graph`, `/api/traversal`, `/api/validation`, `/api/benchmarks`).
  7. Run complete test suite and report pass/fail metrics.
- **Expected Deliverables**:
  - Full automated Pytest suite with >= 90% code coverage.
  - Shared fixtures in `conftest.py`.
  - Verified green test suite execution.
- **Dependencies**:
  - Anushka (Sample scenario fixture).
  - Deep, Ansh, Preetam, Soumya, Kanak (Modules under test).
- **Task Status**: `NOT STARTED`

---

### Member 11 — Kanak
- **Role**: Performance Benchmarking
- **Primary Assigned Files**:
  - `backend/app/benchmarks/benchmark_graph.py`
  - `backend/app/benchmarks/benchmark_traversal.py`
  - `backend/app/benchmarks/benchmark_results.py`
  - `backend/app/services/benchmark_service.py`
  - `backend/app/api/routes/benchmarks.py`
  - `backend/app/benchmarks/__init__.py`
  - `docs/reports/performance_report.md`
  - `scripts/run_benchmarks.py`
- **Supporting Areas**:
  - Traversal performance optimization with Preetam.
  - Builder performance analysis with Ansh.
  - Automated benchmark assertions with Shanu.
- **Exact Responsibilities**:
  1. Build micro-benchmarking harness measuring graph construction latency.
  2. Build traversal benchmark harness measuring downstream BFS latency across 1,000 runs using `time.perf_counter_ns`.
  3. Validate compliance with the under-10-ms traversal latency target.
  4. Aggregate statistical distributions (p50, p90, p95, p99, min, max, std-dev).
  5. Implement `BenchmarkService` and `GET /api/benchmarks` endpoint.
  6. Author `scripts/run_benchmarks.py` CLI runner.
  7. Document actual measured benchmark data in `docs/reports/performance_report.md`.
- **Expected Deliverables**:
  - Working benchmarking suite in `backend/app/benchmarks/`.
  - Working `GET /api/benchmarks` REST API route.
  - CLI benchmarking script and formal performance report.
- **Dependencies**:
  - Ansh (Graph builder).
  - Preetam (Traversal algorithm).
  - Deep (Benchmark response schemas).
- **Task Status**: `NOT STARTED`

---

### Member 12 — Sumit
- **Role**: Documentation and Demo Guide
- **Primary Assigned Files**:
  - `README.md`
  - `docs/api/api_documentation.md`
  - `docs/sprint/sprint_1_demo_guide.md`
  - `docs/architecture/system_architecture.md`
  - `docs/architecture/data_flow.md`
  - `backend/app/static/sprint-1-demo.html`
  - `backend/app/static/css/sprint-1-demo.css`
  - `backend/app/static/js/sprint-1-demo.js`
- **Supporting Areas**:
  - Sprint documentation coordination with Mishti.
  - Architecture documentation alignment with the team.
  - API endpoint verification with all route owners.
- **Exact Responsibilities**:
  1. Maintain root `README.md` with project overview, architecture, quickstart, and team links.
  2. Document all REST API contracts and endpoints in `docs/api/api_documentation.md`.
  3. Author `docs/architecture/system_architecture.md` and `docs/architecture/data_flow.md`.
  4. Author `docs/sprint/sprint_1_demo_guide.md` providing step-by-step operator walkthroughs.
  5. Build static browser demo interface (`sprint-1-demo.html`, `sprint-1-demo.css`, `sprint-1-demo.js`).
  6. Ensure static UI visualizes tiers, renders nodes, and triggers traversal on click.
- **Expected Deliverables**:
  - Comprehensive documentation suite (README, API docs, architecture, data flow, demo guide).
  - Interactive static browser visualization demo served by the backend.
- **Dependencies**:
  - Architecture Team (Collaborative system architecture).
  - Ansh (Graph API).
  - Preetam (Traversal API).
  - Soumya (Validation API).
- **Task Status**: `NOT STARTED`

---

## 3. Cross-Member Dependency Matrix

| Member | Primary Output | Depends On | Needed By |
|---|---|---|---|
| **Mishti** | Sprint objectives & criteria | Deep, Sumit | All 12 members |
| **Deep** | Domain models, schemas, constants, exceptions (COMPLETED; Team Maintained) | Anushka, Mishti | Ansh, Aadee, Preetam, Soumya, Kanak, Sumit |
| **Anushka** | Baseline dataset & fixtures | Deep, Aadee | Aadee, Ansh, Sonal, Soumya, Shanu |
| **Ansh** | NetworkX builder & GraphService | Deep, Aadee, Anushka | Preetam, Soumya, Shanu, Kanak, Sumit |
| **Aadee** | Data loader & Repository | Anushka, Deep | Ansh, Soumya |
| **Preetam** | BFS Traversal & TraversalService | Ansh, Deep | Divyanshu, Shanu, Kanak, Sumit |
| **Sonal** | Mapping verification report | Anushka, Deep, Ansh | Anushka, Soumya, Mishti |
| **Soumya** | Validation engine & report | Ansh, Deep, Anushka | Shanu, Divyanshu, Sumit |
| **Divyanshu** | Edge cases tests & complexity doc | Preetam, Ansh, Soumya, Shanu | Shanu, Kanak, Sumit |
| **Shanu** | Test suite & conftest fixtures | Anushka, Ansh, Preetam, Soumya, Deep | All members (CI quality gate) |
| **Kanak** | Benchmarking suite & perf report | Ansh, Preetam, Deep | Mishti, Sumit, Shanu |
| **Sumit** | Documentation, demo guide & static UI | All route owners, Architecture Team | Evaluators, Team, Render deployment |
