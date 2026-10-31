from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.app.services.benchmark_service import BenchmarkService

benchmarks_bp = Blueprint("benchmarks", __name__)
benchmark_service = BenchmarkService()


@benchmarks_bp.route("/benchmark/tracing", methods=["GET"])
@benchmarks_bp.route("/benchmarks", methods=["GET"])
def api_benchmark_tracing():
    """Benchmark downstream traversal speed for a node (default: SUP-01) against the 10ms SLA."""
    node_id = request.args.get("node_id", "SUP-01")
    threshold_param = request.args.get("threshold_ms", "10.0")

    result, status_code = benchmark_service.run_tracing_benchmark(
        node_id=node_id, threshold_param=threshold_param
    )
    return jsonify(result), status_code
