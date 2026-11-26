"""
Project: RE:Flow
Sprint: 2
File: backend/benchmarks/benchmark_simulation.py

Primary Owner: Shanu (Feature 11 — Performance SLA Benchmarking)
Role: Performance Engineering & Latency Verification Specialist

Purpose:
Execute a 1,000-iteration latency benchmark of the full 5-stage disruption
simulation pipeline (`run_disruption_simulation`) and statistically prove
that end-to-end execution remains well below the 25.0 ms SLA target.

Outputs:
- Console statistical SLA summary table
- JSON report at `backend/reports/simulation_benchmark_report.json`
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from typing import Any

import networkx as nx

try:
    from datetime import UTC  # type: ignore[attr-defined]
except ImportError:
    UTC = timezone.utc  # noqa: UP017

# Ensure repository root is on sys.path for direct CLI execution
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.app.benchmarks.benchmark_results import _percentile  # noqa: E402
from backend.app.data.loader import load_scenario_dataset  # noqa: E402
from backend.app.models.disruption import DisruptionType  # noqa: E402
from backend.app.services.graph_service import service_instance  # noqa: E402
from backend.app.simulation.engine import run_disruption_simulation  # noqa: E402
from backend.app.simulation.events import create_disruption_event  # noqa: E402


def _compute_stats(values_ms: list[float]) -> dict[str, float]:
    """Compute latency summary statistics (all values in milliseconds)."""
    ordered = sorted(values_ms)
    n = len(ordered)
    if n == 0:
        return {
            "min_ms": 0.0,
            "max_ms": 0.0,
            "mean_ms": 0.0,
            "median_ms": 0.0,
            "p90_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "std_dev_ms": 0.0,
        }

    mean_val = statistics.fmean(ordered)
    variance = sum((x - mean_val) ** 2 for x in ordered) / n
    return {
        "min_ms": round(ordered[0], 6),
        "max_ms": round(ordered[-1], 6),
        "mean_ms": round(mean_val, 6),
        "median_ms": round(_percentile(ordered, 50.0), 6),
        "p90_ms": round(_percentile(ordered, 90.0), 6),
        "p95_ms": round(_percentile(ordered, 95.0), 6),
        "p99_ms": round(_percentile(ordered, 99.0), 6),
        "std_dev_ms": round(math.sqrt(variance), 6),
    }


def run_simulation_benchmark(
    iterations: int = 1000,
    warmup_runs: int = 50,
    sla_target_ms: float = 25.0,
    supplier_id: str = "SUP-01",
    delay_duration_hours: float = 8.0,
) -> dict[str, Any]:
    """Run ``iterations`` executions of the full disruption simulation pipeline.

    Strict separation between warm-up iterations (discarded) and measured
    iterations using ``time.perf_counter_ns()``. Also validates benchmark
    oracle invariants and graph immutability.
    """
    graph = service_instance.get_graph()
    scenario = load_scenario_dataset()

    initial_nodes = graph.number_of_nodes()
    initial_edges = graph.number_of_edges()

    event = create_disruption_event(
        supplier_id=supplier_id,
        disruption_type=DisruptionType.SUPPLIER_DELAY,
        delay_duration_hours=delay_duration_hours,
        description="Sprint 2 Feature 11 SLA benchmark run",
    )

    # 1. Warm-up iterations (discarded)
    for _ in range(warmup_runs):
        run_disruption_simulation(event=event, graph=graph, scenario=scenario)

    # 2. Measured iterations
    latencies_ms: list[float] = []
    stage_samples: dict[str, list[float]] = {
        "ripple_ms": [],
        "inventory_ms": [],
        "stockout_ms": [],
        "intervention_ms": [],
    }
    last_result: dict[str, Any] = {}

    for _ in range(iterations):
        t_start = time.perf_counter_ns()
        result = run_disruption_simulation(event=event, graph=graph, scenario=scenario)
        t_end = time.perf_counter_ns()

        latencies_ms.append((t_end - t_start) / 1_000_000.0)

        timing = result.get("timing", {})
        stage_samples["ripple_ms"].append(timing.get("ripple_ns", 0) / 1_000_000.0)
        stage_samples["inventory_ms"].append(timing.get("inventory_ns", 0) / 1_000_000.0)
        stage_samples["stockout_ms"].append(timing.get("stockout_ns", 0) / 1_000_000.0)
        stage_samples["intervention_ms"].append(timing.get("intervention_ns", 0) / 1_000_000.0)
        last_result = result

    # 3. Statistical aggregation
    metrics = _compute_stats(latencies_ms)
    under_sla_count = sum(1 for ms in latencies_ms if ms < sla_target_ms)
    sla_compliance_pct = round((under_sla_count / iterations) * 100.0, 4) if iterations else 0.0
    sla_met = (
        iterations > 0
        and metrics["p99_ms"] < sla_target_ms
        and under_sla_count == iterations
    )

    stage_breakdown = {
        stage: _compute_stats(samples) for stage, samples in stage_samples.items()
    }

    # 4. Oracle & immutability verification
    graph_unmutated = (
        graph.number_of_nodes() == initial_nodes
        and graph.number_of_edges() == initial_edges
    )
    breached_ids = [
        o["order_id"]
        for o in last_result.get("stockout", {}).get("breached_orders", [])
    ]
    oracle_verified = (
        last_result.get("stockout", {}).get("stockout_hour") == 8.0
        and last_result.get("stockout", {}).get("total_breached") == 2
        and set(breached_ids) == {"ORD-01", "ORD-02"}
        and last_result.get("intervention", {}).get("delta_t_hours") == 3.0
        and last_result.get("intervention", {}).get("status") == "FEASIBLE"
        and graph_unmutated
    )

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "benchmark_name": "RE:Flow Sprint 2 Disruption Simulation Pipeline SLA Benchmark",
        "owner": "Shanu (Feature 11)",
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
            "supplier_id": supplier_id,
            "disruption_type": DisruptionType.SUPPLIER_DELAY.value,
            "delay_duration_hours": delay_duration_hours,
            "simulation_horizon_hours": scenario.get("simulation", {}).get("simulation_horizon_hours", 72),
            "graph_nodes": initial_nodes,
            "graph_edges": initial_edges,
            "warmup_runs": warmup_runs,
            "iterations": iterations,
            "sla_target_ms": sla_target_ms,
            "acceptance_criterion": f"100% of runs & P99 latency < {sla_target_ms} ms",
        },
        "metrics": metrics,
        "p50_ms": metrics["median_ms"],
        "p90_ms": metrics["p90_ms"],
        "p95_ms": metrics["p95_ms"],
        "p99_ms": metrics["p99_ms"],
        "mean_ms": metrics["mean_ms"],
        "min_ms": metrics["min_ms"],
        "max_ms": metrics["max_ms"],
        "std_dev_ms": metrics["std_dev_ms"],
        "sla_target_ms": sla_target_ms,
        "iterations": iterations,
        "under_sla_count": under_sla_count,
        "sla_compliance_pct": sla_compliance_pct,
        "sla_met": sla_met,
        "overall_status": "PASS" if (sla_met and oracle_verified) else "FAIL",
        "oracle_verification": {
            "verified": oracle_verified,
            "graph_unmutated": graph_unmutated,
            "critical_part": last_result.get("critical_part", {}).get("part_id"),
            "stockout_hour": last_result.get("stockout", {}).get("stockout_hour"),
            "total_breached": last_result.get("stockout", {}).get("total_breached"),
            "breached_order_ids": breached_ids,
            "delta_t_hours": last_result.get("intervention", {}).get("delta_t_hours"),
            "intervention_status": last_result.get("intervention", {}).get("status"),
        },
        "stage_breakdown": stage_breakdown,
    }


def _print_console_report(report: dict[str, Any]) -> None:
    """Print formatted SLA verification summary to stdout."""
    m = report["metrics"]
    oracle = report["oracle_verification"]
    print("=" * 68)
    print("  RE:Flow Sprint 2 — Simulation Pipeline Performance SLA Benchmark")
    print("=" * 68)
    print(f"  Iterations     : {report['iterations']} (Warm-up: {report['workload']['warmup_runs']})")
    print(f"  SLA Target     : < {report['sla_target_ms']} ms")
    print(f"  Under SLA      : {report['under_sla_count']}/{report['iterations']} ({report['sla_compliance_pct']}%)")
    print("-" * 68)
    print(f"  Min Latency    : {m['min_ms']:.6f} ms")
    print(f"  Mean Latency   : {m['mean_ms']:.6f} ms")
    print(f"  Median (P50)   : {m['median_ms']:.6f} ms")
    print(f"  P90 Latency    : {m['p90_ms']:.6f} ms")
    print(f"  P95 Latency    : {m['p95_ms']:.6f} ms")
    print(f"  P99 Latency    : {m['p99_ms']:.6f} ms")
    print(f"  Max Latency    : {m['max_ms']:.6f} ms")
    print(f"  Std Deviation  : {m['std_dev_ms']:.6f} ms")
    print("-" * 68)
    print(f"  Oracle Check   : {'PASS' if oracle['verified'] else 'FAIL'} "
          f"(Part={oracle['critical_part']}, T_stockout={oracle['stockout_hour']}h, "
          f"Breached={oracle['breached_order_ids']}, dT=+{oracle['delta_t_hours']}h)")
    print(f"  SLA Met        : {report['sla_met']} | Overall Status: {report['overall_status']}")
    print("=" * 68)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RE:Flow Sprint 2 Disruption Simulation Pipeline Benchmark"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of measured simulation runs (default: 1000)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=50,
        help="Number of warmup runs before measurement (default: 50)",
    )
    parser.add_argument(
        "--sla-ms",
        type=float,
        default=25.0,
        help="SLA threshold in milliseconds (default: 25.0)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backend/reports/simulation_benchmark_report.json",
        help="Output path for JSON benchmark report",
    )
    args = parser.parse_args()

    report = run_simulation_benchmark(
        iterations=args.iterations,
        warmup_runs=args.warmup,
        sla_target_ms=args.sla_ms,
    )

    out_path = pathlib.Path(args.output)
    if not out_path.is_absolute():
        out_path = _REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    _print_console_report(report)
    print(f"  JSON Report    : {out_path}")

    assert report["sla_met"], f"SLA VIOLATED: P99={report['p99_ms']}ms >= {args.sla_ms}ms"
    assert report["oracle_verification"]["verified"], "Oracle verification failed during benchmark"
    sys.exit(0)


if __name__ == "__main__":
    main()
