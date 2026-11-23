from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from backend.app.schemas.disruption import DisruptionRequest, SimulationResponse
from backend.app.services.simulation_service import simulation_service

router = APIRouter(tags=["Disruption Simulation"])
disruptions_bp = router


@router.post(
    "/v1/simulation/disrupt",
    response_model=SimulationResponse,
    summary="Simulate supplier disruption pipeline",
    description="Executes the 5-stage simulation pipeline: ripple → inventory → stockout → intervention (<25ms).",
)
@router.post(
    "/disruptions",
    response_model=SimulationResponse,
    summary="Simulate supplier disruption pipeline (alias)",
)
def api_simulate_disruption(request: DisruptionRequest):
    """Run full disruption simulation pipeline."""
    try:
        result = simulation_service.simulate_from_params(
            supplier_id=request.supplier_id,
            delay_duration_hours=request.delay_duration_hours,
            disruption_type=request.disruption_type,
            description=request.description,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}",
        )


@router.get(
    "/v1/simulation/benchmark",
    response_model=SimulationResponse,
    summary="Run canonical 8-hour benchmark scenario",
    description="SUP-01 with 8h delay. Verifies AC-01 through AC-10 oracle targets.",
)
@router.get(
    "/disruptions/benchmark",
    response_model=SimulationResponse,
    summary="Run canonical benchmark scenario (alias)",
)
def api_benchmark_disruption():
    """Run canonical benchmark simulation."""
    try:
        result = simulation_service.simulate_benchmark()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark simulation failed: {str(e)}",
        )
