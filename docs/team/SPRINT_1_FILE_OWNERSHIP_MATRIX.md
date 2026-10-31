# RE:Flow — Sprint 1 File Ownership Matrix

> **Sprint**: Sprint 1 — Supply Chain Graph & Scenario Generator  
> **Total Files Tracked**: 88 files  
> **Status**: APPROVED / ACTIVE  

This matrix maps every file in the RE:Flow Sprint 1 repository to its primary owner, supporting collaborators, concrete responsibility, required deliverable, and current implementation status.

| File Path | Primary Owner | Supporting Members | Responsibility | Deliverable | Status |
|---|---|---|---|---|---|
| `.env.example` | **Deep** | All Members | Define environment variable templates | Valid .env template | `NOT STARTED` |
| `.gitignore` | **Deep** | All Members | Define git ignore patterns for python, venv, caches | Configured .gitignore | `NOT STARTED` |
| `README.md` | **Sumit** | Deep, Mishti | Root project overview, architecture, quickstart, and links | Production-ready README | `NOT STARTED` |
| `backend/app/__init__.py` | **Deep** | All Members | Initialize backend app package | Package initializer | `NOT STARTED` |
| `backend/app/api/__init__.py` | **Deep** | Route Owners | Initialize API package | Package initializer | `NOT STARTED` |
| `backend/app/api/router.py` | **Deep** | Ansh, Preetam, Soumya, Kanak | Central API router aggregating route blueprints | Unified API blueprint | `NOT STARTED` |
| `backend/app/api/routes/__init__.py` | **Deep** | Route Owners | Initialize routes package | Package initializer | `NOT STARTED` |
| `backend/app/api/routes/benchmarks.py` | **Kanak** | Deep | Performance telemetry and SLA latency metrics endpoint | GET /api/benchmarks route | `NOT STARTED` |
| `backend/app/api/routes/graph.py` | **Ansh** | Deep | Graph query endpoint returning 19 nodes and 21 edges | GET /api/graph route | `NOT STARTED` |
| `backend/app/api/routes/health.py` | **Deep** | Ansh | Health check and service diagnostic endpoint | GET /api/health route | `NOT STARTED` |
| `backend/app/api/routes/traversal.py` | **Preetam** | Deep | Downstream impact BFS traversal endpoint | POST /api/traversal route | `NOT STARTED` |
| `backend/app/api/routes/validation.py` | **Soumya** | Deep | Graph validation audit summary endpoint | GET /api/validation route | `NOT STARTED` |
| `backend/app/benchmarks/__init__.py` | **Kanak** | Preetam, Ansh | Export benchmarking suite modules | Package initializer | `NOT STARTED` |
| `backend/app/benchmarks/benchmark_graph.py` | **Kanak** | Ansh | Micro-benchmark harness for graph construction latency | Graph benchmark runner | `NOT STARTED` |
| `backend/app/benchmarks/benchmark_results.py` | **Kanak** | Deep | Result aggregation, statistics (p50, p95, p99), JSON export | Metrics aggregator | `NOT STARTED` |
| `backend/app/benchmarks/benchmark_traversal.py` | **Kanak** | Preetam | Micro-benchmark harness for BFS traversal latency (<10ms SLA) | Traversal benchmark runner | `NOT STARTED` |
| `backend/app/core/__init__.py` | **Deep** | All Members | Initialize core module namespace | Package initializer | `NOT STARTED` |
| `backend/app/core/config.py` | **Deep** | Aadee | Type-safe environment configurations and path resolution | Config object | `NOT STARTED` |
| `backend/app/core/constants.py` | **Deep** | Anushka, Ansh | Domain enums (TierType, EdgeType) and SLA thresholds | Canonical constants | `NOT STARTED` |
| `backend/app/core/exceptions.py` | **Deep** | Soumya, Preetam | Custom domain exception hierarchy | Domain exceptions | `NOT STARTED` |
| `backend/app/data/__init__.py` | **Aadee** | Anushka | Export data loader, normalizer, and repository | Package initializer | `NOT STARTED` |
| `backend/app/data/loader.py` | **Aadee** | Anushka | Read and parse raw scenario JSON with error handling | File loader function | `NOT STARTED` |
| `backend/app/data/normalizer.py` | **Aadee** | Deep | Sanitize and normalize raw JSON into domain records | Data normalizer module | `NOT STARTED` |
| `backend/app/data/repository.py` | **Aadee** | Ansh | Repository pattern interface for scenario records | ScenarioRepository class | `NOT STARTED` |
| `backend/app/graph/__init__.py` | **Ansh** | Preetam | Export graph builder, schema, traversal, operations | Package initializer | `NOT STARTED` |
| `backend/app/graph/builder.py` | **Ansh** | Deep, Aadee, Anushka | Build NetworkX DiGraph from normalized scenario data | nx.DiGraph builder | `NOT STARTED` |
| `backend/app/graph/operations.py` | **Ansh** | Preetam | Reusable graph inspection and subgraph operations | Graph operations library | `NOT STARTED` |
| `backend/app/graph/schema.py` | **Ansh** | Deep | Graph construction rules and tier connection constraints | Builder rule definitions | `NOT STARTED` |
| `backend/app/graph/traversal.py` | **Preetam** | Ansh | Downstream BFS traversal algorithm (<10ms target) | BFS traversal engine | `NOT STARTED` |
| `backend/app/main.py` | **Deep** | Sumit, Ansh | Application entry point, Flask bootstrapping, static route | Runnable Flask app | `NOT STARTED` |
| `backend/app/models/__init__.py` | **Deep** | Ansh, Aadee | Export domain entity models | Package initializer | `NOT STARTED` |
| `backend/app/models/edges.py` | **Deep** | Anushka, Ansh | Domain models for 3 directed relationships (SUPPLIES, USED_IN, FULFILLS) | Edge domain classes | `NOT STARTED` |
| `backend/app/models/graph.py` | **Deep** | Ansh | Graph domain container entity | Graph domain model | `NOT STARTED` |
| `backend/app/models/nodes.py` | **Deep** | Anushka, Aadee | Domain models for 4 tiers (Supplier, Part, Product, Order) | Node domain classes | `NOT STARTED` |
| `backend/app/schemas/__init__.py` | **Deep** | Route Owners | Export serialization schemas | Package initializer | `NOT STARTED` |
| `backend/app/schemas/graph.py` | **Deep** | Ansh | Serialization schemas for graph query payloads | Graph schemas | `NOT STARTED` |
| `backend/app/schemas/traversal.py` | **Deep** | Preetam | Serialization schemas for traversal request/response | Traversal schemas | `NOT STARTED` |
| `backend/app/schemas/validation.py` | **Deep** | Soumya | Serialization schemas for validation audit results | Validation schemas | `NOT STARTED` |
| `backend/app/services/__init__.py` | **Deep** | Service Owners | Export backend service classes | Package initializer | `NOT STARTED` |
| `backend/app/services/benchmark_service.py` | **Kanak** | Deep | Service managing performance telemetry and benchmarks | BenchmarkService class | `NOT STARTED` |
| `backend/app/services/graph_service.py` | **Ansh** | Deep, Aadee | Service orchestrating graph lifecycle and caching | GraphService class | `NOT STARTED` |
| `backend/app/services/traversal_service.py` | **Preetam** | Ansh, Deep | Service coordinating downstream blast radius queries | TraversalService class | `NOT STARTED` |
| `backend/app/services/validation_service.py` | **Soumya** | Deep, Ansh | Service coordinating multi-level graph audit pipeline | ValidationService class | `NOT STARTED` |
| `backend/app/static/css/sprint-1-demo.css` | **Sumit** | None | Styles for swimlanes, node cards, and impact highlights | Responsive CSS stylesheet | `NOT STARTED` |
| `backend/app/static/js/sprint-1-demo.js` | **Sumit** | Ansh, Preetam | Vanilla JS client fetching graph and triggering traversal | JavaScript demo driver | `NOT STARTED` |
| `backend/app/static/sprint-1-demo.html` | **Sumit** | Deep | Static HTML5 container for 4-tier visual demo | HTML5 demo template | `NOT STARTED` |
| `backend/app/utils/__init__.py` | **Deep** | All Members | Export utility helpers and logger | Package initializer | `NOT STARTED` |
| `backend/app/utils/helpers.py` | **Deep** | All Members | Dictionary sanitization and execution timer helpers | Utilities library | `NOT STARTED` |
| `backend/app/utils/logging.py` | **Deep** | All Members | Structured logger configuration | Logging module | `NOT STARTED` |
| `backend/app/validation/__init__.py` | **Soumya** | Shanu | Export graph, schema, and edge validators | Package initializer | `NOT STARTED` |
| `backend/app/validation/edge_validator.py` | **Soumya** | Deep | Edge direction and tier transition validation | Edge validator module | `NOT STARTED` |
| `backend/app/validation/graph_validator.py` | **Soumya** | Ansh | Topological checks (DAG acyclicity, cycle detection) | Graph validator module | `NOT STARTED` |
| `backend/app/validation/schema_validator.py` | **Soumya** | Deep, Anushka | JSON schema and required field verification | Schema validator module | `NOT STARTED` |
| `backend/pytest.ini` | **Shanu** | Deep | Pytest discovery configuration and marker definitions | Configured pytest.ini | `NOT STARTED` |
| `backend/tests/__init__.py` | **Shanu** | All Members | Initialize test suite package | Package initializer | `NOT STARTED` |
| `backend/tests/conftest.py` | **Shanu** | Anushka, Ansh, Deep | Shared Pytest fixtures (graph, raw data, test client) | Shared fixtures module | `NOT STARTED` |
| `backend/tests/fixtures/README.md` | **Anushka** | Shanu | Ownership and specification doc for test fixtures | Companion fixture doc | `NOT STARTED` |
| `backend/tests/fixtures/sample_scenario.json` | **Anushka** | Shanu | Standardized test fixture scenario dataset | Immutable test JSON | `NOT STARTED` |
| `backend/tests/integration/__init__.py` | **Shanu** | All Members | Initialize integration tests package | Package initializer | `NOT STARTED` |
| `backend/tests/integration/test_api.py` | **Shanu** | Route Owners | Integration tests for all REST API endpoints | API integration test suite | `NOT STARTED` |
| `backend/tests/unit/__init__.py` | **Shanu** | All Members | Initialize unit tests package | Package initializer | `NOT STARTED` |
| `backend/tests/unit/test_edge_cases.py` | **Divyanshu** | Shanu, Preetam, Soumya | Unit tests for boundary conditions, cycles, empty inputs | Edge case test suite | `NOT STARTED` |
| `backend/tests/unit/test_graph.py` | **Shanu** | Ansh | Unit tests for graph builder (19 nodes, 21 edges) | Graph unit test suite | `NOT STARTED` |
| `backend/tests/unit/test_traversal.py` | **Shanu** | Preetam | Unit tests for downstream BFS traversal accuracy | Traversal unit test suite | `NOT STARTED` |
| `backend/tests/unit/test_validation.py` | **Shanu** | Soumya | Unit tests for topological, schema, and edge validators | Validation unit test suite | `NOT STARTED` |
| `data/processed/.gitkeep` | **Anushka** | Aadee | Keep processed data folder structure in version control | Directory placeholder | `NOT STARTED` |
| `data/raw/README.md` | **Anushka** | Deep, Sonal | Ownership and specification doc for raw scenario data | Companion dataset doc | `NOT STARTED` |
| `data/raw/scenario_dataset.json` | **Anushka** | Deep, Aadee, Sonal | Approved baseline dataset (19 nodes, 21 edges) | Canonical dataset JSON | `NOT STARTED` |
| `data/schemas/README.md` | **Deep** | Soumya | Ownership and specification doc for graph schema JSON | Companion schema doc | `NOT STARTED` |
| `data/schemas/graph_schema.json` | **Deep** | Soumya, Anushka | JSON Schema defining structural constraints for scenario JSON | JSON Schema file | `NOT STARTED` |
| `docs/api/api_documentation.md` | **Sumit** | Route Owners | Complete REST API reference with curl examples | API documentation doc | `NOT STARTED` |
| `docs/architecture/data_flow.md` | **Sumit** | Aadee, Ansh, Preetam | Data lifecycle documentation from ingestion to visualization | Data flow doc | `NOT STARTED` |
| `docs/architecture/graph_schema.md` | **Deep** | Mishti, Anushka | Canonical graph schema and tier relationship specification | Graph schema doc | `NOT STARTED` |
| `docs/architecture/system_architecture.md` | **Sumit** | Deep | System architecture specification and deployment design | Architecture doc | `NOT STARTED` |
| `docs/reports/complexity_analysis.md` | **Divyanshu** | Preetam, Ansh, Soumya | Algorithmic time and space complexity analysis report | Complexity analysis doc | `NOT STARTED` |
| `docs/reports/mapping_verification.md` | **Sonal** | Anushka, Deep, Ansh | Verification audit report of multi-tier relationship mappings | Mapping audit report | `NOT STARTED` |
| `docs/reports/performance_report.md` | **Kanak** | Preetam, Ansh | Performance benchmark report verifying <10ms SLA | Performance report doc | `NOT STARTED` |
| `docs/reports/validation_report.md` | **Soumya** | Deep | Formal report of graph integrity audit results | Validation report doc | `NOT STARTED` |
| `docs/sprint/sprint_1.md` | **Mishti** | Deep, Sumit | Sprint 1 scope, objectives, and acceptance criteria | Approved Sprint 1 charter | `NOT STARTED` |
| `docs/sprint/sprint_1_demo_guide.md` | **Sumit** | Deep, Route Owners | Step-by-step walkthrough for local and Render demo | Demo execution guide | `NOT STARTED` |
| `docs/team/SPRINT_1_EXECUTION_PLAN.md` | **Mishti** | Deep | 7-phase sequential task execution and handoff plan | Execution plan doc | `NOT STARTED` |
| `docs/team/SPRINT_1_FILE_OWNERSHIP_MATRIX.md` | **Mishti** | Deep | Complete file-to-owner responsibility matrix | File matrix doc | `NOT STARTED` |
| `docs/team/SPRINT_1_TEAM_OWNERSHIP.md` | **Mishti** | Deep | Central team ownership and member profile documentation | Team ownership doc | `NOT STARTED` |
| `pyproject.toml` | **Deep** | Shanu | Define Python project metadata, dependencies, and linter settings | Working pyproject.toml | `NOT STARTED` |
| `render.yaml` | **Deep** | Sumit | Define Render Infrastructure-as-Code deployment configuration | Valid render.yaml | `NOT STARTED` |
| `scripts/run_benchmarks.py` | **Kanak** | Shanu | CLI script executing performance benchmarks | CLI benchmark script | `NOT STARTED` |
| `scripts/run_local.py` | **Deep** | Sumit | One-command local development server launcher | CLI runner script | `NOT STARTED` |
| `scripts/validate_graph.py` | **Soumya** | Shanu | CLI script executing graph validation suite | CLI validation script | `NOT STARTED` |
