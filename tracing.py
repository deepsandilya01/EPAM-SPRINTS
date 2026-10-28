"""Downstream tracing with traversal-only timing."""
from time import perf_counter_ns
import networkx as nx

def trace_downstream_with_metrics(graph: nx.DiGraph, source_node_id: str, threshold_ms: float = 10.0) -> dict:
    start = perf_counter_ns()
    exists = source_node_id in graph
    descendants = sorted(nx.descendants(graph, source_node_id)) if exists else []
    elapsed_ms = (perf_counter_ns() - start) / 1_000_000
    return {"source_node_id":source_node_id,"exists":exists,"downstream":descendants,"visited_node_count":len(descendants),"graph_node_count":graph.number_of_nodes(),"graph_edge_count":graph.number_of_edges(),"traversal_elapsed_ms":elapsed_ms,"threshold_ms":threshold_ms,"within_threshold": elapsed_ms < threshold_ms if exists else None,"time_complexity":"O(V + E)"}
