"""
Team Photon — Downstream Tracing Latency Benchmark Utility
──────────────────────────────────────────────────────────
Measures graph reachability traversal latency under strict statistical benchmarking
criteria and verifies that 95th percentile latency is strictly below 10.0 ms.

Usage:
    python -m benchmarks.benchmark_tracing [--iterations 1000] [--threshold-ms 10.0]
"""

import argparse
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import networkx as nx

from graph_validation.tracing import trace_downstream_with_metrics


def _percentile(data: list[float], p: float) -> float:
    """Calculate the p-th percentile of sorted data (0 <= p <= 100)."""
    if not data:
        return 0.0
    k = (len(data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    d0 = data[int(f)] * (c - k)
    d1 = data[int(c)] * (k - f)
    return d0 + d1


def load_canonical_graph(json_path: Path) -> nx.DiGraph:
    """Construct canonical NetworkX DiGraph from the JSON dataset."""
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    G = nx.DiGraph()
    for cat in ("suppliers", "parts", "products", "orders"):
        for node in raw["nodes"].get(cat, []):
            G.add_node(node["id"], **node)

    for edge_type in ("supplies", "used_in", "fulfills"):
        for edge in raw["edges"].get(edge_type, []):
            attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
            G.add_edge(edge["source"], edge["target"], **attrs)

    return G


def run_benchmark(
    graph: nx.DiGraph,
    nodes: list[str],
    warmup_runs: int = 50,
    measured_runs: int = 1000,
    threshold_ms: float = 10.0,
) -> dict[str, Any]:
    """
    Execute downstream tracing benchmark across specified target nodes.
    
    Strict separation:
    - Warm-up iterations ensure JIT/caching/CPU frequency stabilization.
    - Measured iterations record high-resolution traversal latencies only.
    """
    node_results: dict[str, Any] = {}
    all_latencies_ms: list[float] = []

    for nid in nodes:
        if nid not in graph:
            continue

        # 1. Warm-up iterations (discarded)
        for _ in range(warmup_runs):
            trace_downstream_with_metrics(graph, nid, threshold_ms=threshold_ms)

        # 2. Measured iterations
        latencies_ns: list[int] = []
        downstream_ids: list[str] = []

        for _ in range(measured_runs):
            res = trace_downstream_with_metrics(graph, nid, threshold_ms=threshold_ms)
            latencies_ns.append(res["elapsed_ns"])
            if not downstream_ids:
                downstream_ids = res["downstream_node_ids"]

        latencies_ms = sorted([ns / 1_000_000.0 for ns in latencies_ns])
        all_latencies_ms.extend(latencies_ms)

        n = len(latencies_ms)
        min_ms = latencies_ms[0]
        max_ms = latencies_ms[-1]
        mean_ms = sum(latencies_ms) / n
        median_ms = _percentile(latencies_ms, 50.0)
        p90_ms = _percentile(latencies_ms, 90.0)
        p95_ms = _percentile(latencies_ms, 95.0)
        p99_ms = _percentile(latencies_ms, 99.0)

        variance = sum((x - mean_ms) ** 2 for x in latencies_ms) / n
        std_dev_ms = math.sqrt(variance)

        node_passed = p95_ms <= threshold_ms

        node_results[nid] = {
            "node_id": nid,
            "downstream_count": len(downstream_ids),
            "downstream_sample": downstream_ids[:6],
            "iterations": n,
            "min_ms": round(min_ms, 6),
            "max_ms": round(max_ms, 6),
            "mean_ms": round(mean_ms, 6),
            "median_ms": round(median_ms, 6),
            "p90_ms": round(p90_ms, 6),
            "p95_ms": round(p95_ms, 6),
            "p99_ms": round(p99_ms, 6),
            "std_dev_ms": round(std_dev_ms, 6),
            "threshold_ms": threshold_ms,
            "passed_threshold": node_passed,
        }

    # Aggregate statistics
    all_latencies_ms.sort()
    total_runs = len(all_latencies_ms)
    overall_p95 = _percentile(all_latencies_ms, 95.0) if all_latencies_ms else 0.0
    overall_passed = overall_p95 <= threshold_ms and len(all_latencies_ms) > 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "os_system": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "networkx_version": nx.__version__,
        },
        "workload": {
            "graph_nodes": graph.number_of_nodes(),
            "graph_edges": graph.number_of_edges(),
            "target_nodes": nodes,
            "warmup_runs": warmup_runs,
            "measured_runs_per_node": measured_runs,
            "total_measured_runs": total_runs,
            "acceptance_criterion": f"p95 latency <= {threshold_ms} ms",
            "threshold_ms": threshold_ms,
        },
        "aggregate_metrics": {
            "min_ms": round(all_latencies_ms[0], 6) if all_latencies_ms else 0.0,
            "max_ms": round(all_latencies_ms[-1], 6) if all_latencies_ms else 0.0,
            "mean_ms": round(sum(all_latencies_ms) / total_runs, 6) if total_runs else 0.0,
            "median_ms": round(_percentile(all_latencies_ms, 50.0), 6) if total_runs else 0.0,
            "p90_ms": round(_percentile(all_latencies_ms, 90.0), 6) if total_runs else 0.0,
            "p95_ms": round(overall_p95, 6),
            "p99_ms": round(_percentile(all_latencies_ms, 99.0), 6) if total_runs else 0.0,
        },
        "node_benchmarks": node_results,
        "overall_status": "PASS" if overall_passed else "FAIL",
    }


