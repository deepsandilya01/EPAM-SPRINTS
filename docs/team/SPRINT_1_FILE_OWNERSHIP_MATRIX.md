# RE:Flow — Sprint 1 File Ownership Matrix

> **Sprint**: Sprint 1 — Supply Chain Graph & Scenario Generator  
> **Status**: APPROVED / ACTIVE  

This matrix maps files in the RE:Flow Sprint 1 repository to their primary owner, supporting collaborators, concrete responsibility, required deliverable, and current implementation status.

RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.

| File Path | Primary Owner | Supporting Members | Responsibility | Deliverable | Status |
|---|---|---|---|---|---|
| `.env.example` | **Team Maintained** | All Members | Define environment variable templates | Valid .env template | `COMPLETED` |
| `.gitignore` | **Team Maintained** | All Members | Define git ignore patterns for python, venv, caches | Configured .gitignore | `COMPLETED` |
| `README.md` | **Sumit** | Mishti, Architecture Team | Root project overview, architecture, quickstart, and links | Production-ready README | `COMPLETED` |
| `backend/app/__init__.py` | **Team Maintained** | All Members | Initialize backend app package | Package initializer | `COMPLETED` |
| `backend/app/api/__init__.py` | **Team Maintained** | Route Owners | Initialize API package | Package initializer | `COMPLETED` |
| `backend/app/api/router.py` | **Divyanshu / Team Maintained** | Ansh, Preetam, Soumya, Kanak | Central API router aggregating route blueprints | Unified API blueprint | `NOT STARTED` |
| `backend/app/api/routes/__init__.py` | **Team Maintained** | Route Owners | Initialize routes package | Package initializer | `COMPLETED` |
| `backend/app/api/routes/benchmarks.py` | **Kanak** | Shanu | Performance telemetry and SLA latency metrics endpoint | GET /api/benchmarks route | `NOT STARTED` |
| `backend/app/api/routes/graph.py` | **Ansh** | Divyanshu | Graph query endpoint returning 19 nodes and 21 edges | GET /api/graph route | `NOT STARTED` |
| `backend/app/api/routes/health.py` | **Team Maintained** | Ansh | Health check and service diagnostic endpoint | GET /api/health route | `NOT STARTED` |
| `backend/app/api/routes/traversal.py` | **Preetam** | Divyanshu | Downstream impact BFS traversal endpoint | POST /api/traversal route | `NOT STARTED` |
| `backend/app/api/routes/validation.py` | **Soumya** | Divyanshu | Graph validation audit summary endpoint | GET /api/validation route | `NOT STARTED` |
| `backend/app/benchmarks/__init__.py` | **Kanak** | Preetam, Ansh | Export benchmarking suite modules | Package initializer | `NOT STARTED` |
| `backend/app/benchmarks/benchmark_graph.py` | **Kanak** | Ansh | Micro-benchmark harness for graph construction latency | Graph benchmark runner | `NOT STARTED` |
| `backend/app/benchmarks/benchmark_results.py` | **Kanak** | Shanu | Result aggregation, statistics (p50, p95, p99), JSON export | Metrics aggregator | `NOT STARTED` |
| `backend/app/benchmarks/benchmark_traversal.py` | **Kanak** | Preetam | Micro-benchmark harness for BFS traversal latency (<10ms SLA) | Traversal benchmark runner | `NOT STARTED` |
| `backend/app/core/__init__.py` | **Team Maintained** | All Members | Initialize core module namespace | Package initializer | `COMPLETED` |
| `backend/app/core/config.py` | **Team Maintained** | Aadee | Type-safe environment configurations and path resolution | Config object | `COMPLETED` |
| `backend/app/core/constants.py` | **Team Maintained** | Implemented by Deep | Domain enums (TierType, EdgeType) and SLA thresholds | Canonical constants | `COMPLETED` |
| `backend/app/core/exceptions.py` | **Team Maintained** | Implemented by Deep | Custom domain exception hierarchy | Domain exceptions | `COMPLETED` |
| `backend/app/data/__init__.py` | **Aadee** | Anushka | Export data loader, normalizer, and repository | Package initializer | `NOT STARTED` |
| `backend/app/data/loader.py` | **Aadee** | Anushka | Read and parse raw scenario JSON with error handling | File loader function | `NOT STARTED` |
| `backend/app/data/normalizer.py` | **Aadee** | Development Team | Sanitize and normalize raw JSON into domain records | Data normalizer module | `NOT STARTED` |
| `backend/app/data/repository.py` | **Aadee** | Ansh | Repository pattern interface for scenario records | ScenarioRepository class | `NOT STARTED` |
| `backend/app/graph/__init__.py` | **Ansh** | Preetam | Export graph builder, schema, traversal, operations | Package initializer | `NOT STARTED` |
| `backend/app/graph/builder.py` | **Ansh** | Aadee, Anushka | Build NetworkX DiGraph from normalized scenario data | nx.DiGraph builder | `NOT STARTED` |
| `backend/app/graph/operations.py` | **Ansh** | Preetam | Reusable graph inspection and subgraph operations | Graph operations library | `NOT STARTED` |
| `backend/app/graph/schema.py` | **Ansh** | Development Team | Graph construction rules and tier connection constraints | Builder rule definitions | `NOT STARTED` |
| `backend/app/graph/traversal.py` | **Preetam** | Ansh | Downstream BFS traversal algorithm (<10ms target) | BFS traversal engine | `NOT STARTED` |
| `backend/app/main.py` | **Team Maintained** | Sumit, Ansh | Application entry point, Flask bootstrapping, static route | Runnable Flask app | `NOT STARTED` |
| `backend/app/models/__init__.py` | **Team Maintained** | Implemented by Deep | Export domain entity models | Package initializer | `COMPLETED` |
| `backend/app/models/edges.py` | **Team Maintained** | Implemented by Deep | Domain models for 3 directed relationships (SUPPLIES, USED_IN, FULFILLS) | Edge domain classes | `COMPLETED` |
| `backend/app/models/graph.py` | **Team Maintained** | Implemented by Deep | Graph domain container entity | Graph domain model | `COMPLETED` |
| `backend/app/models/nodes.py` | **Team Maintained** | Implemented by Deep | Domain models for 4 tiers (Supplier, Part, Product, Order) | Node domain classes | `COMPLETED` |
| `backend/app/schemas/__init__.py` | **Team Maintained** | Implemented by Deep | Export serialization schemas | Package initializer | `COMPLETED` |
| `backend/app/schemas/graph.py` | **Team Maintained** | Implemented by Deep | Serialization schemas for graph query payloads | Graph schemas | `COMPLETED` |
| `backend/app/schemas/traversal.py` | **Team Maintained** | Implemented by Deep | Serialization schemas for traversal request/response | Traversal schemas | `COMPLETED` |
| `backend/app/schemas/validation.py` | **Team Maintained** | Implemented by Deep | Serialization schemas for validation audit results | Validation schemas | `COMPLETED` |
| `backend/app/services/__init__.py` | **Team Maintained** | Service Owners | Export backend service classes | Package initializer | `COMPLETED` |
| `backend/app/services/benchmark_service.py` | **Kanak** | Shanu | Service managing performance telemetry and benchmarks | BenchmarkService class | `NOT STARTED` |
| `backend/app/services/graph_service.py` | **Ansh** | Aadee | Service orchestrating graph lifecycle and caching | GraphService class | `NOT STARTED` |
| `backend/app/services/traversal_service.py` | **Preetam** | Ansh | Service coordinating downstream blast radius queries | TraversalService class | `NOT STARTED` |
| `backend/app/services/validation_service.py` | **Soumya** | Ansh | Service coordinating multi-level graph audit pipeline | ValidationService class | `NOT STARTED` |
| `backend/app/static/css/sprint-1-demo.css` | **Sumit** | None | Styles for swimlanes, node cards, and impact highlights | Responsive CSS stylesheet | `NOT STARTED` |
| `backend/app/static/js/sprint-1-demo.js` | **Sumit** | Ansh, Preetam | Vanilla JS client fetching graph and triggering traversal | JavaScript demo driver | `NOT STARTED` |
| `backend/app/static/sprint-1-demo.html` | **Sumit** | Team Maintained | Static HTML5 container for 4-tier visual demo | HTML5 demo template | `NOT STARTED` |
| `backend/app/utils/__init__.py` | **Team Maintained** | All Members | Export utility helpers and logger | Package initializer | `COMPLETED` |
| `backend/app/utils/helpers.py` | **Team Maintained** | All Members | Dictionary sanitization and execution timer helpers | Utilities library | `COMPLETED` |
| `backend/app/utils/logging.py` | **Team Maintained** | All Members | Structured logger configuration | Logging module | `COMPLETED` |
| `backend/app/validation/__init__.py` | **Soumya** | Shanu | Export graph, schema, and edge validators | Package initializer | `NOT STARTED` |
| `backend/app/validation/edge_validator.py` | **Soumya** | Development Team | Edge direction and tier transition validation | Edge validator module | `NOT STARTED` |
| `backend/app/validation/graph_validator.py` | **Soumya** | Ansh | Topological checks (DAG acyclicity, cycle detection) | Graph validator module | `NOT STARTED` |
| `backend/app/validation/schema_validator.py` | **Soumya** | Anushka | JSON schema and required field verification | Schema validator module | `NOT STARTED` |
| `backend/pytest.ini` | **Shanu** | Team Maintained | Pytest discovery configuration and marker definitions | Configured pytest.ini | `COMPLETED` |
| `backend/tests/__init__.py` | **Shanu** | All Members | Initialize test suite package | Package initializer | `COMPLETED` |
| `backend/tests/conftest.py` | **Shanu** | Anushka, Ansh | Shared Pytest fixtures (graph, raw data, test client) | Shared fixtures module | `NOT STARTED` |
| `backend/tests/fixtures/README.md` | **Anushka** | Shanu | Ownership and specification doc for test fixtures | Companion fixture doc | `COMPLETED` |
| `backend/tests/fixtures/sample_scenario.json` | **Anushka** | Shanu | Standardized test fixture scenario dataset | Immutable test JSON | `NOT STARTED` |
| `backend/tests/integration/__init__.py` | **Shanu** | All Members | Initialize integration tests package | Package initializer | `NOT STARTED` |
| `backend/tests/integration/test_api.py` | **Shanu** | Route Owners | Integration tests for all REST API endpoints | API integration test suite | `NOT STARTED` |
| `backend/tests/unit/__init__.py` | **Shanu** | All Members | Initialize unit tests package | Package initializer | `COMPLETED` |
| `backend/tests/unit/test_api_schemas.py` | **Team Maintained** | Shanu, Divyanshu | Unit tests for REST API schemas and validation | API schemas test suite | `COMPLETED` |
| `backend/tests/unit/test_domain_models.py` | **Team Maintained** | Shanu, Sonal | Unit tests for domain models (19 nodes, 21 edges) | Domain models test suite | `COMPLETED` |
| `backend/tests/unit/test_edge_cases.py` | **Divyanshu** | Shanu, Preetam, Soumya | Unit tests for boundary conditions, cycles, empty inputs | Edge case test suite | `NOT STARTED` |
| `backend/tests/unit/test_graph.py` | **Shanu** | Ansh | Unit tests for graph builder (19 nodes, 21 edges) | Graph unit test suite | `NOT STARTED` |
| `backend/tests/unit/test_traversal.py` | **Shanu** | Preetam | Unit tests for downstream BFS traversal accuracy | Traversal unit test suite | `NOT STARTED` |
| `backend/tests/unit/test_validation.py` | **Shanu** | Soumya | Unit tests for topological, schema, and edge validators | Validation unit test suite | `NOT STARTED` |
| `data/processed/.gitkeep` | **Anushka** | Aadee | Keep processed data folder structure in version control | Directory placeholder | `COMPLETED` |
| `data/raw/README.md` | **Anushka** | Sonal | Ownership and specification doc for raw scenario data | Companion dataset doc | `COMPLETED` |
| `data/raw/scenario_dataset.json` | **Anushka** | Aadee, Sonal | Approved baseline dataset (19 nodes, 21 edges) | Canonical dataset JSON | `NOT STARTED` |
| `data/schemas/README.md` | **Team Maintained** | Implemented by Deep | Ownership and specification doc for graph schema JSON | Companion schema doc | `COMPLETED` |
| `data/schemas/graph_schema.json` | **Team Maintained** | Implemented by Deep | JSON Schema defining structural constraints for scenario JSON | JSON Schema file | `COMPLETED` |
| `docs/api/api_documentation.md` | **Sumit** | Route Owners | Complete REST API reference with curl examples | API documentation doc | `NOT STARTED` |
| `docs/architecture/data_flow.md` | **Sumit** | Aadee, Ansh, Preetam | Data lifecycle documentation from ingestion to visualization | Data flow doc | `NOT STARTED` |
| `docs/architecture/graph_schema.md` | **Team Maintained** | Implemented by Deep | Canonical graph schema and tier relationship specification | Graph schema doc | `COMPLETED` |
| `docs/architecture/system_architecture.md` | **Sumit** | Architecture Team | System architecture specification and deployment design | Architecture doc | `NOT STARTED` |
| `docs/reports/complexity_analysis.md` | **Divyanshu** | Preetam, Ansh, Soumya | Algorithmic time and space complexity analysis report | Complexity analysis doc | `NOT STARTED` |
| `docs/reports/mapping_verification.md` | **Sonal** | Anushka, Ansh | Verification audit report of multi-tier relationship mappings | Mapping audit report | `NOT STARTED` |
| `docs/reports/performance_report.md` | **Kanak** | Preetam, Ansh | Performance benchmark report verifying <10ms SLA | Performance report doc | `NOT STARTED` |
| `docs/reports/validation_report.md` | **Soumya** | Development Team | Formal report of graph integrity audit results | Validation report doc | `NOT STARTED` |
| `docs/sprint/sprint_1.md` | **Mishti** | Sumit, Architecture Team | Sprint 1 scope, objectives, and acceptance criteria | Approved Sprint 1 charter | `NOT STARTED` |
| `docs/sprint/sprint_1_demo_guide.md` | **Sumit** | Route Owners | Step-by-step walkthrough for local and Render demo | Demo execution guide | `NOT STARTED` |
| `docs/team/SPRINT_1_CODE_EXPLANATION.md` | **Team Maintained** | All Members | Comprehensive code walkthrough and implementation guide | Technical documentation | `COMPLETED` |
| `docs/team/SPRINT_1_EXECUTION_PLAN.md` | **Mishti** | Architecture Team | 7-phase sequential task execution and handoff plan | Execution plan doc | `NOT STARTED` |
| `docs/team/SPRINT_1_FILE_OWNERSHIP_MATRIX.md` | **Mishti** | Architecture Team | Complete file-to-owner responsibility matrix | File matrix doc | `COMPLETED` |
| `docs/team/SPRINT_1_TEAM_OWNERSHIP.md` | **Mishti** | Architecture Team | Central team ownership and member profile documentation | Team ownership doc | `COMPLETED` |
| `docs/team/SPRINT_1_TECHNICAL_REVIEW.md` | **Team Maintained** | All Members | 3-level EPAM technical review preparation guide | Technical review guide | `COMPLETED` |
| `pyproject.toml` | **Team Maintained** | Shanu | Define Python project metadata, dependencies, and linter settings | Working pyproject.toml | `COMPLETED` |
| `render.yaml` | **Team Maintained** | Sumit | Define Render Infrastructure-as-Code deployment configuration | Valid render.yaml | `COMPLETED` |
| `scripts/run_benchmarks.py` | **Kanak** | Shanu | CLI script executing performance benchmarks | CLI benchmark script | `NOT STARTED` |
| `scripts/run_local.py` | **Team Maintained** | Sumit | One-command local development server launcher | CLI runner script | `COMPLETED` |
| `scripts/validate_graph.py` | **Soumya** | Shanu | CLI script executing graph validation suite | CLI validation script | `NOT STARTED` |
