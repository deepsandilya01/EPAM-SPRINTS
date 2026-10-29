# Developer Guidelines & Engineering Workflow

> **Document:** `docs/DEVELOPMENT.md`  
> **Project:** Team Photon — Supply-Chain Decision, Ripple & Recovery Intelligence System  
> **Target Audience:** Core Contributors, Code Reviewers, and EPAM Technical Evaluators

This guide outlines our development workflow, coding standards, test strategy, and static analysis guidelines.

---

## 1. Development Principles

1. **Safety & Zero Regressions**: Any modification to graph algorithms or schemas must pass all existing unit and regression tests without breaking downstream consumers.
2. **Deterministic Behavior**: All graph queries, traversals, and validation checks must produce deterministic outputs.
3. **High-Performance Traversal**: Reachability queries must operate under strict microsecond SLAs ($p_{95} \le 10.0\text{ ms}$).
4. **Readable Engineering Documentation**: Maintain concise, meaningful comments explaining algorithmic invariants, constraints, and non-obvious logic. Avoid decorative ASCII banners or AI-style boilerplates.

---

## 2. Code Organization & Responsibilities

```text
EPAM-SPRINTS/
├── backend/
│   ├── app.py                     # Flask REST application & in-memory graph state
│   ├── graph_validation/          # Core graph validation & tracing engine
│   │   ├── __init__.py            # Package exports
│   │   ├── schema.py              # Domain constants, enums, dataclasses
│   │   ├── validator.py           # Pre-construction & live NetworkX validation
│   │   ├── tracing.py             # Nanosecond BFS reachability timer
│   │   └── reporting.py           # Report formatting & disk serialization
│   ├── benchmarks/                # Latency & throughput benchmarking runners
│   │   └── benchmark_tracing.py   # Statistical CLI benchmark (1,000 runs)
│   ├── tests/                     # 73-test pytest suite
│   │   ├── conftest.py            # Fixtures (clean graph, cycle graph, mock JSON)
│   │   └── test_*.py              # Unit, integration, and regression tests
│   ├── static/                    # Frontend visualizer assets
│   │   └── index.html             # D3.js interactive dashboard
│   ├── data/                      # Canonical input data
│   │   └── photon_sprint1_graph_data.json
│   └── reports/                   # Generated benchmark & validation evidence
├── docs/                          # Architecture, setup, development docs
```

---

## 3. Python Coding Standards

### 3.1 Python Version Support
The codebase supports Python **3.9 through 3.13**. All new code must adhere to:
- Include `from __future__ import annotations` at the top of every module using PEP 604 type unions (`X | None`).
- Use cross-version timezone UTC handling:
  ```python
  try:
      from datetime import UTC  # Python 3.11+
  except ImportError:
      from datetime import timezone
      UTC = timezone.utc  # noqa: UP017
  ```
- Use `pathlib.Path` for all filesystem operations to ensure cross-platform compatibility (Windows vs macOS/Linux).

### 3.2 Immutability & Dataclasses
Validation results and configuration must use `@dataclass(frozen=True)` where state should not mutate after instantiation:
```python
@dataclass(frozen=True)
class ValidationError:
    category: str
    message: str
    entity_id: str | None = None
```

### 3.3 Dynamic Path Resolution
Always resolve paths relative to the current file using `pathlib.Path(__file__).resolve().parent` to allow execution from either repository root or module subdirectories.

---

## 4. Testing Strategy & Execution

Our test suite uses `pytest` and contains **73 automated test cases** categorized into four distinct layers:

### 4.1 Test Layers

