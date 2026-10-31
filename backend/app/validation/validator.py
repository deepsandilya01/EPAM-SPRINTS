from __future__ import annotations

from typing import Any

import networkx as nx

from backend.app.validation.cycles import evaluate_acyclicity
from backend.app.validation.edges import (
    validate_edge_records,
    validate_edge_relationships,
)
from backend.app.validation.models import (
    AcyclicityPolicy,
    BaselineCounts,
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
    ValidationReport,
    _iso_now,
)
from backend.app.validation.nodes import validate_node_records

# Re-export core validation models for callers importing from validator.py
__all__ = [
    "AcyclicityPolicy",
    "BaselineCounts",
    "CheckStatus",
    "Severity",
    "ValidationCheck",
    "ValidationError",
    "ValidationPolicy",
    "ValidationReport",
    "validate_dataset_schema",
    "validate_edge_relationships",
    "validate_graph",
    "validate_graph_topology",
    "validate_networkx_graph",
    "validate_raw_graph_data",
]


def validate_networkx_graph(
    graph: nx.DiGraph,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """Validate an in-memory NetworkX DiGraph instance against structural rules."""
    if policy is None:
        policy = ValidationPolicy()

    checks: list[ValidationCheck] = []
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    summary: dict[str, Any] = {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "supplier_count": 0,
        "part_count": 0,
        "product_count": 0,
        "order_count": 0,
        "supplies_count": 0,
        "used_in_count": 0,
        "fulfills_count": 0,
    }

    if not isinstance(graph, (nx.DiGraph, nx.MultiDiGraph)) or not graph.is_directed():
        errors.append(
            ValidationError(
                code="ERR_GRAPH_NOT_DIRECTED",
                severity=Severity.CRITICAL.value,
                message="Graph is not a directed graph (DiGraph).",
                entity_type="graph",
                expected="nx.DiGraph",
                actual=type(graph).__name__,
            )
        )
        checks.append(
            ValidationCheck(
                check_id="GRAPH_DIRECTED",
                status=CheckStatus.FAIL.value,
                message="Graph instance is not directed.",
            )
        )
        return ValidationReport(
            valid=False,
            graph_name="Live NetworkX Graph",
            mode="baseline" if policy.check_baseline_counts else "integrity",
            summary=summary,
            checks=checks,
            errors=errors,
            warnings=warnings,
            policy=policy.to_dict(),
            timestamp=_iso_now(),
        )

    checks.append(
        ValidationCheck(
            check_id="GRAPH_DIRECTED",
            status=CheckStatus.PASS.value,
            message="Graph is a valid directed graph.",
        )
    )

    node_kinds: dict[str, str] = {}
    for node_id, data in graph.nodes(data=True):
        kind = data.get("kind") or data.get("tier") or data.get("category", "")
        if kind.endswith("s"):
            kind = kind[:-1]
        kind = kind.lower()
        node_kinds[node_id] = kind

        if kind == "supplier":
            summary["supplier_count"] += 1
        elif kind == "part":
            summary["part_count"] += 1
        elif kind == "product":
            summary["product_count"] += 1
        elif kind == "order":
            summary["order_count"] += 1

    for u, v, attrs in graph.edges(data=True):
        relation = attrs.get("relation")
        u_kind = node_kinds.get(u)
        v_kind = node_kinds.get(v)

        if relation == "SUPPLIES":
            summary["supplies_count"] += 1
            if u_kind != "supplier" or v_kind != "part":
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_EDGE_DIRECTION",
                        severity=Severity.CRITICAL.value,
                        message=(
                            f"SUPPLIES edge '{u} -> {v}' connects '{u_kind}' to '{v_kind}', "
                            "expected 'supplier -> part'."
                        ),
                        entity_type="edge",
                        entity_id=(u, v),
                    )
                )
        elif relation == "USED_IN":
            summary["used_in_count"] += 1
            if u_kind != "part" or v_kind != "product":
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_EDGE_DIRECTION",
                        severity=Severity.CRITICAL.value,
                        message=(
                            f"USED_IN edge '{u} -> {v}' connects '{u_kind}' to '{v_kind}', "
                            "expected 'part -> product'."
                        ),
                        entity_type="edge",
                        entity_id=(u, v),
                    )
                )
        elif relation == "FULFILLS":
            summary["fulfills_count"] += 1
            if u_kind != "product" or v_kind != "order":
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_EDGE_DIRECTION",
                        severity=Severity.CRITICAL.value,
                        message=(
                            f"FULFILLS edge '{u} -> {v}' connects '{u_kind}' to '{v_kind}', "
                            "expected 'product -> order'."
                        ),
                        entity_type="edge",
                        entity_id=(u, v),
                    )
                )
        else:
            errors.append(
                ValidationError(
                    code="ERR_UNKNOWN_RELATION",
                    severity=Severity.ERROR.value,
                    message=f"Edge '{u} -> {v}' has unrecognized relation: '{relation}'.",
                    entity_type="edge",
                    entity_id=(u, v),
                    actual=relation,
                )
            )

    checks.append(
        ValidationCheck(
            check_id="EDGE_DIRECTIONS",
            status=(
                CheckStatus.PASS.value
                if not any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in errors)
                else CheckStatus.FAIL.value
            ),
            message="Edge directions verified against supply-chain dependency rules.",
        )
    )

    if policy.check_baseline_counts:
        bc = policy.baseline_counts
        counts_ok = (
            summary["node_count"] == bc.total_nodes
            and summary["edge_count"] == bc.total_edges
            and summary["supplier_count"] == bc.suppliers
            and summary["part_count"] == bc.parts
            and summary["product_count"] == bc.products
            and summary["order_count"] == bc.orders
            and summary["supplies_count"] == bc.supplies
            and summary["used_in_count"] == bc.used_in
            and summary["fulfills_count"] == bc.fulfills
        )
        if not counts_ok:
            errors.append(
                ValidationError(
                    code="ERR_BASELINE_COUNT_MISMATCH",
                    severity=Severity.ERROR.value,
                    message="Live graph counts do not match original baseline counts.",
                    entity_type="graph",
                    expected=bc.to_dict(),
                    actual=summary,
                )
            )
            checks.append(
                ValidationCheck(
                    check_id="BASELINE_COUNTS",
                    status=CheckStatus.FAIL.value,
                    message="Live graph counts deviate from baseline counts.",
                    details={"expected": bc.to_dict(), "actual": summary},
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="BASELINE_COUNTS",
                    status=CheckStatus.PASS.value,
                    message="Live graph matches original baseline counts exactly.",
                )
            )
    else:
        checks.append(
            ValidationCheck(
                check_id="STRUCTURAL_INTEGRITY",
                status=CheckStatus.PASS.value if not errors else CheckStatus.FAIL.value,
                message="Internal structural integrity verified (edges reference valid nodes; direction rules obeyed).",
            )
        )

    evaluate_acyclicity(graph, policy, checks, errors, warnings)

    return ValidationReport(
        valid=len(errors) == 0,
        graph_name="Live NetworkX Graph",
        mode="baseline" if policy.check_baseline_counts else "integrity",
        summary=summary,
        checks=checks,
        errors=errors,
        warnings=warnings,
        policy=policy.to_dict(),
        timestamp=_iso_now(),
    )


