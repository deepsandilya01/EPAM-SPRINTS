# Project Structure

This document provides a complete inventory of the files and directories in the `EPAM-SPRINTS` repository.

```
EPAM-SPRINTS/
├── .env.example                     # Sample environment variable configuration
├── pyproject.toml                   # Project metadata, dependencies, and Ruff configuration
├── render.yaml                      # Render PaaS deployment manifest
├── scripts/                         # Operational CLI utilities
│   ├── run_benchmarks.py            # Downstream traversal SLA latency benchmark CLI
│   ├── run_local.py                 # Interactive local development server runner
│   └── validate_graph.py            # Standalone graph structural audit CLI
├── backend/
│   ├── pytest.ini                   # Pytest runner configuration
│   ├── reports/
│   │   ├── graph_benchmark_report.json # Persisted SLA traversal benchmark results
│   │   └── graph_validation_report.json# Persisted graph integrity validation results
│   ├── tests/                       # Pytest test suite (130 tests)
│   │   ├── conftest.py              # Test fixtures (Flask test client, canonical datasets)
│   │   ├── integration/
│   │   │   └── test_api.py          # Flask HTTP routes and end-to-end integration tests
│   │   └── unit/
│   │       ├── test_api_schemas.py  # Pydantic request/response schema unit tests
│   │       ├── test_domain_models.py# Domain model validation unit tests
│   │       ├── test_edge_cases.py   # Malformed payloads and edge-case unit tests
│   │       ├── test_graph.py        # Graph construction and baseline count unit tests
│   │       ├── test_traversal.py    # Downstream BFS reachability unit tests
│   │       └── test_validation.py   # Validation module unit tests
│   └── app/                         # Core application package
│       ├── __init__.py              # App package init
│       ├── main.py                  # Flask entrypoint, static routing, and error handlers
│       ├── api/                     # HTTP API layer
│       │   ├── __init__.py          # API blueprint aggregator (/api)
│       │   └── routes/              # Modular route blueprints
│       │       ├── __init__.py
│       │       ├── benchmarks.py    # GET /api/benchmarks, /api/benchmark/tracing
│       │       ├── graph.py         # GET /api/graph, DELETE /api/node/<id>, undo, reset
│       │       ├── health.py        # GET /api/health
│       │       ├── traversal.py     # GET /api/downstream/<id>, /api/impact/<id>
│       │       └── validation.py    # GET /api/validation
│       ├── core/                    # Application settings and exceptions
│       │   ├── __init__.py
│       │   ├── config.py            # Pydantic BaseSettings configuration
│       │   └── exceptions.py        # Custom domain exception hierarchy
│       ├── data/                    # Dataset loaders and JSON files
│       │   ├── __init__.py
│       │   ├── loader.py            # Scenario dataset loader
│       │   ├── datasets/
│       │   │   └── scenario_dataset.json # Canonical 19-node, 21-edge supply chain scenario
│       │   └── schemas/
│       │       └── graph_schema.json     # JSON schema for scenario datasets
│       ├── graph/                   # Graph algorithms and operations
│       │   ├── __init__.py
│       │   ├── builder.py           # NetworkX DiGraph builder
│       │   ├── operations.py        # Cascading deletion, snapshotting, and undo stack
│       │   └── traversal.py         # Downstream BFS traversal algorithm
│       ├── models/                  # Domain entity dataclasses
│       │   ├── __init__.py
│       │   ├── edges.py             # SupplyChainEdge, SuppliesEdge, UsedInEdge, FulfillsEdge
│       │   ├── graph.py             # SupplyChainGraph domain container
│       │   └── nodes.py             # SupplierNode, PartNode, ProductNode, OrderNode
│       ├── schemas/                 # Pydantic API contract schemas
│       │   ├── __init__.py
│       │   ├── graph.py             # Graph response and filter schemas
│       │   ├── traversal.py         # Traversal request and response schemas
│       │   └── validation.py        # Validation request and response schemas
│       ├── services/                # Business logic services
│       │   ├── __init__.py
│       │   ├── benchmark_service.py # Downstream traversal benchmarking service
│       │   ├── graph_service.py     # In-memory graph state and mutation service
│       │   └── validation_service.py# Graph integrity and schema validation service
│       ├── static/                  # Frontend single-page application
│       │   ├── css/
│       │   │   └── sprint-1-demo.css # Visual styling and layout
│       │   ├── js/
│       │   │   └── sprint-1-demo.js  # D3.js visualization, interactions, and API polling
│       │   └── sprint-1-demo.html   # Main HTML UI container
│       └── validation/              # Modular validation subsystem
│           ├── __init__.py          # Public validation exports
│           ├── cycles.py            # Pure cycle detection and DAG acyclicity validation
│           ├── edges.py             # Edge records and direction rule validation
│           ├── models.py            # Validation dataclasses, policies, and enums
│           ├── nodes.py             # Node records, categories, and field validation
│           ├── reporting.py         # Console formatting and JSON report generation
│           └── validator.py         # High-level validation orchestrator
└── docs/                            # Project documentation
    ├── README.md                    # Documentation index
    ├── api-reference.md             # REST API endpoint reference
    ├── architecture.md              # System architecture and data flow
    ├── benchmarking.md              # Traversal latency benchmarks and SLA
    ├── configuration.md             # Environment variables and configuration options
    ├── deployment.md                # Render deployment guide
    ├── frontend.md                  # D3.js frontend visualization architecture
    ├── graph-model.md               # 4-tier DAG domain model specification
    ├── installation-and-setup.md    # Local environment setup instructions
    ├── project-structure.md         # File and directory inventory (this file)
    ├── running-locally.md           # Running the local Flask server
    ├── testing.md                   # Pytest test suite architecture and running tests
    ├── troubleshooting.md           # Debugging and common issue resolution
    └── validation.md                # Modular validation engine guide
```

