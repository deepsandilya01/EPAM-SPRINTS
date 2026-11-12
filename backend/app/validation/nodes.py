from __future__ import annotations

from typing import Any

from backend.app.validation.models import (
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
)


def validate_node_records(
    raw_nodes: dict[str, Any],
    policy: ValidationPolicy,
    checks: list[ValidationCheck],
    errors: list[ValidationError],
    warnings: list[ValidationError],
) -> tuple[set[str], dict[str, dict[str, Any]], dict[str, str], dict[str, int], list[str]]:
    """
    Validate node categories and records from raw JSON input.

    Returns:
        (seen_node_ids, node_records_by_id, node_kind_by_id, node_category_counts, duplicate_ids)
    """
    seen_node_ids: set[str] = set()
    node_records_by_id: dict[str, dict[str, Any]] = {}
    node_kind_by_id: dict[str, str] = {}
    node_category_counts: dict[str, int] = {cat: 0 for cat in policy.allowed_node_categories}
    duplicate_ids: list[str] = []

    for cat in policy.allowed_node_categories:
        cat_list = raw_nodes.get(cat, [])
        if not isinstance(cat_list, list):
            errors.append(
                ValidationError(
                    code="ERR_INVALID_CATEGORY_TYPE",
                    severity=Severity.ERROR.value,
                    message=f"Node category '{cat}' must be a list, got {type(cat_list).__name__}.",
                    entity_type="node",
                    expected="list",
                    actual=type(cat_list).__name__,
                    suggested_action=f"Define raw_nodes['{cat}'] as a list of node records.",
                )
            )
            continue

        singular_kind = cat.removesuffix("s")

        for idx, node in enumerate(cat_list):
            node_category_counts[cat] += 1
            if not isinstance(node, dict):
                errors.append(
                    ValidationError(
                        code="ERR_MALFORMED_NODE_RECORD",
                        severity=Severity.ERROR.value,
                        message=f"Node at index {idx} in category '{cat}' is not a dict.",
                        entity_type="node",
                        expected="dict",
                        actual=type(node).__name__,
                        suggested_action="Ensure every node record is a JSON object.",
                    )
                )
                continue

            nid = node.get("id")
            if nid is None:
                errors.append(
                    ValidationError(
                        code="ERR_MISSING_NODE_ID",
                        severity=Severity.CRITICAL.value,
                        message=f"Node at index {idx} in category '{cat}' is missing required 'id'.",
                        entity_type="node",
                        expected="non-empty string",
                        actual=None,
                        suggested_action="Assign a unique string identifier (e.g., 'SUP-01', 'PART-01') to 'id'.",
                    )
                )
                continue
            elif not isinstance(nid, str) or not nid.strip():
                errors.append(
                    ValidationError(
                        code="ERR_EMPTY_NODE_ID",
                        severity=Severity.CRITICAL.value,
                        message=f"Node at index {idx} in category '{cat}' has empty or non-string id: {nid!r}.",
                        entity_type="node",
                        expected="non-empty string",
                        actual=repr(nid),
                        suggested_action="Provide a valid, non-blank string for the node identifier.",
                    )
                )
                continue

            if nid in seen_node_ids:
                duplicate_ids.append(nid)
                errors.append(
                    ValidationError(
                        code="ERR_DUPLICATE_NODE_ID",
                        severity=Severity.CRITICAL.value,
                        message=f"Duplicate node identifier '{nid}' detected in raw node records.",
                        entity_type="node",
                        entity_id=nid,
                        expected="unique node identifier",
                        actual=f"Duplicate id '{nid}' in category '{cat}'",
                        suggested_action="Ensure all entity IDs are globally unique across all categories.",
                    )
                )
            else:
                seen_node_ids.add(nid)
                node_records_by_id[nid] = node

            kind = node.get("kind")
            if kind != singular_kind:
                errors.append(
                    ValidationError(
                        code="ERR_INVALID_NODE_KIND",
                        severity=Severity.ERROR.value,
                        message=f"Node '{nid}' has kind '{kind}', expected '{singular_kind}'.",
                        entity_type="node",
                        entity_id=nid,
                        expected=singular_kind,
                        actual=kind,
                        suggested_action=f"Set 'kind': '{singular_kind}' on node '{nid}'.",
                    )
                )
            node_kind_by_id[nid] = kind or singular_kind

            if not node.get("label"):
                errors.append(
                    ValidationError(
                        code="ERR_MISSING_NODE_LABEL",
                        severity=Severity.ERROR.value,
                        message=f"Node '{nid}' is missing required 'label'.",
                        entity_type="node",
                        entity_id=nid,
                        expected="string",
                        actual=node.get("label"),
                        suggested_action=f"Add a descriptive 'label' to node '{nid}'.",
                    )
                )

            if singular_kind == "supplier":
                if not node.get("supplier_id"):
                    errors.append(
                        ValidationError(
                            code="ERR_MISSING_SUPPLIER_ID",
                            severity=Severity.ERROR.value,
                            message=f"Supplier node '{nid}' missing 'supplier_id'.",
                            entity_type="node",
                            entity_id=nid,
                            suggested_action="Add 'supplier_id' matching the node id.",
                        )
                    )
                if not node.get("location"):
                    warnings.append(
                        ValidationError(
                            code="ERR_MISSING_LOCATION",
                            severity=Severity.WARNING.value,
                            message=f"Supplier node '{nid}' missing 'location'.",
                            entity_type="node",
                            entity_id=nid,
                            suggested_action="Specify a geographic location for the supplier.",
                        )
                    )

            elif singular_kind == "part":
                if not node.get("part_id"):
                    errors.append(
                        ValidationError(
                            code="ERR_MISSING_PART_ID",
                            severity=Severity.ERROR.value,
                            message=f"Part node '{nid}' missing 'part_id'.",
                            entity_type="node",
                            entity_id=nid,
                        )
                    )
                for num_field in ("stock_on_hand", "daily_consumption", "days_of_supply"):
                    val = node.get(num_field)
                    if val is None or not isinstance(val, (int, float)) or val < 0:
                        errors.append(
                            ValidationError(
                                code="ERR_INVALID_PART_NUMERIC_FIELD",
                                severity=Severity.ERROR.value,
                                message=(
                                    f"Part '{nid}' field '{num_field}' must be a non-negative number, "
                                    f"got {val!r}."
                                ),
                                entity_type="node",
                                entity_id=nid,
                                expected="numeric >= 0",
                                actual=val,
                                suggested_action=f"Provide a valid non-negative numeric value for '{num_field}'.",
                            )
                        )

            elif singular_kind == "product":
                if not node.get("product_id"):
                    errors.append(
                        ValidationError(
                            code="ERR_MISSING_PRODUCT_ID",
                            severity=Severity.ERROR.value,
                            message=f"Product node '{nid}' missing 'product_id'.",
                            entity_type="node",
                            entity_id=nid,
                        )
                    )

            elif singular_kind == "order":
                if not node.get("order_id"):
                    errors.append(
                        ValidationError(
                            code="ERR_MISSING_ORDER_ID",
                            severity=Severity.ERROR.value,
                            message=f"Order node '{nid}' missing 'order_id'.",
                            entity_type="node",
                            entity_id=nid,
                        )
                    )
                qty = node.get("quantity")
                if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
                    errors.append(
                        ValidationError(
                            code="ERR_INVALID_ORDER_QUANTITY",
                            severity=Severity.ERROR.value,
                            message=f"Order '{nid}' quantity must be a positive number, got {qty!r}.",
                            entity_type="node",
                            entity_id=nid,
                            expected="number > 0",
                            actual=qty,
                            suggested_action="Specify a quantity greater than zero.",
                        )
                    )
                if not node.get("deadline"):
                    errors.append(
                        ValidationError(
                            code="ERR_MISSING_DEADLINE",
                            severity=Severity.ERROR.value,
                            message=f"Order '{nid}' missing required 'deadline'.",
                            entity_type="node",
                            entity_id=nid,
                        )
                    )

    if duplicate_ids:
        checks.append(
            ValidationCheck(
                check_id="NODE_DUPLICATES",
                status=CheckStatus.FAIL.value,
                message=f"Duplicate node IDs detected in raw records: {duplicate_ids}",
                details={"duplicates": duplicate_ids},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                check_id="NODE_DUPLICATES",
                status=CheckStatus.PASS.value,
                message="All node identifiers are unique across raw records.",
            )
        )

    return seen_node_ids, node_records_by_id, node_kind_by_id, node_category_counts, duplicate_ids

