"""Defensive raw-data and NetworkX graph validation."""
from __future__ import annotations
import json
from collections import Counter
from typing import Any
import networkx as nx
from .schema import NODE_CATEGORIES, RELATIONSHIP_CATEGORIES, EXPECTED_NODE_COUNTS, EXPECTED_EDGE_COUNTS, NODE_REQUIRED_FIELDS, EDGE_REQUIRED_FIELDS, ValidationPolicy

def _issue(code: str, message: str, severity: str = "ERROR", **extra: Any) -> dict:
    return {"code": code, "severity": severity, "message": message, **extra}

def validate_graph_data(raw_data: Any, policy: ValidationPolicy | None = None) -> dict:
    policy = policy or ValidationPolicy()
    errors, warnings, checks = [], [], []
    def check(cid, ok, message, detail=None):
        checks.append({"check_id": cid, "status": "PASS" if ok else "FAIL", "message": message, **({"details": detail} if detail else {})})
    if not isinstance(raw_data, dict):
        errors.append(_issue("INVALID_TOP_LEVEL", "Graph JSON root must be an object.", actual_type=type(raw_data).__name__))
        return {"valid": False, "graph_name": "Team Photon Sprint 1", "summary": {}, "checks": [], "errors": errors, "warnings": [], "policy": policy.__dict__}
    nodes_obj, edges_obj = raw_data.get("nodes"), raw_data.get("edges")
    if not isinstance(nodes_obj, dict) or not isinstance(edges_obj, dict):
        errors.append(_issue("MISSING_STRUCTURE", "'nodes' and 'edges' must both be objects."))
        return {"valid": False, "graph_name": "Team Photon Sprint 1", "summary": {}, "checks": [], "errors": errors, "warnings": [], "policy": policy.__dict__}
    ids, node_types, node_records = [], {}, []
    for category, kind in NODE_CATEGORIES.items():
        records = nodes_obj.get(category)
        if not isinstance(records, list):
            errors.append(_issue("MISSING_NODE_CATEGORY", f"nodes.{category} must be a list.", category=category))
            continue
        for i, node in enumerate(records):
            if not isinstance(node, dict):
                errors.append(_issue("INVALID_NODE_RECORD", f"nodes.{category}[{i}] must be an object.", category=category, index=i)); continue
            nid = node.get("id")
            if not isinstance(nid, str) or not nid.strip():
                errors.append(_issue("MISSING_NODE_ID", f"nodes.{category}[{i}] has a missing or invalid id.", category=category, index=i)); continue
            if nid in ids: errors.append(_issue("DUPLICATE_NODE_ID", f"Duplicate node ID {nid} detected before graph construction.", node_id=nid))
            ids.append(nid); node_types[nid] = kind; node_records.append(node)
            if node.get("kind") != kind:
                errors.append(_issue("INVALID_NODE_KIND", f"Node {nid} must have kind '{kind}'.", node_id=nid, expected=kind, actual=node.get("kind")))
            for field, typ in NODE_REQUIRED_FIELDS[kind].items():
                if field not in node: errors.append(_issue("MISSING_NODE_FIELD", f"Node {nid} is missing required field '{field}'.", node_id=nid, field=field))
                elif not isinstance(node[field], typ) or (typ is str and not node[field].strip()):
                    errors.append(_issue("INVALID_NODE_FIELD", f"Node {nid} field '{field}' has an invalid value/type.", node_id=nid, field=field, expected=str(typ), actual=type(node[field]).__name__))
    edge_records, edge_counts = [], Counter()
    for category, expected_pair in RELATIONSHIP_CATEGORIES.items():
        records = edges_obj.get(category)
        if not isinstance(records, list):
            errors.append(_issue("MISSING_EDGE_CATEGORY", f"edges.{category} must be a list.", category=category)); continue
        for i, edge in enumerate(records):
            if not isinstance(edge, dict):
                errors.append(_issue("INVALID_EDGE_RECORD", f"edges.{category}[{i}] must be an object.", category=category, index=i)); continue
            for field, typ in EDGE_REQUIRED_FIELDS.items():
                if field not in edge: errors.append(_issue("MISSING_EDGE_FIELD", f"Edge in {category}[{i}] missing '{field}'.", category=category, index=i, field=field))
                elif not isinstance(edge[field], typ) or not edge[field].strip(): errors.append(_issue("INVALID_EDGE_FIELD", f"Edge {category}[{i}] has invalid '{field}'.", category=category, index=i, field=field))
            source, target = edge.get("source"), edge.get("target")
            if source not in node_types: errors.append(_issue("INVALID_EDGE_REFERENCE", f"Edge source {source!r} does not exist.", edge={"source":source,"target":target}, field="source"))
            if target not in node_types: errors.append(_issue("INVALID_EDGE_REFERENCE", f"Edge target {target!r} does not exist.", edge={"source":source,"target":target}, field="target"))
            if source in node_types and target in node_types and (node_types[source], node_types[target]) != expected_pair:
                errors.append(_issue("INVALID_EDGE_DIRECTION", f"{category} edge must point {expected_pair[0]} → {expected_pair[1]}.", edge={"source":source,"target":target}, expected=expected_pair, actual=(node_types[source],node_types[target])))
            if edge.get("relation") != category.upper():
                errors.append(_issue("INVALID_RELATIONSHIP_TYPE", f"Relationship in edges.{category} must be '{category.upper()}'.", actual=edge.get("relation"), expected=category.upper()))
            edge_counts[category] += 1; edge_records.append(edge)
    for category, kind in NODE_CATEGORIES.items():
        actual = sum(1 for k in node_types.values() if k == kind)
        if policy.check_baseline_counts: check(f"NODE_COUNT_{kind.upper()}", actual == EXPECTED_NODE_COUNTS[kind], f"{kind} count: expected {EXPECTED_NODE_COUNTS[kind]}, found {actual}.")
    if policy.check_baseline_counts:
        check("TOTAL_NODE_COUNT", len(ids) == sum(EXPECTED_NODE_COUNTS.values()), f"Total nodes: expected 19, found {len(ids)}.")
        check("TOTAL_EDGE_COUNT", len(edge_records) == sum(EXPECTED_EDGE_COUNTS.values()), f"Total edges: expected 21, found {len(edge_records)}.")
        for rel, expected in EXPECTED_EDGE_COUNTS.items():
            check(f"EDGE_COUNT_{rel.upper()}", edge_counts[rel] == expected, f"{rel} edges: expected {expected}, found {edge_counts[rel]}.")
    graph = nx.DiGraph()
    graph.add_nodes_from((n["id"], n) for n in node_records if isinstance(n.get("id"), str))
    for edge in edge_records:
        if isinstance(edge.get("source"), str) and isinstance(edge.get("target"), str) and edge["source"] in graph and edge["target"] in graph:
            graph.add_edge(edge["source"], edge["target"])
    if policy.require_acyclic is None:
        warnings.append(_issue("ACYCLICITY_POLICY_UNDEFINED", "Acyclicity policy is undefined; configure require_acyclic explicitly.", severity="WARNING"))
        checks.append({"check_id":"ACYCLICITY","status":"WARN","message":"Acyclicity policy is undefined."})
    elif policy.require_acyclic:
        acyclic = nx.is_directed_acyclic_graph(graph)
        check("ACYCLICITY", acyclic, "Graph is acyclic." if acyclic else "Graph contains a cycle.")
        if not acyclic:
            try: cycle = nx.find_cycle(graph)
            except nx.NetworkXNoCycle: cycle = []
            errors.append(_issue("CYCLE_DETECTED", "DAG policy is enabled but a cycle was found.", cycle=[{"source":u,"target":v} for u,v in cycle]))
    else:
        checks.append({"check_id":"ACYCLICITY","status":"SKIP","message":"Cycles are permitted by policy."})
    # structural checks are errors; baseline deviations are represented as failed checks
    for c in checks:
        if c["status"] == "FAIL": errors.append(_issue(c["check_id"], c["message"], severity="ERROR"))
    summary = {"node_count":len(ids),"edge_count":len(edge_records)}
    summary.update({f"{kind}_count":sum(1 for k in node_types.values() if k==kind) for kind in NODE_CATEGORIES.values()})
    summary.update({f"{rel}_count":edge_counts[rel] for rel in RELATIONSHIP_CATEGORIES})
    return {"valid": not errors, "graph_name": raw_data.get("metadata",{}).get("project","Team Photon Sprint 1"), "summary":summary, "checks":checks, "errors":errors, "warnings":warnings, "policy":policy.__dict__}

