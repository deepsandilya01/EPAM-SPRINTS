# Downstream Tracing Latency Benchmarks

This directory contains statistical latency benchmarks for downstream reachability tracing across the canonical discrete manufacturing supply-chain graph.

## Benchmark Target
The Sprint 1 performance requirement states that 95th percentile latency ($p_{95}$) for downstream reachability traversal must be **strictly below 10.0 milliseconds** (`< 10.0 ms`).

## Running the Benchmark

From repository root:
```bash
python -m backend.benchmarks.benchmark_tracing --iterations 1000 --threshold-ms 10.0
```

Or from within `backend/`:
```bash
python -m benchmarks.benchmark_tracing --iterations 1000 --threshold-ms 10.0
```

### CLI Parameters
- `--iterations`: Number of measured iterations per target node (default: `1000`)
- `--warmup`: Number of warmup runs prior to measurement (default: `50`)
- `--threshold-ms`: Performance SLA limit in milliseconds (default: `10.0`)
- `--nodes`: Comma-separated node identifiers to benchmark (default: `SUP-01,SUP-02`)
- `--output`: Filepath to output JSON results (default: `backend/reports/graph_benchmark_report.json`)
