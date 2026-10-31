# RE:Flow - Supply Chain Graph & Scenario Generator

> **Sprint 1 Ownership & Task Assignment**
> - **Primary Owner**: Sumit
> - **Role**: Documentation and Demo Guide
> - **File**: `README.md`
> - **Status**: NOT STARTED

### File Purpose
Main entry point and documentation hub for the RE:Flow supply chain dependency mapping project.

### Primary Responsibilities
- Maintain comprehensive overview of RE:Flow project goals and architecture.
- Document Sprint 1 structure overview and module descriptions.
- Maintain team ownership summary and link to central ownership documents.
- Provide quickstart guide for local development and testing.
- Coordinate documentation updates with all 12 team members.

### Dependencies
- Mishti: Sprint 1 objectives and scope.
- Deep: Architecture and data contracts.
- All 12 team members: Individual module deliverables.

### Expected Deliverables
- Production-ready root README.md.

---

RE:Flow is a supply chain dependency mapping and impact analysis platform developed as part of the EPAM project. It models multi-tier supply chain networks as directed acyclic graphs (DAGs) to simulate disruption cascades, trace downstream impact, and validate topological integrity.

## Architecture

- **Backend**: Single Python backend service (Flask).
- **Graph Representation**: Directed Graph (`DiGraph`) powered by NetworkX.
- **Dataset**: JSON-based scenario datasets representing multi-tier supply chains.
- **Demo**: Static HTML5, CSS3, and Vanilla JavaScript user interface served directly by the backend.
- **Deployment**: Unified deployment on Render (single web service hosting API and static demo). No separate React frontend; no Vercel deployment.

## Sprint 1 Repository Structure

```text
RE-Flow/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py
│   │   │       ├── graph.py
│   │   │       ├── traversal.py
│   │   │       ├── validation.py
│   │   │       └── benchmarks.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── nodes.py
│   │   │   ├── edges.py
│   │   │   └── graph.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py
│   │   │   ├── traversal.py
│   │   │   └── validation.py
│   │   │
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── loader.py
│   │   │   ├── normalizer.py
│   │   │   └── repository.py
│   │   │
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py
│   │   │   ├── builder.py
│   │   │   ├── traversal.py
│   │   │   └── operations.py
│   │   │
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   ├── graph_validator.py
│   │   │   ├── schema_validator.py
│   │   │   └── edge_validator.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── graph_service.py
│   │   │   ├── traversal_service.py
│   │   │   ├── validation_service.py
│   │   │   └── benchmark_service.py
│   │   │
│   │   ├── benchmarks/
│   │   │   ├── __init__.py
│   │   │   ├── benchmark_graph.py
│   │   │   ├── benchmark_traversal.py
│   │   │   └── benchmark_results.py
│   │   │
│   │   ├── static/
│   │   │   ├── sprint-1-demo.html
│   │   │   ├── css/
│   │   │   │   └── sprint-1-demo.css
│   │   │   └── js/
│   │   │       └── sprint-1-demo.js
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_graph.py
│   │   │   ├── test_traversal.py
│   │   │   ├── test_validation.py
│   │   │   └── test_edge_cases.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   └── test_api.py
│   │   └── fixtures/
│   │       └── sample_scenario.json
│   │
│   └── pytest.ini
│
├── data/
│   ├── raw/
│   │   └── scenario_dataset.json
│   ├── processed/
│   │   └── .gitkeep
│   └── schemas/
│       └── graph_schema.json
│
├── docs/
│   ├── architecture/
│   │   ├── system_architecture.md
│   │   ├── graph_schema.md
│   │   └── data_flow.md
│   │
│   ├── api/
│   │   └── api_documentation.md
│   │
│   ├── sprint/
│   │   ├── sprint_1.md
│   │   └── sprint_1_demo_guide.md
│   │
│   └── reports/
│       ├── mapping_verification.md
│       ├── validation_report.md
│       ├── performance_report.md
│       └── complexity_analysis.md
│
├── scripts/
│   ├── run_local.py
│   ├── validate_graph.py
│   └── run_benchmarks.py
│
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── render.yaml
```

## Sprint 1 Context

- **Focus**: Supply Chain Graph & Scenario Generator.
- **Planned Baseline Scenario**:
  - 2 Suppliers
  - 5 BOM Parts
  - 2 Finished Products
  - 10 Customer Orders
  - 19 Total Nodes
  - 21 Directed Edges
- **Relationship Types**:
  - `SUPPLIES`: Supplier → BOM Part
  - `USED_IN`: BOM Part → Finished Product
  - `FULFILLS`: Finished Product → Customer Order

## Getting Started

### Prerequisites
- Python >= 3.11
- pip / virtualenv

### Setup
```bash
# Clone the repository
git clone https://github.com/deepsandilya01/EPAM-SPRINTS.git
cd EPAM-SPRINTS

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run test suite
pytest backend/tests
```
