from __future__ import annotations

import networkx as nx

from backend.app.validation.models import (
    AcyclicityPolicy,
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
)


def evaluate_acyclicity(
    graph: nx.DiGraph,
    policy: ValidationPolicy,
    checks: list[ValidationCheck],
    errors: list[ValidationError],
    warnings: list[ValidationError],
) -> None:
    """Evaluate acyclicity according to the configured policy."""
    if policy.acyclicity_policy == AcyclicityPolicy.REQUIRE_DAG:
        is_dag = nx.is_directed_acyclic_graph(graph)
        if is_dag:
            checks.append(
                ValidationCheck(
                    check_id="GRAPH_ACYCLICITY",
                    status=CheckStatus.PASS.value,
                    message="Graph is a verified Directed Acyclic Graph (DAG) with zero cycles.",
                )
            )
        else:
            cycle_desc = "Unknown cycle"
            try:
                cycle_edges = nx.find_cycle(graph, orientation="original")
                cycle_nodes = [u for u, v, _ in cycle_edges] + [cycle_edges[-1][1]]
                cycle_desc = " -> ".join(cycle_nodes)
            except (nx.NetworkXNoCycle, nx.NetworkXError):
                cycle_desc = "Cycle detected (path unresolvable)"

            errors.append(
                ValidationError(
                    code="ERR_CYCLE_DETECTED",
                    severity=Severity.CRITICAL.value,
                    message=f"Cycle detected in supply-chain dependency graph: {cycle_desc}.",
                    entity_type="graph",
                    actual=cycle_desc,
                    suggested_action=(
                        "Remove cyclic dependency to maintain a valid DAG flow "
                        "(Supplier -> Part -> Product -> Order)."
                    ),
                )
            )
            checks.append(
                ValidationCheck(
                    check_id="GRAPH_ACYCLICITY",
                    status=CheckStatus.FAIL.value,
                    message=f"Cycle detected in graph: {cycle_desc}",
                    details={"cycle": cycle_desc},
                )
            )

    elif policy.acyclicity_policy == AcyclicityPolicy.ALLOW_CYCLES:
        has_cycles = not nx.is_directed_acyclic_graph(graph)
        checks.append(
            ValidationCheck(
                check_id="GRAPH_ACYCLICITY",
                status=CheckStatus.SKIP.value,
                message=f"Acyclicity enforcement skipped by policy (allow_cycles=True, has_cycles={has_cycles}).",
            )
        )

    elif policy.acyclicity_policy == AcyclicityPolicy.UNSPECIFIED:
        warn = ValidationError(
            code="WARN_ACYCLICITY_POLICY_UNDEFINED",
            severity=Severity.WARNING.value,
            message="Acyclicity policy is unspecified; graph may contain cycles without validation gating.",
            entity_type="policy",
            suggested_action="Explicitly set policy.acyclicity_policy to REQUIRE_DAG or ALLOW_CYCLES.",
        )
        warnings.append(warn)
        checks.append(
            ValidationCheck(
                check_id="GRAPH_ACYCLICITY",
                status=CheckStatus.WARN.value,
                message="Acyclicity policy is undefined; explicit configuration or documented decision required.",
            )
        )