def validate_graph_topology(
    graph: nx.DiGraph,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """Alias for validate_networkx_graph."""
    return validate_networkx_graph(graph, policy=policy)


def validate_raw_graph_data(
    raw_data: Any,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """Validate raw JSON-like dictionary data before constructing a NetworkX graph."""
    if policy is None:
        policy = ValidationPolicy()

    checks: list[ValidationCheck] = []
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    summary: dict[str, Any] = {
        "node_count": 0,
        "edge_count": 0,
        "supplier_count": 0,
        "part_count": 0,
        "product_count": 0,
        "order_count": 0,
        "supplies_count": 0,
        "used_in_count": 0,
        "fulfills_count": 0,
    }

    if not isinstance(raw_data, dict):
        err = ValidationError(
            code="ERR_INVALID_TOP_LEVEL_TYPE",
            severity=Severity.CRITICAL.value,
            message=f"Top-level data must be a JSON object (dict), got {type(raw_data).__name__}.",
            entity_type="structure",
            expected="dict",
            actual=type(raw_data).__name__,
            suggested_action="Ensure the root of the graph data JSON is an object with 'nodes' and 'edges'.",
        )
        errors.append(err)
        checks.append(
            ValidationCheck(
                check_id="SCHEMA_TOP_LEVEL",
                status=CheckStatus.FAIL.value,
                message="Top-level structure is not a dictionary.",
                details={"type": type(raw_data).__name__},
            )
        )
        return ValidationReport(
            valid=False,
            graph_name="Team Photon Sprint 1",
            mode="baseline" if policy.check_baseline_counts else "integrity",
            summary=summary,
            checks=checks,
            errors=errors,
            warnings=warnings,
            policy=policy.to_dict(),
            timestamp=_iso_now(),
        )

    if "nodes" not in raw_data or not isinstance(raw_data.get("nodes"), dict):
        errors.append(
            ValidationError(
                code="ERR_MISSING_NODES_KEY",
                severity=Severity.CRITICAL.value,
                message="Top-level key 'nodes' is missing or not a dictionary.",
                entity_type="structure",
                expected="dict",
                actual=type(raw_data.get("nodes")).__name__,
                suggested_action="Add a 'nodes' object containing node category lists.",
            )
        )
    if "edges" not in raw_data or not isinstance(raw_data.get("edges"), dict):
        errors.append(
            ValidationError(
                code="ERR_MISSING_EDGES_KEY",
                severity=Severity.CRITICAL.value,
                message="Top-level key 'edges' is missing or not a dictionary.",
                entity_type="structure",
                expected="dict",
                actual=type(raw_data.get("edges")).__name__,
                suggested_action="Add an 'edges' object containing relationship category lists.",
            )
        )

    if errors:
        checks.append(
            ValidationCheck(
                check_id="SCHEMA_TOP_LEVEL",
                status=CheckStatus.FAIL.value,
                message="Top-level schema is missing required 'nodes' or 'edges' dictionary.",
            )
        )
        return ValidationReport(
            valid=False,
            graph_name="Team Photon Sprint 1",
            mode="baseline" if policy.check_baseline_counts else "integrity",
            summary=summary,
            checks=checks,
            errors=errors,
            warnings=warnings,
            policy=policy.to_dict(),
            timestamp=_iso_now(),
        )

    checks.append(
        ValidationCheck(
            check_id="SCHEMA_TOP_LEVEL",
            status=CheckStatus.PASS.value,
            message="Top-level data structure is valid with 'nodes' and 'edges'.",
        )
    )

    raw_nodes = raw_data["nodes"]
    raw_edges = raw_data["edges"]

    (
        seen_node_ids,
        node_records_by_id,
        node_kind_by_id,
        node_category_counts,
        duplicate_ids,
    ) = validate_node_records(raw_nodes, policy, checks, errors, warnings)

    summary["node_count"] = len(seen_node_ids)
    summary["supplier_count"] = node_category_counts.get("suppliers", 0)
    summary["part_count"] = node_category_counts.get("parts", 0)
    summary["product_count"] = node_category_counts.get("products", 0)
    summary["order_count"] = node_category_counts.get("orders", 0)

    edge_type_counts, _, _ = validate_edge_records(
        raw_edges, seen_node_ids, node_kind_by_id, policy, checks, errors
    )

    summary["edge_count"] = sum(edge_type_counts.values())
    summary["supplies_count"] = edge_type_counts.get("supplies", 0)
    summary["used_in_count"] = edge_type_counts.get("used_in", 0)
    summary["fulfills_count"] = edge_type_counts.get("fulfills", 0)

    if policy.check_baseline_counts:
        bc = policy.baseline_counts
        node_counts_match = (
            summary["node_count"] == bc.total_nodes
            and summary["supplier_count"] == bc.suppliers
            and summary["part_count"] == bc.parts
            and summary["product_count"] == bc.products
            and summary["order_count"] == bc.orders
        )
        edge_counts_match = (
            summary["edge_count"] == bc.total_edges
            and summary["supplies_count"] == bc.supplies
            and summary["used_in_count"] == bc.used_in
            and summary["fulfills_count"] == bc.fulfills
        )

        if not node_counts_match:
            errors.append(
                ValidationError(
                    code="ERR_BASELINE_NODE_COUNT_MISMATCH",
                    severity=Severity.ERROR.value,
                    message=(
                        f"Baseline node count mismatch. Expected total={bc.total_nodes} "
                        f"(sup={bc.suppliers}, part={bc.parts}, prod={bc.products}, ord={bc.orders}), "
                        f"got total={summary['node_count']} (sup={summary['supplier_count']}, "
                        f"part={summary['part_count']}, prod={summary['product_count']}, ord={summary['order_count']})."
                    ),
                    entity_type="graph",
                    expected=bc.to_dict(),
                    actual=summary,
                    suggested_action="Verify if the input data represents the canonical 19-node Sprint 1 baseline graph.",
                )
            )
            checks.append(
                ValidationCheck(
                    check_id="BASELINE_NODE_COUNTS",
                    status=CheckStatus.FAIL.value,
                    message="Node counts do not match baseline expected counts.",
                    details={"expected": bc.to_dict(), "actual": summary},
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="BASELINE_NODE_COUNTS",
                    status=CheckStatus.PASS.value,
                    message="Expected baseline node counts match exactly (19 nodes: 2 sup, 5 part, 2 prod, 10 ord).",
                )
            )

        if not edge_counts_match:
            errors.append(
                ValidationError(
                    code="ERR_BASELINE_EDGE_COUNT_MISMATCH",
                    severity=Severity.ERROR.value,
                    message=(
                        f"Baseline edge count mismatch. Expected total={bc.total_edges} "
                        f"(supplies={bc.supplies}, used_in={bc.used_in}, fulfills={bc.fulfills}), "
                        f"got total={summary['edge_count']} (supplies={summary['supplies_count']}, "
                        f"used_in={summary['used_in_count']}, fulfills={summary['fulfills_count']})."
                    ),
                    entity_type="graph",
                    expected=bc.to_dict(),
                    actual=summary,
                    suggested_action="Verify if the input data represents the canonical 21-edge Sprint 1 baseline graph.",
                )
            )
            checks.append(
                ValidationCheck(
                    check_id="BASELINE_EDGE_COUNTS",
                    status=CheckStatus.FAIL.value,
                    message="Edge counts do not match baseline expected counts.",
                    details={"expected": bc.to_dict(), "actual": summary},
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    check_id="BASELINE_EDGE_COUNTS",
                    status=CheckStatus.PASS.value,
                    message="Expected baseline edge counts match exactly (21 edges: 6 supplies, 5 used_in, 10 fulfills).",
                )
            )
    else:
        checks.append(
            ValidationCheck(
                check_id="BASELINE_COUNTS",
                status=CheckStatus.SKIP.value,
                message="Baseline count verification skipped (integrity mode active).",
            )
        )

    if not duplicate_ids and not any(
        e.code in ("ERR_NONEXISTENT_SOURCE_NODE", "ERR_NONEXISTENT_TARGET_NODE")
        for e in errors
    ):
        g = nx.DiGraph()
        for nid, nattrs in node_records_by_id.items():
            g.add_node(nid, **nattrs)
        for edge_type in policy.allowed_edge_types:
            for edge in raw_edges.get(edge_type, []):
                if isinstance(edge, dict) and "source" in edge and "target" in edge:
                    edge_attrs = {
                        k: v for k, v in edge.items() if k not in ("source", "target")
                    }
                    g.add_edge(edge["source"], edge["target"], **edge_attrs)

        checks.append(
            ValidationCheck(
                check_id="GRAPH_DIRECTED",
                status=CheckStatus.PASS.value,
                message="Graph is a valid directed graph (DiGraph).",
            )
        )

        evaluate_acyclicity(g, policy, checks, errors, warnings)
    else:
        checks.append(
            ValidationCheck(
                check_id="GRAPH_DIRECTED",
                status=CheckStatus.SKIP.value,
                message="DiGraph construction skipped due to fatal duplicate ID or nonexistent endpoint errors.",
            )
        )
        checks.append(
            ValidationCheck(
                check_id="GRAPH_ACYCLICITY",
                status=CheckStatus.SKIP.value,
                message="Acyclicity check skipped due to invalid node/edge entities.",
            )
        )

    is_valid = len(errors) == 0

    return ValidationReport(
        valid=is_valid,
        graph_name=raw_data.get("metadata", {}).get("project", "Team Photon Sprint 1"),
        mode="baseline" if policy.check_baseline_counts else "integrity",
        summary=summary,
        checks=checks,
        errors=errors,
        warnings=warnings,
        policy=policy.to_dict(),
        timestamp=_iso_now(),
    )


def validate_dataset_schema(
    raw_data: Any,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """Alias for validate_raw_graph_data."""
    return validate_raw_graph_data(raw_data, policy=policy)


def validate_graph(
    raw_data_or_graph: Any,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """Unified entry point validating either a raw scenario dictionary or a NetworkX DiGraph."""
    if isinstance(raw_data_or_graph, (nx.DiGraph, nx.MultiDiGraph)):
        return validate_networkx_graph(raw_data_or_graph, policy=policy)
    return validate_raw_graph_data(raw_data_or_graph, policy=policy)
