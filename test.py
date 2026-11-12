# =====================================================================
# INTEGRATION TESTING AND VERIFICATION SUITE — SPRINT 1
# ---------------------------------------------------------------------
# FUNCTION INTEGRATION MAPPING:
#   - Core Data Model Structure: Adapted from supply_chain_server.py
#   - Downstream Traversal Logic: Adapted from downstream_traversal.py
# =====================================================================

import time
import platform
import json
import networkx as nx

# ---------------------------------------------------------------------
# 1. GRAPH STRUCTURE MODEL DATA TOPOLOGY
# ---------------------------------------------------------------------
# This structure replicates 'photon_sprint1_graph_data.json' exactly,
# containing 19 unique vertices and 20 directed link pairs.
RAW_MOCK_DATABASE = {
    "nodes": {
        "suppliers": [{"id": "SUP-01", "kind": "supplier", "label": "Supplier 1"}, {"id": "SUP-02", "kind": "supplier", "label": "Supplier 2"}],
        "parts": [
            {"id": "P01", "kind": "part", "label": "Part 1"}, {"id": "P02", "kind": "part", "label": "Part 2"},
            {"id": "P03", "kind": "part", "label": "Part 3"}, {"id": "P04", "kind": "part", "label": "Part 4"}, {"id": "P05", "kind": "part", "label": "Part 5"}
        ],
        "products": [{"id": "F01", "kind": "product", "label": "Product 1"}, {"id": "F02", "kind": "product", "label": "Product 2"}],
        "orders": [
            {"id": "O01", "kind": "order", "label": "Order 1"}, {"id": "O02", "kind": "order", "label": "Order 2"},
            {"id": "O03", "kind": "order", "label": "Order 3"}, {"id": "O04", "kind": "order", "label": "Order 4"},
            {"id": "O05", "kind": "order", "label": "Order 5"}, {"id": "O06", "kind": "order", "label": "Order 6"},
            {"id": "O07", "kind": "order", "label": "Order 7"}, {"id": "O08", "kind": "order", "label": "Order 8"},
            {"id": "O09", "kind": "order", "label": "Order 9"}, {"id": "O10", "kind": "order", "label": "Order 10"}
        ]
    },
    "edges": {
        "supplies": [
            {"source": "SUP-01", "target": "P01", "relation": "SUPPLIES"},
            {"source": "SUP-01", "target": "P02", "relation": "SUPPLIES"},
            {"source": "SUP-02", "target": "P03", "relation": "SUPPLIES"},
            {"source": "SUP-02", "target": "P04", "relation": "SUPPLIES"},
            {"source": "SUP-02", "target": "P05", "relation": "SUPPLIES"}
        ],
        "used_in": [
            {"source": "P01", "target": "F01", "relation": "USED_IN"},
            {"source": "P02", "target": "F01", "relation": "USED_IN"},
            {"source": "P03", "target": "F02", "relation": "USED_IN"},
            {"source": "P04", "target": "F02", "relation": "USED_IN"},
            {"source": "P05", "target": "F02", "relation": "USED_IN"}
        ],
        "fulfills": [
            {"source": "F01", "target": "O01", "relation": "FULFILLS"}, {"source": "F01", "target": "O02", "relation": "FULFILLS"},
            {"source": "F01", "target": "O03", "relation": "FULFILLS"}, {"source": "F01", "target": "O04", "relation": "FULFILLS"},
            {"source": "F01", "target": "O05", "relation": "FULFILLS"}, {"source": "F02", "target": "O06", "relation": "FULFILLS"},
            {"source": "F02", "target": "O07", "relation": "FULFILLS"}, {"source": "F02", "target": "O08", "relation": "FULFILLS"},
            {"source": "F02", "target": "O09", "relation": "FULFILLS"}, {"source": "F02", "target": "O10", "relation": "FULFILLS"}
        ]
    }
}

def _build_graph(raw: dict) -> nx.DiGraph:
    """Graph parsing engine from supply_chain_server.py."""
    G = nx.DiGraph()
    for category in ("suppliers", "parts", "products", "orders"):
        for node in raw["nodes"][category]:
            G.add_node(node["id"], **node)
    for edge_type in ("supplies", "used_in", "fulfills"):
        for edge in raw["edges"][edge_type]:
            G.add_edge(
                edge["source"],
                edge["target"],
                relation=edge["relation"],
                **{k: v for k, v in edge.items() if k not in ("source", "target", "relation")},
            )
    return G

