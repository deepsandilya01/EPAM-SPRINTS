"""
Project: RE:Flow
Sprint: 2
File: backend/app/simulation/engine.py

Primary Owner: Ansh
Role: Engine Pipeline Architect & Technical Integration Lead

Purpose:
Orchestrated disruption simulation pipeline that chains all 5 team member
modules into a single end-to-end execution:
  events (Divyanshu) → ripple (Aadee) → inventory (Sonal)
  → stockout (Anushka) → intervention (Mishti)

Responsibilities:
- Accept a DisruptionEvent and produce the complete simulation result.
- Reuse a *read-only* copy of the Sprint 1 graph (never mutate).
- Complete full pipeline execution in < 25 ms.
- Extract part-level stock/consumption from the scenario dataset.
- Select the critical (first-to-stockout) part for inventory simulation.
- Return all five outputs: event, impact, depletion timeline, stockout, intervention.

Dependencies:
- Divyanshu: DisruptionEvent model  (backend/app/models/disruption.py)
- Aadee:     propagate_ripple_effect (backend/app/simulation/ripple.py)
- Sonal:     simulate_inventory_depletion (backend/app/simulation/inventory.py)
- Anushka:   predict_stockout_and_orders  (backend/app/simulation/stockout.py)
- Mishti:    compute_intervention_window  (backend/app/simulation/intervention.py)
- Kanak:     scenario_dataset.json        (backend/app/data/datasets/)

Deliverables:
- run_disruption_simulation() returning complete SimulationResult.
- Pipeline latency < 25 ms on the benchmark scenario.
- Sprint 1 graph never mutated.

Status: COMPLETE
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from backend.app.models.disruption import DisruptionEvent
from backend.app.models.impact import RippleImpactSummary
from backend.app.models.inventory import InventoryDepletionTimeline
from backend.app.models.stockout import StockoutPredictionResult

from backend.app.simulation.ripple import propagate_ripple_effect
from backend.app.simulation.inventory import simulate_inventory_depletion
from backend.app.simulation.stockout import predict_stockout_and_orders
from backend.app.simulation.intervention import calculate_intervention_window


# ---------------------------------------------------------------------------
# Data adapter helpers — resolve IDs and stock from the scenario dataset
# ---------------------------------------------------------------------------

def _extract_parts_for_supplier(
    scenario: Dict[str, Any],
    graph: nx.DiGraph,
    supplier_id: str,
) -> List[Dict[str, Any]]:
    """Return part dicts downstream of *supplier_id* that carry stock metadata.

    Walks the graph to find PART-* successors, then looks them up in the
    scenario dataset's ``nodes.parts`` list for initial_stock and consumption.
    """
    # Build a lookup from the dataset parts list
    parts_by_id: Dict[str, Dict[str, Any]] = {}
    nodes_section = scenario.get("nodes", {})
    for part in nodes_section.get("parts", []):
        pid = part.get("id") or part.get("part_id", "")
        parts_by_id[pid] = part

    # Traverse graph to find downstream parts
    result: List[Dict[str, Any]] = []
    for successor in graph.successors(supplier_id):
        node_data = graph.nodes.get(successor, {})
        raw_kind = (
            node_data.get("kind")
            or node_data.get("type")
            or node_data.get("tier")
            or ""
        )
        if str(raw_kind).strip().upper() in ("PART", "PARTS", "BOM_PART") or successor.startswith(("PART-", "P-")):
            ds_part = parts_by_id.get(successor, node_data)
            result.append({
                "part_id": successor,
                "initial_stock": float(
                    ds_part.get("initial_stock_units")
                    or ds_part.get("stock_on_hand")
                    or 0
                ),
                "hourly_consumption": float(
                    ds_part.get("hourly_consumption_units")
                    or ds_part.get("daily_consumption", 0) / 24.0
                ),
            })

    return result


def _find_critical_part(
    parts: List[Dict[str, Any]],
    delay_hours: float,
) -> Optional[Dict[str, Any]]:
    """Select the part that stocks out first (minimum hours-to-zero).

    For the benchmark scenario with PART-05 (10 units, 1.25/hr) this returns
    PART-05 with stockout at hour 8.
    """
    best: Optional[Dict[str, Any]] = None
    best_hours: float = float("inf")

    for p in parts:
        consumption = p["hourly_consumption"]
        stock = p["initial_stock"]
        if consumption <= 0:
            continue
        hours_to_zero = stock / consumption
        if hours_to_zero < best_hours:
            best_hours = hours_to_zero
            best = p

    return best


def _extract_order_deadlines(
    scenario: Dict[str, Any],
    affected_order_ids: List[str],
) -> Dict[str, float]:
    """Build {order_id: delivery_deadline_hours} from the dataset."""
    orders_by_id: Dict[str, Dict[str, Any]] = {}
    nodes_section = scenario.get("nodes", {})
    for order in nodes_section.get("orders", []):
        oid = order.get("id") or order.get("order_id", "")
        orders_by_id[oid] = order

    deadlines: Dict[str, float] = {}
    for oid in affected_order_ids:
        order = orders_by_id.get(oid, {})
        deadline = order.get("delivery_deadline_hours")
        if deadline is not None:
            deadlines[oid] = float(deadline)

    return deadlines


def _get_recovery_lead_time(
    scenario: Dict[str, Any],
    supplier_id: str,
) -> float:
    """Read the supplier's recovery_lead_time_hours from the dataset (default 5.0)."""
    nodes_section = scenario.get("nodes", {})
    for sup in nodes_section.get("suppliers", []):
        sid = sup.get("id") or sup.get("supplier_id", "")
        if sid == supplier_id:
            return float(sup.get("recovery_lead_time_hours", 5.0))
    return 5.0


