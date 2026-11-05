from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.app.services.benchmark_service import BenchmarkService

router = APIRouter()
benchmarks_bp = router
benchmark_service = BenchmarkService()


@router.get("/benchmark/tracing")
@router.get("/benchmarks")
def api_benchmark_tracing(
    node_id: str = Query("SUP-01"),
    threshold_ms: str = Query("10.0"),
):
    """Benchmark downstream traversal speed for a node (default: SUP-01) against the 10ms SLA."""
    result, status_code = benchmark_service.run_tracing_benchmark(
        node_id=node_id, threshold_param=threshold_ms
    )
    return JSONResponse(status_code=status_code, content=result)
