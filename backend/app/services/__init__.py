from __future__ import annotations

from backend.app.services.benchmark_service import BenchmarkService, benchmark_service
from backend.app.services.graph_service import GraphService, service_instance
from backend.app.services.simulation_service import SimulationService, simulation_service
from backend.app.services.validation_service import ValidationService, validation_service

# TraversalService alias for seamless backwards compatibility
TraversalService = GraphService
traversal_service = service_instance

__all__ = [
    "BenchmarkService",
    "GraphService",
    "SimulationService",
    "TraversalService",
    "ValidationService",
    "benchmark_service",
    "service_instance",
    "simulation_service",
    "traversal_service",
    "validation_service",
]
