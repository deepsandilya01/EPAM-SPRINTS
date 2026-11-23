"""
Project: RE:Flow
Sprint: 2
File: backend/app/services/simulation_service.py

Primary Owner: Ansh
Role: Engine Pipeline Architect & Technical Integration Lead

Purpose:
Service layer wrapping the simulation engine for use by API routes
and test harnesses. Manages graph reuse, dataset caching, and provides
a clean interface for Preetam's /api/disruptions endpoint.

Responsibilities:
- Expose SimulationService class with simulate() method.
- Cache one read-only graph instance for repeated simulations (no rebuild).
- Provide factory helpers for the benchmark scenario (SUP-01, 8h delay).
- Validate input parameters before delegating to the engine.

Dependencies:
- Ansh: simulation engine (backend/app/simulation/engine.py)
- Divyanshu: create_disruption_event (backend/app/simulation/events.py)
- GraphService: Sprint 1 graph (backend/app/services/graph_service.py)
- Kanak: scenario_dataset.json (backend/app/data/datasets/)

Deliverables:
- SimulationService class with simulate(), simulate_benchmark(), get_scenario().
- Thread-safe graph access.

Output Goes To:
- Preetam: SimulationService → disruptions route (backend/app/api/routes/disruptions.py)
- Soumya: functions to test (backend/tests/)
- Shanu: function to benchmark (backend/benchmarks/)

Status: COMPLETE
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

import networkx as nx

from backend.app.data.loader import load_scenario_dataset
from backend.app.models.disruption import DisruptionEvent, DisruptionType
from backend.app.services.graph_service import service_instance
from backend.app.simulation.engine import run_disruption_simulation
from backend.app.simulation.events import create_disruption_event

logger = logging.getLogger(__name__)

_SIM_LOCK = threading.RLock()


class SimulationService:
    """High-level service orchestrating disruption simulations.

    Reuses the Sprint 1 graph from GraphService (read-only) and loads
    the scenario dataset once at construction time.

    Attributes
    ----------
    _graph : nx.DiGraph
        Read-only reference to the canonical Sprint 1 graph.
    _scenario : dict
        Full scenario dataset containing node metadata and simulation config.
    """

    def __init__(
        self,
        graph: nx.DiGraph | None = None,
        scenario: Dict[str, Any] | None = None,
    ) -> None:
        self._graph = graph or service_instance.get_graph()
        self._scenario = scenario or load_scenario_dataset()
        self._sim_config = self._scenario.get("simulation", {})

    # ── Core simulation method ───────────────────────────────────────

    def simulate(
        self,
        event: DisruptionEvent,
        *,
        simulation_horizon_hours: int | None = None,
    ) -> Dict[str, Any]:
        """Run the full disruption pipeline for the given event.

        Parameters
        ----------
        event : DisruptionEvent
            Disruption event (from Divyanshu's events.py / create_disruption_event).
        simulation_horizon_hours : int, optional
            Override simulation window (default: from dataset or 72).

        Returns
        -------
        dict
            Complete simulation result with event, impact, depletion,
            stockout, intervention, timing, and pipeline_elapsed_ms.

        Raises
        ------
        ValueError
            If the supplier_id in the event is not present in the graph.
        """
        if event.supplier_id not in self._graph:
            raise ValueError(
                f"Supplier '{event.supplier_id}' not found in graph. "
                f"Available suppliers: {[n for n, d in self._graph.nodes(data=True) if d.get('kind') == 'supplier']}"
            )

        with _SIM_LOCK:
            return run_disruption_simulation(
                event=event,
                graph=self._graph,
                scenario=self._scenario,
                simulation_horizon_hours=simulation_horizon_hours,
            )

    # ── Convenience factories ────────────────────────────────────────

    def simulate_from_params(
        self,
        supplier_id: str,
        delay_duration_hours: float = 8.0,
        disruption_type: str = "SUPPLIER_DELAY",
        description: str = "",
        *,
        simulation_horizon_hours: int | None = None,
    ) -> Dict[str, Any]:
        """Create a DisruptionEvent from raw parameters and simulate.

        This is the method Preetam's /api/disruptions route should call
        when receiving a POST payload.
        """
        dtype = DisruptionType(disruption_type)
        event = create_disruption_event(
            supplier_id=supplier_id,
            disruption_type=dtype,
            delay_duration_hours=delay_duration_hours,
            description=description,
        )
        return self.simulate(
            event, simulation_horizon_hours=simulation_horizon_hours,
        )

    def simulate_benchmark(self) -> Dict[str, Any]:
        """Run the canonical benchmark scenario: SUP-01 with 8h delay.

        Expected Results (AC-01 through AC-10)
        --------------------------------------
        - event.delay_duration_hours == 8.0
        - event.supplier_id == "SUP-01"
        - Downstream parts, products, orders identified
        - Critical part PART-05: 10 units, 1.25/hr → stockout at hour 8
        - Exactly 2 breached orders: ORD-01, ORD-02
        - ΔT == 3.0h, status == "FEASIBLE"
        - Pipeline < 25 ms
        """
        disruption_hours = float(
            self._sim_config.get("disruption_duration_hours", 8.0)
        )
        event = create_disruption_event(
            supplier_id="SUP-01",
            disruption_type=DisruptionType.SUPPLIER_DELAY,
            delay_duration_hours=disruption_hours,
            description="Benchmark scenario — 8-hour supplier delay at SUP-01",
        )
        return self.simulate(event)

    # ── Accessors ────────────────────────────────────────────────────

    def get_scenario(self) -> Dict[str, Any]:
        """Return the loaded scenario dataset."""
        return self._scenario

    def get_graph(self) -> nx.DiGraph:
        """Return the read-only graph reference."""
        return self._graph

    def get_simulation_config(self) -> Dict[str, Any]:
        """Return the simulation config block from the dataset."""
        return dict(self._sim_config)


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors GraphService pattern)
# ---------------------------------------------------------------------------
simulation_service = SimulationService()

__all__ = ["SimulationService", "simulation_service"]
