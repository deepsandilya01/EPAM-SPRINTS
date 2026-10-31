from __future__ import annotations

from typing import Any

import networkx as nx

from backend.app.validation.schema import (
    AcyclicityPolicy,
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
    ValidationReport,
    _iso_now,
)


def validate_networkx_graph(
    graph: nx.DiGraph,
    policy: ValidationPolicy | None = None
) -> ValidationReport:
    """
    Validate an in-memory NetworkX DiGraph instance.

    Used for live graph validation, including structural integrity verification
    after legitimate node deletion.
    """
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

    # Check directedness
    if not isinstance(graph, (nx.DiGraph, nx.MultiDiGraph)) or not graph.is_directed():
        errors.append(ValidationError(
            code="ERR_GRAPH_NOT_DIRECTED",
            severity=Severity.CRITICAL.value,
            message="Graph is not a directed graph (DiGraph).",
            entity_type="graph",
            expected="nx.DiGraph",
            actual=type(graph).__name__,
        ))
        checks.append(ValidationCheck(
            check_id="GRAPH_DIRECTED",
            status=CheckStatus.FAIL.value,
            message="Graph instance is not directed.",
        ))
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

    checks.append(ValidationCheck(
        check_id="GRAPH_DIRECTED",
        status=CheckStatus.PASS.value,
        message="Graph is a valid directed graph."
    ))

    # Node categorization and attribute checks
    node_kinds: dict[str, str] = {}
    for nid, attrs in graph.nodes(data=True):
        kind = attrs.get("kind")
        if not kind:
            errors.append(ValidationError(
                code="ERR_MISSING_NODE_KIND",
                severity=Severity.ERROR.value,
                message=f"Node '{nid}' in live graph is missing 'kind' attribute.",
                entity_type="node",
                entity_id=nid,
            ))
            continue

        node_kinds[nid] = kind
        if kind == "supplier":
            summary["supplier_count"] += 1
        elif kind == "part":
            summary["part_count"] += 1
        elif kind == "product":
            summary["product_count"] += 1
        elif kind == "order":
            summary["order_count"] += 1

    # Edge relation and direction checks
    for u, v, attrs in graph.edges(data=True):
        relation = attrs.get("relation")
        u_kind = node_kinds.get(u)
        v_kind = node_kinds.get(v)

        if relation == "SUPPLIES":
            summary["supplies_count"] += 1
            if u_kind != "supplier" or v_kind != "part":
                errors.append(ValidationError(
                    code="ERR_INVALID_EDGE_DIRECTION",
                    severity=Severity.CRITICAL.value,
                    message=f"SUPPLIES edge '{u} -> {v}' connects '{u_kind}' to '{v_kind}', expected 'supplier -> part'.",
                    entity_type="edge",
                    entity_id=(u, v),
                ))
        elif relation == "USED_IN":
            summary["used_in_count"] += 1
            if u_kind != "part" or v_kind != "product":
                errors.append(ValidationError(
                    code="ERR_INVALID_EDGE_DIRECTION",
                    severity=Severity.CRITICAL.value,
                    message=f"USED_IN edge '{u} -> {v}' connects '{u_kind}' to '{v_kind}', expected 'part -> product'.",
                    entity_type="edge",
                    entity_id=(u, v),
                ))
        elif relation == "FULFILLS":
            summary["fulfills_count"] += 1
            if u_kind != "product" or v_kind != "order":
                errors.append(ValidationError(
                    code="ERR_INVALID_EDGE_DIRECTION",
                    severity=Severity.CRITICAL.value,
                    message=f"FULFILLS edge '{u} -> {v}' connects '{u_kind}' to '{v_kind}', expected 'product -> order'.",
                    entity_type="edge",
                    entity_id=(u, v),
                ))
        else:
            errors.append(ValidationError(
                code="ERR_UNKNOWN_RELATION",
                severity=Severity.ERROR.value,
                message=f"Edge '{u} -> {v}' has unrecognized relation: '{relation}'.",
                entity_type="edge",
                entity_id=(u, v),
                actual=relation,
            ))

    checks.append(ValidationCheck(
        check_id="EDGE_DIRECTIONS",
        status=CheckStatus.PASS.value if not any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in errors) else CheckStatus.FAIL.value,
        message="Edge directions verified against supply-chain dependency rules."
    ))

    # Baseline counts check (if enabled)
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
            errors.append(ValidationError(
                code="ERR_BASELINE_COUNT_MISMATCH",
                severity=Severity.ERROR.value,
                message="Live graph counts do not match original baseline counts.",
                entity_type="graph",
                expected=bc.to_dict(),
                actual=summary,
            ))
            checks.append(ValidationCheck(
                check_id="BASELINE_COUNTS",
                status=CheckStatus.FAIL.value,
                message="Live graph counts deviate from baseline counts.",
                details={"expected": bc.to_dict(), "actual": summary}
            ))
        else:
            checks.append(ValidationCheck(
                check_id="BASELINE_COUNTS",
                status=CheckStatus.PASS.value,
                message="Live graph matches original baseline counts exactly."
            ))
    else:
        checks.append(ValidationCheck(
            check_id="STRUCTURAL_INTEGRITY",
            status=CheckStatus.PASS.value if not errors else CheckStatus.FAIL.value,
            message="Internal structural integrity verified (edges reference valid nodes; direction rules obeyed)."
        ))

    # Acyclicity verification
    _evaluate_acyclicity(graph, policy, checks, errors, warnings)

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