def main():
    parser = argparse.ArgumentParser(description="Team Photon Downstream Tracing Latency Benchmark")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of measured iterations per node (default: 1000)")
    parser.add_argument("--warmup", type=int, default=50, help="Number of warmup iterations per node (default: 50)")
    parser.add_argument("--threshold-ms", type=float, default=10.0, help="Target latency threshold in ms (default: 10.0)")
    parser.add_argument("--nodes", type=str, default="SUP-01,SUP-02", help="Comma-separated node IDs to trace (default: SUP-01,SUP-02)")
    parser.add_argument("--output", type=str, default="reports/graph_benchmark_report.json", help="Output path for benchmark report JSON")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    data_file = base_dir / "photon_sprint1_graph_data.json"
    if not data_file.exists():
        print(f"Error: Data file not found at {data_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading canonical graph from {data_file}...")
    graph = load_canonical_graph(data_file)
    print(f"Graph loaded: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges.")

    target_nodes = [n.strip() for n in args.nodes.split(",") if n.strip()]
    print(f"Running benchmark on nodes: {target_nodes}")
    print(f"Warmup runs: {args.warmup} | Measured runs: {args.iterations} | Threshold: < {args.threshold_ms} ms")

    result = run_benchmark(
        graph=graph,
        nodes=target_nodes,
        warmup_runs=args.warmup,
        measured_runs=args.iterations,
        threshold_ms=args.threshold_ms,
    )

    # Save report
    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = base_dir / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Print summary
    agg = result["aggregate_metrics"]
    print("\n" + "=" * 76)
    print("  TEAM PHOTON — DOWNSTREAM TRACING BENCHMARK RESULTS")
    print("=" * 76)
    print(f"  Overall Status : [{result['overall_status']}]")
    print(f"  Target Nodes   : {', '.join(target_nodes)}")
    print(f"  Total Runs     : {result['workload']['total_measured_runs']}")
    print(f"  Threshold      : < {args.threshold_ms} ms (Criterion: p95 <= {args.threshold_ms} ms)")
    print("-" * 76)
    print(f"  Min Latency    : {agg['min_ms']:>8.4f} ms")
    print(f"  Mean Latency   : {agg['mean_ms']:>8.4f} ms")
    print(f"  Median (p50)   : {agg['median_ms']:>8.4f} ms")
    print(f"  90th Percentile: {agg['p90_ms']:>8.4f} ms")
    print(f"  95th Percentile: {agg['p95_ms']:>8.4f} ms  (Target: < {args.threshold_ms} ms)")
    print(f"  99th Percentile: {agg['p99_ms']:>8.4f} ms")
    print(f"  Max Latency    : {agg['max_ms']:>8.4f} ms")
    print("-" * 76)
    for nid, ndata in result["node_benchmarks"].items():
        status = "PASS" if ndata["passed_threshold"] else "FAIL"
        print(f"  Node {nid:<8} | p95: {ndata['p95_ms']:>6.4f} ms | mean: {ndata['mean_ms']:>6.4f} ms | [{status}] (descendants: {ndata['downstream_count']})")
    print("=" * 76)
    print(f"  Report written to: {out_path}\n")

    sys.exit(0 if result["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()

