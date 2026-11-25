import json
from datetime import datetime, timezone
from uuid import uuid4

import networkx as nx

from backend.app.data.loader import load_scenario_dataset
from backend.app.models.disruption import (
    DisruptionEvent,
    DisruptionType
)
from backend.app.simulation.engine import run_disruption_simulation


def build_graph(scenario):

    graph = nx.DiGraph()

    # Load all nodes
    for group in scenario["nodes"].values():
        for node in group:
            graph.add_node(node["id"], **node)

    # Load all relationships
    for group in scenario["edges"].values():
        for edge in group:
            graph.add_edge(
                edge["source"],
                edge["target"],
                **edge
            )

    return graph


def main():

    print("\n========== RE:FLOW SPRINT 2 ==========")

    # 1. Load actual scenario dataset
    scenario = load_scenario_dataset()

    print("\n[1] Scenario dataset loaded successfully")

    # 2. Construct NetworkX graph
    graph = build_graph(scenario)

    print("[2] Supply chain graph constructed")
    print(f"    Nodes: {graph.number_of_nodes()}")
    print(f"    Edges: {graph.number_of_edges()}")

    # 3. Create 8-hour supplier disruption
    event = DisruptionEvent(
        event_id=str(uuid4()),
        supplier_id="SUP-01",
        disruption_type=DisruptionType.SUPPLIER_DELAY,
        delay_duration_hours=8.0,
        created_at=datetime.now(timezone.utc),
        description="8-hour supplier delay test"
    )

    print("\n[3] Disruption event created")
    print("    Supplier: SUP-01")
    print("    Delay: 8 hours")

    # 4. Execute complete simulation pipeline
    result = run_disruption_simulation(
        event=event,
        graph=graph,
        scenario=scenario
    )

    # 5. Display results
    print("\n========== SIMULATION RESULTS ==========")

    print("\nStatus:", result["status"])

    print("\nAffected parts:")
    print(result["impact"]["affected_parts"])

    print("\nAffected products:")
    print(result["impact"]["affected_products"])

    print("\nRipple-affected orders:")
    print(result["impact"]["affected_orders"])

    print("\nCritical part:")
    print(result["critical_part"])

    print("\nStockout prediction:")
    print(json.dumps(result["stockout"], indent=4, default=str))

    print("\nIntervention window:")
    print(json.dumps(result["intervention"], indent=4, default=str))

    print("\nPipeline execution time:")
    print(result["pipeline_elapsed_ms"], "ms")

    print("\nUnder 25 ms:", result["under_25ms"])

    print("\n========== TEST COMPLETED ==========")


if __name__ == "__main__":
    main()