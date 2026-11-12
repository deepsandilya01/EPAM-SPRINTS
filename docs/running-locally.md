# Running Locally

## Development Server Launch Options

Once dependencies are installed, you can start the application using either of the following methods.

---

### Option 1: Interactive Dev Runner (Recommended)

Run the included convenience script, which binds to port `5050` (or `PORT` if specified in `.env`) and prints an interactive URL menu:

```bash
python3 scripts/run_local.py
```

Console output:
```text
============================================================
  RE:Flow Supply Chain Engine running on http://127.0.0.1:5050
  Interactive Demo UI : http://127.0.0.1:5050/
  Graph API           : http://127.0.0.1:5050/api/graph
  Validation Audit    : http://127.0.0.1:5050/api/validation
  Benchmark API       : http://127.0.0.1:5050/api/benchmark/tracing
============================================================
```

### Option 2: Direct Flask Module Execution

You can also run the Flask entrypoint directly with Python:

```bash
python3 -m backend.app.main
```

Or execute the file directly:

```bash
python3 backend/app/main.py
```

---

## Accessing the Application

Open your browser and navigate to:

- **Visualization UI**: [http://127.0.0.1:5050/](http://127.0.0.1:5050/)
- **Health Check**: [http://127.0.0.1:5050/api/health](http://127.0.0.1:5050/api/health)
- **Active Graph API**: [http://127.0.0.1:5050/api/graph](http://127.0.0.1:5050/api/graph)
- **Validation Report**: [http://127.0.0.1:5050/api/validation](http://127.0.0.1:5050/api/validation)
- **Downstream Tracing**: [http://127.0.0.1:5050/api/downstream/SUP-01](http://127.0.0.1:5050/api/downstream/SUP-01)
- **Latency Benchmark**: [http://127.0.0.1:5050/api/benchmark/tracing](http://127.0.0.1:5050/api/benchmark/tracing)

---

## Running CLI Tools

### 1. Standalone Graph Validation CLI

Validates the canonical scenario dataset against schema rules, baseline counts, edge directions, and acyclicity:

```bash
python3 scripts/validate_graph.py
```

### 2. Downstream Traversal Benchmark CLI

Executes 1,000 iterations of downstream BFS reachability tracing across both suppliers (`SUP-01` and `SUP-02`) and asserts latency against the 10.0 ms SLA:

```bash
python3 scripts/run_benchmarks.py --iterations 1000 --threshold 10.0
```
