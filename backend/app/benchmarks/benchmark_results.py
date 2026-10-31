from __future__ import annotations

import json
import math
import pathlib
from typing import Any


def _percentile(data: list[float], p: float) -> float:
    """Calculate the p-th percentile of sorted data (0 <= p <= 100)."""
    if not data:
        return 0.0
    k = (len(data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    return data[int(f)] * (c - k) + data[int(c)] * (k - f)


class BenchmarkResultAggregator:
    """
    Statistical aggregator for benchmark latency measurements.
    """

    def __init__(self, operation_name: str, sla_threshold_ms: float = 10.0) -> None:
        self.operation_name = operation_name
        self.sla_threshold_ms = sla_threshold_ms
        self.latencies_ms: list[float] = []

    def record(self, latency_ms: float) -> None:
        """Record a single execution latency in milliseconds."""
        self.latencies_ms.append(float(latency_ms))

    def compute_statistics(self) -> dict[str, Any]:
        """Compute summary statistics for all recorded latencies."""
        if not self.latencies_ms:
            return {
                "operation": self.operation_name,
                "iterations": 0,
                "status": "PASS",
                "sla_threshold_ms": self.sla_threshold_ms,
                "p50_ms": 0.0,
                "p90_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "mean_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "std_dev_ms": 0.0,
            }

        sorted_vals = sorted(self.latencies_ms)
        n = len(sorted_vals)
        mean_val = sum(sorted_vals) / n
        variance = sum((x - mean_val) ** 2 for x in sorted_vals) / n
        std_dev = math.sqrt(variance)

        p95 = _percentile(sorted_vals, 95.0)
        status = "PASS" if p95 <= self.sla_threshold_ms else "FAIL"

        return {
            "operation": self.operation_name,
            "iterations": n,
            "status": status,
            "sla_threshold_ms": self.sla_threshold_ms,
            "min_ms": round(sorted_vals[0], 6),
            "max_ms": round(sorted_vals[-1], 6),
            "mean_ms": round(mean_val, 6),
            "p50_ms": round(_percentile(sorted_vals, 50.0), 6),
            "p90_ms": round(_percentile(sorted_vals, 90.0), 6),
            "p95_ms": round(p95, 6),
            "p99_ms": round(_percentile(sorted_vals, 99.0), 6),
            "std_dev_ms": round(std_dev, 6),
        }

    def export_json(self, output_path: str | pathlib.Path) -> None:
        """Export aggregated statistics to disk as JSON."""
        stats = self.compute_statistics()
        out = pathlib.Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
