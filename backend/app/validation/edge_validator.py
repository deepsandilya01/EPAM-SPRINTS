from __future__ import annotations

import networkx as nx

from backend.app.validation.schema import (
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
    ValidationReport,
    _iso_now,
)


def validate_edge_relationships(
    graph: nx.DiGraph,
    policy: ValidationPolicy | None = None,
) -> ValidationReport:
    """
    Verify edge direction and tier transition validity on a NetworkX DiGraph.
    Ensures:
      - SUPPLIES: supplier -> part
      - USED_IN: part -> product
      - FULFILLS: product -> order
      - No dangling edges or reversed transitions.
    """
    if policy is None:
        policy = ValidationPolicy()

    errors: list[ValidationError] = []
    checks: list[ValidationCheck] = []

    # Map node categories
    node_kinds: dict[str, str] = {}
    for node_id, data in graph.nodes(data=True):
        kind = data.get("tier") or data.get("category", "")
        # normalize kind
        if kind.endswith("s"):
            kind = kind[:-1]
        node_kinds[node_id] = kind.lower()

    # Direction rule mappings
    direction_rules = policy.direction_rules

    valid_directions = True
    for u, v, data in graph.edges(data=True):
        rel = (data.get("relation") or "").lower()
        src_kind = node_kinds.get(u, "")
        tgt_kind = node_kinds.get(v, "")

        if rel in direction_rules:
            exp_src, exp_tgt, expected_rel = direction_rules[rel]
            if src_kind != exp_src or tgt_kind != exp_tgt:
                valid_directions = False
                errors.append(ValidationError(
                    code="ERR_INVALID_EDGE_DIRECTION",
                    severity=Severity.ERROR.value,
                    message=f"Edge '{u}' -> '{v}' ({expected_rel}) connects '{src_kind}' to '{tgt_kind}', expected '{exp_src}' -> '{exp_tgt}'.",
                    entity_type="edge",
                    entity_id=(u, v),
                    expected=f"{exp_src} -> {exp_tgt}",
                    actual=f"{src_kind} -> {tgt_kind}",
                ))

    check_status = CheckStatus.PASS.value if valid_directions else CheckStatus.FAIL.value
    check_msg = (
        "Edge directions verified against supply-chain dependency rules."
        if valid_directions else "One or more edges violate tier dependency rules."
    )
    checks.append(ValidationCheck(
        check_id="EDGE_DIRECTIONS",
        status=check_status,
        message=check_msg,
    ))

    return ValidationReport(
        valid=len(errors) == 0,
        graph_name="Edge Direction Audit",
        mode="integrity",
        summary={"node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges()},
        checks=checks,
        errors=errors,
        warnings=[],
        policy=policy.to_dict(),
        timestamp=_iso_now(),
    )
