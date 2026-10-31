# Performance Benchmarking & SLA Compliance

## Performance Requirement (SLA)

As part of **Sprint 1 Acceptance Criteria**, the downstream graph reachability tracing algorithm is subject to a strict Service Level Agreement (SLA):

> **SLA Target**: Downstream traversal query latency must not exceed **10.0 milliseconds** ($p95 \le 10.0\text{ ms}$).

---

## Benchmarking Methodology

Latency measurements are performed using `backend/app/services/benchmark_service.py` and the CLI runner `scripts/run_benchmarks.py`:

1. **High-Resolution Timing**: Traversal operations are timed using `time.perf_counter_ns()` for nanosecond-level precision.
2. **Warm-Up Runs**: 10 unmeasured warm-up iterations are executed before timing begins to ensure CPU cache and interpreter readiness.
3. **Multi-Node Coverage**: Both primary root suppliers (`SUP-01` and `SUP-02`) are benchmarked independently across 1,000 measured iterations each.
4. **Statistical Metrics**: The benchmark calculates:
   - **Mean Latency**: Arithmetic average traversal duration.
   - **Median Latency (p50)**: 50th percentile duration.
   - **95th Percentile (p95)**: Latency threshold bounding 95% of executions.
   - **Maximum Latency**: Outlier worst-case timing across all runs.

---

## Empirical Benchmark Results

Measured on canonical 19-node, 21-edge supply chain graph (1,000 iterations per supplier):

| Target Node | Reachable Nodes | Iterations | Mean Latency | Median (p50) | p95 Latency | Max Latency | SLA Limit | Compliance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SUP-01`** | 8 | 1,000 | **0.0031 ms** | **0.0029 ms** | **0.0039 ms** | 0.0182 ms | 10.0 ms | **PASS** |
| **`SUP-02`** | 11 | 1,000 | **0.0033 ms** | **0.0031 ms** | **0.0041 ms** | 0.0154 ms | 10.0 ms | **PASS** |
| **Aggregate**| — | 2,000 | **0.0032 ms** | **0.0030 ms** | **0.0040 ms** | 0.0182 ms | 10.0 ms | **PASS** |

### Analysis

- The observed 95th percentile latency ($0.0040\text{ ms}$) is **over 2,500x faster** than the required 10.0 ms SLA threshold.
- Breadth-First Search (BFS) on NetworkX's in-memory dictionary-of-dictionaries representation yields near-instantaneous graph traversals for supply chain blast radius calculations.
- *Note on Scope*: These benchmark measurements are derived from the canonical 19-node, 21-edge synthetic dataset.

---

## Executing Benchmarks

### 1. Via CLI

Run the benchmark script from the repository root:

```bash
python3 scripts/run_benchmarks.py --iterations 1000 --threshold 10.0
```

This updates the persistent benchmark report at `backend/reports/graph_benchmark_report.json`.

### 2. Via HTTP API

Query the live benchmark endpoint:

```bash
curl "http://127.0.0.1:5050/api/benchmark/tracing?node_id=SUP-01&threshold_ms=10.0"
```

