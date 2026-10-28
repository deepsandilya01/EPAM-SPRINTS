"""Sprint 1 supplier-to-order dependency mapping for Team Photon.

Scope: load the agreed scenario, validate the graph contract, and report downstream
reachability. This module does not predict confirmed disruption or calculate recovery.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import date
from collections import Counter
import networkx as nx

ROOT = Path(__file__).resolve().parent
SCENARIO_PATH = ROOT / "scenario.json"
EXPECTED_PATH = ROOT / "expected_results.json"
EXPECTED_NODE_COUNTS = {"supplier": 2, "part": 5, "product": 2, "order": 10}
EXPECTED_EDGE_COUNTS = {"SUPPLIES": 6, "USED_IN": 5, "FULFILLS": 10}
NODE_REQUIRED = {
    "supplier": {"name", "location", "note"},
    "part": {"name", "stock_on_hand", "daily_consumption"},
    "product": {"name", "parts_needed"},
    "order": {"customer", "product_id", "quantity", "deadline"},
}
EDGE_REQUIRED = {
    "SUPPLIES": {"lead_time_hours", "max_capacity_units_per_day"},
    "USED_IN": {"quantity_per_product"},
    "FULFILLS": set(),
}
EDGE_TYPES = {"SUPPLIES": ("supplier", "part"), "USED_IN": ("part", "product"), "FULFILLS": ("product", "order")}

class ScenarioValidationError(ValueError):
    """Raised when scenario data violates the Sprint 1 contract."""

def load_scenario(path: Path = SCENARIO_PATH) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ScenarioValidationError(f"Scenario file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ScenarioValidationError(f"Malformed scenario JSON: {exc}") from exc

def validate_scenario(scenario: dict, *, enforce_baseline: bool = True) -> None:
    if not isinstance(scenario, dict) or not isinstance(scenario.get("nodes"), list) or not isinstance(scenario.get("edges"), list):
        raise ScenarioValidationError("Scenario must contain 'nodes' and 'edges' lists.")
    ids, kinds = set(), {}
    for i, node in enumerate(scenario["nodes"]):
        if not isinstance(node, dict): raise ScenarioValidationError(f"Node at index {i} must be an object.")
        node_id, kind, attrs = node.get("id"), node.get("kind"), node.get("attributes")
        if not isinstance(node_id, str) or not node_id.strip(): raise ScenarioValidationError(f"Node at index {i} has an empty/invalid ID.")
        if node_id in ids: raise ScenarioValidationError(f"Duplicate node ID across entity types: {node_id}")
        if kind not in NODE_REQUIRED: raise ScenarioValidationError(f"Node {node_id} has unsupported kind: {kind}")
        if not isinstance(attrs, dict): raise ScenarioValidationError(f"Node {node_id} must have an attributes object.")
        missing = NODE_REQUIRED[kind] - attrs.keys()
        if missing: raise ScenarioValidationError(f"Node {node_id} missing required attributes: {sorted(missing)}")
        if any(attrs[k] is None or (isinstance(attrs[k], str) and not attrs[k].strip()) for k in NODE_REQUIRED[kind]):
            raise ScenarioValidationError(f"Node {node_id} has an empty required attribute.")
        if kind == "part":
            if not _number(attrs["stock_on_hand"]) or not _number(attrs["daily_consumption"]): raise ScenarioValidationError(f"Part {node_id} stock/consumption must be numeric.")
            if float(attrs["stock_on_hand"]) < 0 or float(attrs["daily_consumption"]) < 0: raise ScenarioValidationError(f"Part {node_id} stock/consumption cannot be negative.")
        if kind == "order":
            if not _number(attrs["quantity"]) or float(attrs["quantity"]) <= 0: raise ScenarioValidationError(f"Order {node_id} quantity must be positive numeric.")
            try: date.fromisoformat(str(attrs["deadline"]))
            except ValueError as exc: raise ScenarioValidationError(f"Order {node_id} deadline must be an ISO date (YYYY-MM-DD).") from exc
        ids.add(node_id); kinds[node_id] = kind
    if enforce_baseline:
        counts = Counter(n["kind"] for n in scenario["nodes"])
        if dict(counts) != EXPECTED_NODE_COUNTS: raise ScenarioValidationError(f"Expected node counts {EXPECTED_NODE_COUNTS}; got {dict(counts)}")
    seen_edges = set(); edge_counts = Counter()
    for i, edge in enumerate(scenario["edges"]):
        if not isinstance(edge, dict): raise ScenarioValidationError(f"Edge at index {i} must be an object.")
        src, dst, rel, attrs = edge.get("source"), edge.get("target"), edge.get("relation"), edge.get("attributes", {})
        if src not in ids or dst not in ids: raise ScenarioValidationError(f"Edge {src} -{rel}-> {dst} references an unknown endpoint.")
        if rel not in EDGE_TYPES: raise ScenarioValidationError(f"Unsupported relationship label: {rel}")
        if (kinds[src], kinds[dst]) != EDGE_TYPES[rel]: raise ScenarioValidationError(f"Wrong direction/type for {rel} edge {src} -> {dst}.")
        if not isinstance(attrs, dict): raise ScenarioValidationError(f"Attributes for edge {src} -> {dst} must be an object.")
        missing = EDGE_REQUIRED[rel] - attrs.keys()
        if missing: raise ScenarioValidationError(f"{rel} edge {src} -> {dst} missing attributes: {sorted(missing)}")
        if rel == "SUPPLIES":
            for key in EDGE_REQUIRED[rel]:
                if not _number(attrs[key]) or float(attrs[key]) < 0: raise ScenarioValidationError(f"SUPPLIES attribute {key} must be non-negative numeric.")
        if rel == "USED_IN" and (not _number(attrs["quantity_per_product"]) or float(attrs["quantity_per_product"]) <= 0):
            raise ScenarioValidationError("USED_IN quantity_per_product must be positive numeric.")
        key = (src, dst, rel)
        if key in seen_edges: raise ScenarioValidationError(f"Duplicate relationship: {src} -{rel}-> {dst}")
        seen_edges.add(key); edge_counts[rel] += 1
    if enforce_baseline and dict(edge_counts) != EXPECTED_EDGE_COUNTS:
        raise ScenarioValidationError(f"Expected edge counts {EXPECTED_EDGE_COUNTS}; got {dict(edge_counts)}")
    graph = nx.DiGraph()
    for node in scenario["nodes"]: graph.add_node(node["id"], kind=node["kind"], **node["attributes"])
    for edge in scenario["edges"]: graph.add_edge(edge["source"], edge["target"], relation=edge["relation"], **edge.get("attributes", {}))
    if not nx.is_directed_acyclic_graph(graph): raise ScenarioValidationError("Graph must be directed and acyclic.")
    # Each order's product_id must match the product connected to it by FULFILLS.
    for node in scenario["nodes"]:
        if node["kind"] == "order":
            oid, pid = node["id"], node["attributes"]["product_id"]
            if pid not in kinds or kinds[pid] != "product": raise ScenarioValidationError(f"Order {oid} references unknown product {pid}.")
            if not graph.has_edge(pid, oid) or graph[pid][oid]["relation"] != "FULFILLS":
                raise ScenarioValidationError(f"Order {oid} product_id does not match a FULFILLS edge from {pid}.")

def _number(value) -> bool:
    try:
        float(value)
        return not isinstance(value, bool)
    except (TypeError, ValueError):
        return False

def build_graph(scenario: dict | None = None) -> nx.DiGraph:
    scenario = load_scenario() if scenario is None else scenario
    validate_scenario(scenario)
    graph = nx.DiGraph()
    for node in scenario["nodes"]:
        graph.add_node(node["id"], kind=node["kind"], **node["attributes"])
    for edge in scenario["edges"]:
        graph.add_edge(edge["source"], edge["target"], relation=edge["relation"], **edge.get("attributes", {}))
    return graph

def trace_supplier_dependencies(graph: nx.DiGraph, supplier_id: str) -> dict:
    if supplier_id not in graph or graph.nodes[supplier_id].get("kind") != "supplier":
        raise ValueError(f"Unknown supplier ID: {supplier_id}")
    reachable = nx.descendants(graph, supplier_id)
    result = {"supplier_id": supplier_id}
    for kind, key in (("part", "parts"), ("product", "products"), ("order", "orders")):
        result[key] = sorted(n for n in reachable if graph.nodes[n].get("kind") == kind)
    result["order_count"] = len(result["orders"])
    return result

def load_expected_results(path: Path = EXPECTED_PATH) -> dict:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc: raise ScenarioValidationError(f"Could not load expected results: {exc}") from exc

def verify_expected_results(graph: nx.DiGraph, expected: dict | None = None) -> list[dict]:
    expected = load_expected_results() if expected is None else expected
    results = []
    for supplier_id, target in expected.items():
        actual = trace_supplier_dependencies(graph, supplier_id)
        passed = all(actual[k] == sorted(target[k]) for k in ("parts", "products", "orders")) and actual["order_count"] == target["order_count"]
        results.append({"supplier_id": supplier_id, "actual": actual, "passed": passed})
    return results

def main() -> int:
    scenario = load_scenario()
    graph = build_graph(scenario)
    print(f"Scenario: {scenario.get('dataset_name', 'unnamed')}")
    print(f"Graph validation: PASS | {graph.number_of_nodes()} nodes, {graph.number_of_edges()} directed edges | DAG: PASS")
    print("Edge counts: " + ", ".join(f"{rel}={sum(1 for _,_,d in graph.edges(data=True) if d.get('relation')==rel)}" for rel in EDGE_TYPES))
    print("\nSupplier reachability (dependency paths only; not proof of disruption):")
    all_passed = True
    for item in verify_expected_results(graph):
        actual = item["actual"]; all_passed &= item["passed"]
        print(f"{item['supplier_id']}: parts={actual['parts']}; products={actual['products']}; orders={actual['orders']} ({actual['order_count']}) | {'PASS' if item['passed'] else 'FAIL'}")
    print(f"\nExpected-results verification: {'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
