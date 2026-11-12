from __future__ import annotations

from typing import Any

import networkx as nx

from backend.app.validation.models import (
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
    ValidationReport,
    _iso_now,
)


def validate_edge_records(
    raw_edges: dict[str, Any],
    seen_node_ids: set[str],
    node_kind_by_id: dict[str, str],
    policy: ValidationPolicy,
    checks: list[ValidationCheck],
    errors: list[ValidationError],
) -> tuple[dict[str, int], int, list[dict[str, Any]]]:
    """
    Validate edge categories, endpoint references, and direction rules from raw JSON input.

    Returns:
        (edge_type_counts, total_valid_edges, invalid_edges)
    """
    edge_type_counts: dict[str, int] = {et: 0 for et in policy.allowed_edge_types}
    total_valid_edges = 0
    invalid_edges: list[dict[str, Any]] = []

    for edge_type in policy.allowed_edge_types:
        edge_list = raw_edges.get(edge_type, [])
        if not isinstance(edge_list, list):
            errors.append(
                ValidationError(
                    code="ERR_INVALID_EDGE_CATEGORY_TYPE",
                    severity=Severity.ERROR.value,
                    message=f"Edge category '{edge_type}' must be a list, got {type(edge_list).__name__}.",
                    entity_type="edge",
                    expected="list",
                    actual=type(edge_list).__name__,
                )
            )
            continue

        rule = policy.direction_rules.get(edge_type)
        expected_src_kind = rule[0] if rule else None
        expected_tgt_kind = rule[1] if rule else None
        expected_rel_str = rule[2] if rule else None

        for idx, edge in enumerate(edge_list):
            edge_type_counts[edge_type] += 1
            if not isinstance(edge, dict):
                errors.append(
                    ValidationError(
                        code="ERR_MALFORMED_EDGE_RECORD",
                        severity=Severity.ERROR.value,
                        message=f"Edge at index {idx} in '{edge_type}' is not a dict.",
                        entity_type="edge",
                        expected="dict",
                        actual=type(edge).__name__,
                    )
                )
                continue

            src = edge.get("source")
            tgt = edge.get("target")

            if not src or not isinstance(src, str):
                errors.append(
                    ValidationError(
                        code="ERR_MISSING_EDGE_SOURCE",
                        severity=Severity.CRITICAL.value,
                        message=f"Edge in '{edge_type}' missing valid 'source'.",
                        entity_type="edge",
                        actual=src,
                        suggested_action="Specify a valid node identifier for 'source'.",
                    )
                )
                invalid_edges.append(edge)
                continue

            if not tgt or not isinstance(tgt, str):
                errors.append(
                    ValidationError(
                        code="ERR_MISSING_EDGE_TARGET",
                        severity=Severity.CRITICAL.value,
                        message=f"Edge in '{edge_type}' from '{src}' missing valid 'target'.",
                        entity_type="edge",
                        actual=tgt,
                        suggested_action="Specify a valid node identifier for 'target'.",
                    )
                )
                invalid_edges.append(edge)
                continue

            src_exists = src in seen_node_ids
            tgt_exists = tgt in seen_node_ids

            if not src_exists:
                errors.append(
                    ValidationError(
                        code="ERR_NONEXISTENT_SOURCE_NODE",
                        severity=Severity.CRITICAL.value,
                        message=f"Edge references nonexistent source node '{src}'.",
                        entity_type="edge",
                        entity_id=(src, tgt),
                        expected=f"Existing node in {list(seen_node_ids)[:5]}...",
                        actual=src,
                        suggested_action=f"Define node '{src}' in raw_nodes before referencing it.",
                    )
                )
            if not tgt_exists:
                errors.append(
                    ValidationError(
                        code="ERR_NONEXISTENT_TARGET_NODE",
                        severity=Severity.CRITICAL.value,
                        message=f"Edge references nonexistent target node '{tgt}'.",
                        entity_type="edge",
                        entity_id=(src, tgt),
                        expected=f"Existing node in {list(seen_node_ids)[:5]}...",
                        actual=tgt,
                        suggested_action=f"Define node '{tgt}' in raw_nodes before referencing it.",
                    )
                )

            if not src_exists or not tgt_exists:
                invalid_edges.append(edge)
                continue

            rel = edge.get("relation")
            if expected_rel_str and rel != expected_rel_str:
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_RELATION_NAME",
                        severity=Severity.ERROR.value,
                        message=(
                            f"Edge '{src} -> {tgt}' in category '{edge_type}' has relation '{rel}', "
                            f"expected '{expected_rel_str}'."
                        ),
                        entity_type="edge",
                        entity_id=(src, tgt),
                        expected=expected_rel_str,
                        actual=rel,
                        suggested_action=f"Set 'relation': '{expected_rel_str}' on this edge.",
                    )
                )

            src_kind = node_kind_by_id.get(src)
            tgt_kind = node_kind_by_id.get(tgt)

            if expected_src_kind and src_kind != expected_src_kind:
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_EDGE_DIRECTION",
                        severity=Severity.CRITICAL.value,
                        message=(
                            f"Invalid edge direction for '{edge_type}': source '{src}' has kind '{src_kind}', "
                            f"expected '{expected_src_kind}'."
                        ),
                        entity_type="edge",
                        entity_id=(src, tgt),
                        expected=f"{expected_src_kind} -> {expected_tgt_kind}",
                        actual=f"{src_kind} -> {tgt_kind}",
                        suggested_action=f"Ensure '{edge_type}' edges originate from a '{expected_src_kind}'.",
                    )
                )
                invalid_edges.append(edge)
                continue

            if expected_tgt_kind and tgt_kind != expected_tgt_kind:
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_EDGE_DIRECTION",
                        severity=Severity.CRITICAL.value,
                        message=(
                            f"Invalid edge direction for '{edge_type}': target '{tgt}' has kind '{tgt_kind}', "
                            f"expected '{expected_tgt_kind}'."
                        ),
                        entity_type="edge",
                        entity_id=(src, tgt),
                        expected=f"{expected_src_kind} -> {expected_tgt_kind}",
                        actual=f"{src_kind} -> {tgt_kind}",
                        suggested_action=f"Ensure '{edge_type}' edges terminate at a '{expected_tgt_kind}'.",
                    )
                )
                invalid_edges.append(edge)
                continue

            total_valid_edges += 1

    has_ref_errors = any(
        e.code
        in (
            "ERR_NONEXISTENT_SOURCE_NODE",
            "ERR_NONEXISTENT_TARGET_NODE",
            "ERR_MISSING_EDGE_SOURCE",
            "ERR_MISSING_EDGE_TARGET",
        )
        for e in errors
    )
    if has_ref_errors:
        checks.append(
            ValidationCheck(
                check_id="EDGE_REFERENCES",
                status=CheckStatus.FAIL.value,
                message="One or more edges reference nonexistent or invalid node endpoints.",
            )
        )
    else:
        checks.append(
            ValidationCheck(
                check_id="EDGE_REFERENCES",
                status=CheckStatus.PASS.value,
                message="All edges connect valid existing nodes.",
            )
        )

    has_dir_errors = any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in errors)
    if has_dir_errors:
        checks.append(
            ValidationCheck(
                check_id="EDGE_DIRECTIONS",
                status=CheckStatus.FAIL.value,
                message="One or more edges violate the agreed supply-chain dependency direction.",
            )
        )
    else:
        checks.append(
            ValidationCheck(
                check_id="EDGE_DIRECTIONS",
                status=CheckStatus.PASS.value,
                message="All edges follow the agreed supply-chain direction (Supplier -> Part -> Product -> Order).",
            )
        )

    return edge_type_counts, total_valid_edges, invalid_edges


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

    node_kinds: dict[str, str] = {}
    for node_id, data in graph.nodes(data=True):
        kind = data.get("tier") or data.get("category", "")
        if kind.endswith("s"):
            kind = kind[:-1]
        node_kinds[node_id] = kind.lower()

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
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_EDGE_DIRECTION",
                        severity=Severity.ERROR.value,
                        message=(
                            f"Edge '{u}' -> '{v}' ({expected_rel}) connects '{src_kind}' "
                            f"to '{tgt_kind}', expected '{exp_src}' -> '{exp_tgt}'."
                        ),
                        entity_type="edge",
                        entity_id=(u, v),
                        expected=f"{exp_src} -> {exp_tgt}",
                        actual=f"{src_kind} -> {tgt_kind}",
                    )
                )

    check_status = CheckStatus.PASS.value if valid_directions else CheckStatus.FAIL.value
    check_msg = (
        "Edge directions verified against supply-chain dependency rules."
        if valid_directions
        else "One or more edges violate tier dependency rules."
    )
    checks.append(
        ValidationCheck(
            check_id="EDGE_DIRECTIONS",
            status=check_status,
            message=check_msg,
        )
    )

    return ValidationReport(
        valid=len(errors) == 0,
        graph_name="Edge Direction Audit",
        mode="integrity",
        summary={
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
        },
        checks=checks,
        errors=errors,
        warnings=[],
        policy=policy.to_dict(),
        timestamp=_iso_now(),
    )