def _evaluate_acyclicity(
    G: nx.DiGraph,
    policy: ValidationPolicy,
    checks: list[ValidationCheck],
    errors: list[ValidationError],
    warnings: list[ValidationError]
) -> None:
    """Evaluate acyclicity according to the configured policy."""
    if policy.acyclicity_policy == AcyclicityPolicy.REQUIRE_DAG:
        is_dag = nx.is_directed_acyclic_graph(G)
        if is_dag:
            checks.append(ValidationCheck(
                check_id="GRAPH_ACYCLICITY",
                status=CheckStatus.PASS.value,
                message="Graph is a verified Directed Acyclic Graph (DAG) with zero cycles."
            ))
        else:
            # Find an illustrative cycle path
            cycle_desc = "Unknown cycle"
            try:
                cycle_edges = nx.find_cycle(G, orientation="original")
                cycle_nodes = [u for u, v, _ in cycle_edges] + [cycle_edges[-1][1]]
                cycle_desc = " -> ".join(cycle_nodes)
            except (nx.NetworkXNoCycle, nx.NetworkXError):
                cycle_desc = "Cycle detected (path unresolvable)"

            errors.append(ValidationError(
                code="ERR_CYCLE_DETECTED",
                severity=Severity.CRITICAL.value,
                message=f"Cycle detected in supply-chain dependency graph: {cycle_desc}.",
                entity_type="graph",
                actual=cycle_desc,
                suggested_action="Remove cyclic dependency to maintain a valid DAG flow (Supplier -> Part -> Product -> Order)."
            ))
            checks.append(ValidationCheck(
                check_id="GRAPH_ACYCLICITY",
                status=CheckStatus.FAIL.value,
                message=f"Cycle detected in graph: {cycle_desc}",
                details={"cycle": cycle_desc}
            ))

    elif policy.acyclicity_policy == AcyclicityPolicy.ALLOW_CYCLES:
        has_cycles = not nx.is_directed_acyclic_graph(G)
        checks.append(ValidationCheck(
            check_id="GRAPH_ACYCLICITY",
            status=CheckStatus.SKIP.value,
            message=f"Acyclicity enforcement skipped by policy (allow_cycles=True, has_cycles={has_cycles})."
        ))

    elif policy.acyclicity_policy == AcyclicityPolicy.UNSPECIFIED:
        warn = ValidationError(
            code="WARN_ACYCLICITY_POLICY_UNDEFINED",
            severity=Severity.WARNING.value,
            message="Acyclicity policy is unspecified; graph may contain cycles without validation gating.",
            entity_type="policy",
            suggested_action="Explicitly set policy.acyclicity_policy to REQUIRE_DAG or ALLOW_CYCLES."
        )
        warnings.append(warn)
        checks.append(ValidationCheck(
            check_id="GRAPH_ACYCLICITY",
            status=CheckStatus.WARN.value,
            message="Acyclicity policy is undefined; explicit configuration or documented decision required."
        ))


def validate_graph(
    data_or_graph: dict[str, Any] | nx.DiGraph,
    policy: ValidationPolicy | None = None
) -> ValidationReport:
    """
    Public unified validation entry point.

    Routes to `validate_raw_graph_data` if a dict is passed, or
    `validate_networkx_graph` if an `nx.DiGraph` is passed.
    """
    if isinstance(data_or_graph, (nx.DiGraph, nx.MultiDiGraph, nx.Graph)):
        return validate_networkx_graph(data_or_graph, policy=policy)
    elif isinstance(data_or_graph, dict):
        from backend.app.validation.schema_validator import validate_raw_graph_data

        return validate_raw_graph_data(data_or_graph, policy=policy)
    else:
        raise TypeError(f"Unsupported data type for validation: {type(data_or_graph).__name__}. Expected dict or nx.DiGraph.")


def validate_graph_topology(
    graph: nx.DiGraph,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """Alias for validate_networkx_graph."""
    return validate_networkx_graph(graph, policy=policy)