| Test File | Test Count | Focus Area |
|---|---|---|
| [`backend/tests/test_acyclicity.py`](../backend/tests/test_acyclicity.py) | 5 | DAG acyclicity verification and cycle injection detection |
| [`backend/tests/test_node_counts.py`](../backend/tests/test_node_counts.py) | 9 | Entity count verification across Suppliers, Parts, Products, Orders |
| [`backend/tests/test_duplicate_ids.py`](../backend/tests/test_duplicate_ids.py) | 8 | Pre-construction duplicate ID detection and collision mitigation |
| [`backend/tests/test_edge_direction.py`](../backend/tests/test_edge_direction.py) | 10 | Tier-flow invariant validation (Suppliers $\to$ Parts $\to$ Products $\to$ Orders) |
| [`backend/tests/test_edge_integrity.py`](../backend/tests/test_edge_integrity.py) | 8 | Dangling edge, orphan node, and schema mismatch validation |
| [`backend/tests/test_missing_entities.py`](../backend/tests/test_missing_entities.py) | 8 | Missing required field handling (`id`, `category`, `source`, `target`) |
| [`backend/tests/test_malformed_data.py`](../backend/tests/test_malformed_data.py) | 7 | Non-dictionary nodes, malformed edge payloads, corrupt JSON schemas |
| [`backend/tests/test_tracing.py`](../backend/tests/test_tracing.py) | 6 | BFS downstream reachability traversal accuracy and latency limits |
| [`backend/tests/test_reporting.py`](../backend/tests/test_reporting.py) | 6 | Validation report serialization and schema compliance |
| [`backend/tests/test_api_integration.py`](../backend/tests/test_api_integration.py) | 6 | Flask REST API endpoints and HTTP response status codes |

### 4.2 Running Tests
```bash
# Run all tests
pytest

# Run tests with detailed test names
pytest -v

# Run a specific test file
pytest backend/tests/test_tracing.py

# Run tests matching a keyword expression
pytest -k "duplicate"

# Run tests with coverage
pytest --cov=backend.graph_validation --cov-report=term-missing
```

### 4.3 Test Fixtures (`conftest.py`)
All reusable fixtures are declared in [`backend/tests/conftest.py`](../backend/tests/conftest.py):
- `raw_sprint1_data`: Loads canonical JSON data from disk.
- `sprint1_digraph`: Constructs a validated live `nx.DiGraph`.
- `cycle_digraph`: Constructs a synthetic graph with a known circular dependency (`A -> B -> C -> A`).
- `test_client`: Flask test client configured with in-memory graph state.

---

## 5. Benchmarking & Performance SLAs

The system enforces a **strict traversal latency SLA** ($p_{95} \le 10.0\text{ ms}$).

### Running the Benchmark
```bash
python -m backend.benchmarks.benchmark_tracing
```

### Benchmark Metrics Tracked:
- 100 warmup runs (eliminates JIT / cache warmup anomalies).
- 1,000 measured iterations across random source nodes.
- Metrics calculated: Mean, Median, Min, Max, $p_{90}$, $p_{95}$, $p_{99}$.
- Results written to [`backend/reports/graph_benchmark_report.json`](../backend/reports/graph_benchmark_report.json).

---

## 6. Static Analysis & Linting

We enforce clean, modern Python style using **Ruff**:
```bash
# Run linter checks
ruff check .

# Automatically apply safe fixes
ruff check . --fix
```

### Configured Rules (`pyproject.toml`):
- `E`, `W`: Pycodestyle errors and warnings.
- `F`: Pyflakes (undefined variables, unused imports).
- `I`: isort (consistent import ordering).
- `UP`: pyupgrade (modern Python syntax patterns).
- `B`: flake8-bugbear (common bug patterns).

---

## 7. Git & Contribution Workflow

1. **Branch Naming**:
   - `feature/<name>` for new capabilities (e.g., `feature/Deep`).
   - `fix/<name>` for bug fixes.
   - `docs/<name>` for documentation improvements.
2. **Local Pre-Flight Checks**:
   Before staging changes, always run the full verification pipeline:
   ```bash
   ruff check .
   pytest
   python -m backend.benchmarks.benchmark_tracing
   ```
3. **Commit Guidelines**:
   - Write imperative, concise commit subjects (e.g., `refactor(backend): reorganize modules into backend package`).
   - Never commit build artifacts (`*.pyc`, `__pycache__`, `.venv`, `*.zip`).