def validate_networkx_graph(graph: nx.Graph, policy: ValidationPolicy | None = None) -> dict:
    policy = policy or ValidationPolicy(check_baseline_counts=False)
    errors, checks, warnings = [], [], []
    if policy.directed and not graph.is_directed():
        errors.append(_issue("GRAPH_NOT_DIRECTED", "Graph must be directed."))
    allowed = {"supplier": {"part"}, "part":{"product"}, "product":{"order"}}
    for u,v,data in graph.edges(data=True):
        ku, kv = graph.nodes[u].get("kind"), graph.nodes[v].get("kind")
        if kv not in allowed.get(ku,set()):
            errors.append(_issue("INVALID_EDGE_DIRECTION", f"Invalid edge direction/type from {u} ({ku}) to {v} ({kv}).", edge={"source":u,"target":v}))
        if data.get("relation") not in {"SUPPLIES","USED_IN","FULFILLS"}:
            errors.append(_issue("INVALID_RELATIONSHIP_TYPE", f"Unsupported relationship on {u} → {v}.", edge={"source":u,"target":v}))
    if policy.require_acyclic is None:
        warnings.append(_issue("ACYCLICITY_POLICY_UNDEFINED","Acyclicity policy is undefined.",severity="WARNING"))
    elif policy.require_acyclic and graph.is_directed() and not nx.is_directed_acyclic_graph(graph):
        errors.append(_issue("CYCLE_DETECTED","DAG policy is enabled but a cycle was found."))
    return {"valid":not errors,"summary":{"node_count":graph.number_of_nodes(),"edge_count":graph.number_of_edges()},"checks":checks,"errors":errors,"warnings":warnings,"policy":policy.__dict__}