# ---------------------------------------------------------------------------
# Main pipeline entry point
# ---------------------------------------------------------------------------

def run_disruption_simulation(
    event: DisruptionEvent,
    graph: nx.DiGraph,
    scenario: Dict[str, Any],
    *,
    simulation_horizon_hours: int | None = None,
) -> Dict[str, Any]:
    """Execute the full 5-stage disruption simulation pipeline.

    Stages
    ------
    1. **Ripple propagation** (Aadee) — BFS downstream from disrupted supplier
    2. **Inventory depletion** (Sonal) — hourly stock curve for critical part
    3. **Stockout prediction** (Anushka) — breached customer orders
    4. **Intervention window** (Mishti) — ΔT feasibility calculation
    5. **Result assembly** — unified JSON payload with timing metrics

    Parameters
    ----------
    event : DisruptionEvent
        The disruption to simulate (created by Divyanshu's events.py).
    graph : nx.DiGraph
        **Read-only** Sprint 1 graph. The function never mutates it.
    scenario : dict
        Full scenario dataset (from loader.py) containing node metadata
        with stock levels, consumption rates, and order deadlines.
    simulation_horizon_hours : int, optional
        Override for the simulation window (default: from dataset or 72).

    Returns
    -------
    dict
        Complete simulation result with keys: event, impact, depletion,
        stockout, intervention, timing, and pipeline_elapsed_ms.
    """
    t_pipeline_start = time.perf_counter_ns()

    # --- Read simulation config from dataset ---
    sim_config = scenario.get("simulation", {})
    if simulation_horizon_hours is None:
        simulation_horizon_hours = int(sim_config.get("simulation_horizon_hours", 72))

    # ── Stage 1: Ripple propagation (Aadee) ──────────────────────────
    t0 = time.perf_counter_ns()
    impact: RippleImpactSummary = propagate_ripple_effect(graph, event)
    t_ripple_ns = time.perf_counter_ns() - t0

    # ── Stage 2: Inventory depletion (Sonal) ─────────────────────────
    t0 = time.perf_counter_ns()

    # Find all affected parts and pick the critical (first-to-stockout) part
    affected_parts_data = _extract_parts_for_supplier(
        scenario, graph, event.supplier_id,
    )
    critical_part = _find_critical_part(
        affected_parts_data, event.delay_duration_hours,
    )

    if critical_part is not None:
        depletion: InventoryDepletionTimeline = simulate_inventory_depletion(
            part_id=critical_part["part_id"],
            initial_stock=critical_part["initial_stock"],
            hourly_consumption=critical_part["hourly_consumption"],
            delay_duration_hours=event.delay_duration_hours,
            simulation_horizon_hours=simulation_horizon_hours,
        )
    else:
        # No parts affected — create a no-stockout depletion
        depletion = InventoryDepletionTimeline(
            part_id="NONE",
            initial_stock=0.0,
            hourly_consumption=0.0,
            delay_hours=event.delay_duration_hours,
            timeline=[],
            stockout_hour=None,
        )
    t_inventory_ns = time.perf_counter_ns() - t0

    # ── Stage 3: Stockout & breached orders (Anushka) ────────────────
    t0 = time.perf_counter_ns()

    order_deadlines = _extract_order_deadlines(
        scenario, impact.affected_orders,
    )
    recovery_lead_time = _get_recovery_lead_time(scenario, event.supplier_id)

    stockout: StockoutPredictionResult = predict_stockout_and_orders(
        depletion=depletion,
        impact=impact,
        order_deadlines=order_deadlines,
        recovery_lead_time_hours=recovery_lead_time,
    )
    t_stockout_ns = time.perf_counter_ns() - t0

    # ── Stage 4: Intervention window (Mishti) ────────────────────────
    t0 = time.perf_counter_ns()
    intervention_res = calculate_intervention_window(
        stockout_result=stockout,
        current_hour=0.0,
        recovery_lead_time_hours=recovery_lead_time,
    )
    intervention = (
        intervention_res.model_dump()
        if hasattr(intervention_res, "model_dump")
        else intervention_res
    )
    t_intervention_ns = time.perf_counter_ns() - t0

    # ── Stage 5: Assemble result ─────────────────────────────────────
    t_pipeline_total_ns = time.perf_counter_ns() - t_pipeline_start
    t_pipeline_ms = round(t_pipeline_total_ns / 1_000_000, 4)

    depletion_data = depletion.model_dump()

    return {
        "status": "success",
        "event": event.model_dump(),
        "impact": impact.model_dump(),
        "depletion": depletion_data,
        "depletion_timeline": depletion_data.get("timeline", []),
        "stockout": stockout.model_dump(),
        "intervention": intervention,
        "critical_part": critical_part,
        "timing": {
            "ripple_ns": t_ripple_ns,
            "ripple_ms": round(t_ripple_ns / 1_000_000, 4),
            "inventory_ns": t_inventory_ns,
            "inventory_ms": round(t_inventory_ns / 1_000_000, 4),
            "stockout_ns": t_stockout_ns,
            "stockout_ms": round(t_stockout_ns / 1_000_000, 4),
            "intervention_ns": t_intervention_ns,
            "intervention_ms": round(t_intervention_ns / 1_000_000, 4),
            "pipeline_total_ns": t_pipeline_total_ns,
            "pipeline_total_ms": t_pipeline_ms,
        },
        "pipeline_elapsed_ms": t_pipeline_ms,
        "execution_time_ms": t_pipeline_ms,
        "under_25ms": t_pipeline_ms < 25.0,
    }


__all__ = ["run_disruption_simulation"]
