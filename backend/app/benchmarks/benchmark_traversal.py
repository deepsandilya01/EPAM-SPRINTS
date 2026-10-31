"""
Project: RE:Flow
Sprint: 1
File: backend/app/benchmarks/benchmark_traversal.py

Primary Owner: Kanak
Role: Performance Benchmarking

Purpose:
Benchmark runner for measuring downstream traversal execution speed.

Responsibilities:
- Benchmark downstream BFS traversal from each supplier and intermediate node.
- Run 1,000 iterations to measure min, mean, p50, p95, and max latency.
- Evaluate traversal performance against the strict under-10-ms SLA target.
- Flag any latency violations exceeding 10 ms.

Dependencies:
- Preetam: Traversal algorithm in backend/app/graph/traversal.py.
- Ansh: Populated graph instance.

Deliverables:
- run_traversal_benchmark() function returning verified latency metrics.

Status: NOT STARTED
"""