# ---------------------------------------------------------------------
# 2. RUNNING TRAVERSAL ROUTINE DEVISE
# ---------------------------------------------------------------------
def find_downstream_dependencies(graph: nx.DiGraph, supplier_id: str) -> dict:
    """Downstream dependency function from downstream_traversal.py."""
    if supplier_id not in graph:
        raise ValueError(f"Supplier '{supplier_id}' not found.")

    supplier_type = (
        graph.nodes[supplier_id].get("kind")
        or graph.nodes[supplier_id].get("node_type")
    )
    if supplier_type != "supplier":
        raise ValueError(f"'{supplier_id}' is not a supplier.")

    downstream_nodes = nx.descendants(graph, supplier_id)

    result = {"parts": [], "products": [], "orders": []}
    type_mapping = {
        "part": "parts",
        "product": "products",
        "order": "orders",
    }

    for node_id in downstream_nodes:
        node_type = (
            graph.nodes[node_id].get("kind")
            or graph.nodes[node_id].get("node_type")
        )
        category = type_mapping.get(node_type)
        if category is not None:
            result[category].append(node_id)

    for category in result:
        result[category].sort()

    return result

# ---------------------------------------------------------------------
# 3. TIMING SUITE LOG ENGINE
# ---------------------------------------------------------------------
def run_formal_sla_test_audit():
    print("======================================================================")
    print("📋 SPRINT 1 — RUNTIME AUDIT AND LOG VALIDATION ENGINE")
    print("======================================================================")
    
    print("🧬 SYSTEM SPECIFICATIONS:")
    print(f"   • Operating System Platform: {platform.system()} ({platform.release()})")
    print(f"   • Engine Interpreter Local: Python v{platform.python_version()}")
    print(f"   • Hardware Architecture:     {platform.machine()}\n")
    
    # Generate structural graph instance
    GRAPH_INSTANCE = _build_graph(RAW_MOCK_DATABASE)
    node_count = GRAPH_INSTANCE.number_of_nodes()
    edge_count = GRAPH_INSTANCE.number_of_edges()
    
    print("📊 BASELINE GRAPH VALIDATION:")
    print(f"   • Model Structure Array: {node_count} Nodes | {edge_count} Interdependencies")
    print(f"   • Database Integrity Log: {'🟢 MATCH' if node_count == 19 else '🔴 FAULT'}\n")
    
    target_supplier = "SUP-01"
    stress_test_loops = 10000
    target_sla_limit_ms = 10.0
    
    print(f"⏳ RUNNING LOOP REPETITIONS FOR ENGINE VERIFICATION...")
    print(f"   • Traversal Base Root: '{target_supplier}'")
    print(f"   • Target Test Scale:   {stress_test_loops:,} continuous cycles")
    
    # Warm-up pass to eliminate initial compiler overhead variances
    for _ in range(100):
        _ = find_downstream_dependencies(GRAPH_INSTANCE, target_supplier)
        
    # Isolate clock time windows utilizing clean native performance counters
    time_start_marker = time.perf_counter()
    for _ in range(stress_test_loops):
        _ = find_downstream_dependencies(GRAPH_INSTANCE, target_supplier)
    time_end_marker = time.perf_counter()
    
    # Parse out operational speed telemetry
    total_window_seconds = time_end_marker - time_start_marker
    mean_speed_calculated_ms = (total_window_seconds / stress_test_loops) * 1000
    is_compliant = mean_speed_calculated_ms < target_sla_limit_ms
    
    print("\n========================= ATTESTATION RUN MATRIX =========================")
    print(f"⏱️ Evaluation processing window total: {total_window_seconds:.6f} seconds")
    print(f"⚡ Calculated mean function speed:     {mean_speed_calculated_ms:.5f} ms")
    print(f"🎯 Assigned sprint boundary threshold: {target_sla_limit_ms:.2f} ms")
    print(f"📢 Operational SLA Verification:       {'🟢 COMPLIANT' if is_compliant else '🔴 NON-COMPLIANT'}")
    print("=========================================================================\n")

if __name__ == "__main__":
    run_formal_sla_test_audit()
