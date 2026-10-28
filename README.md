# Team Photon — Graph Validation Sprint 1

Flask + NetworkX supply-chain graph demo with baseline validation, current-graph structural checks, downstream tracing metrics, and a D3 frontend validation panel.

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
python -m pytest --cov=graph_validation --cov-report=term-missing
python -m compileall app.py graph_validation tests benchmarks
python -m benchmarks.benchmark_tracing
python app.py
```

Open http://127.0.0.1:5000. Use **Graph Validation** in the top bar. `GET /api/validation` returns separate reports for original baseline and current in-memory graph. `GET /api/trace/<node_id>` reports traversal-only time.

## Data model and policy

The source dataset declares a DAG and dependency direction Supplier → Part → Product → Order. Baseline validation checks 19 nodes / 21 edges and category counts. Current graph integrity deliberately omits baseline counts so legitimate cascade deletions are not treated as structural corruption. Duplicate IDs are checked against raw records before constructing a `DiGraph`.

The current model permits PART-05 to be supplied by both suppliers. Consequently supplier descendant sets overlap. For future schema/count changes, update `graph_validation/schema.py` after approving the change and update tests/fixtures in the same change.

## Timing interpretation

Benchmark times only `networkx.descendants()` traversal plus the tiny source-existence check and result sorting in `trace_downstream_with_metrics`; excludes loading, validation, HTTP, and frontend rendering. Reported measurements are machine/environment-specific, not a universal performance guarantee. The 10 ms criterion is compared against measured values, never hardcoded as a pass.

## Structure

- `app.py`: existing Flask routes plus validation and trace endpoints.
- `static/index.html`: existing D3 frontend plus validation panel.
- `graph_validation/`: schema, validators, and tracing metrics.
- `tests/`: pytest unit, reachability, and Flask regression tests.
- `benchmarks/`: reproducible benchmark script.
- `reports/`: generated machine-readable reports.
- `docs/`: setup, schema, integration, frontend, testing details.
