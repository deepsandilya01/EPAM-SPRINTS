"""
Team Photon — Graph Structure Validation Module
─────────────────────────────────────────────────
Provides rigorous schema, count, reference, direction, and acyclicity validation
for the supply-chain dependency graph.
"""

from datetime import UTC, datetime
from typing import Any

import networkx as nx

from .schema import (
    AcyclicityPolicy,
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
    ValidationReport,
)


def _iso_now() -> str:
    """Return ISO 8601 formatted timestamp in UTC."""
    return datetime.now(UTC).isoformat()


def validate_raw_graph_data(
    raw_data: Any,
    policy: ValidationPolicy | None = None
) -> ValidationReport:
    """
    Validate raw JSON-like dictionary data BEFORE constructing a NetworkX graph.

    This pre-construction validation is mandatory because NetworkX DiGraph silently
    collapses duplicate node identifiers upon insertion.

    Checks performed:
    1. Top-level JSON schema (dict type, required keys: 'nodes', 'edges').
    2. Missing/empty node IDs and duplicate node IDs across raw records.
    3. Node required fields and value types per category.
    4. Edge endpoints existence, missing references, edge types.
    5. Edge direction compliance (Supplier -> Part -> Product -> Order).
    6. Edge required attributes.
    7. Baseline count matching (when policy.check_baseline_counts is True).
    8. Directedness and conditional acyclicity (DAG verification).
    """
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

    # ─────────────────────────────────────────────────────────────
    # Check 1: Top-Level Data Structure
    # ─────────────────────────────────────────────────────────────
    if not isinstance(raw_data, dict):
        err = ValidationError(
            code="ERR_INVALID_TOP_LEVEL_TYPE",
            severity=Severity.CRITICAL.value,
            message=f"Top-level data must be a JSON object (dict), got {type(raw_data).__name__}.",
            entity_type="structure",
            expected="dict",
            actual=type(raw_data).__name__,
            suggested_action="Ensure the root of the graph data JSON is an object with 'nodes' and 'edges'."
        )
        errors.append(err)
        checks.append(ValidationCheck(
            check_id="SCHEMA_TOP_LEVEL",
            status=CheckStatus.FAIL.value,
            message="Top-level structure is not a dictionary.",
            details={"type": type(raw_data).__name__}
        ))
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
        errors.append(ValidationError(
            code="ERR_MISSING_NODES_KEY",
            severity=Severity.CRITICAL.value,
            message="Top-level key 'nodes' is missing or not a dictionary.",
            entity_type="structure",
            expected="dict",
            actual=type(raw_data.get("nodes")).__name__,
            suggested_action="Add a 'nodes' object containing node category lists."
        ))
    if "edges" not in raw_data or not isinstance(raw_data.get("edges"), dict):
        errors.append(ValidationError(
            code="ERR_MISSING_EDGES_KEY",
            severity=Severity.CRITICAL.value,
            message="Top-level key 'edges' is missing or not a dictionary.",
            entity_type="structure",
            expected="dict",
            actual=type(raw_data.get("edges")).__name__,
            suggested_action="Add an 'edges' object containing relationship category lists."
        ))

    if errors:
        checks.append(ValidationCheck(
            check_id="SCHEMA_TOP_LEVEL",
            status=CheckStatus.FAIL.value,
            message="Top-level schema is missing required 'nodes' or 'edges' dictionary.",
        ))
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

    checks.append(ValidationCheck(
        check_id="SCHEMA_TOP_LEVEL",
        status=CheckStatus.PASS.value,
        message="Top-level data structure is valid with 'nodes' and 'edges'."
    ))

    raw_nodes = raw_data["nodes"]
    raw_edges = raw_data["edges"]

    # ─────────────────────────────────────────────────────────────
    # Check 2: Node Entities, Duplicate IDs & Required Attributes
    # ─────────────────────────────────────────────────────────────
    seen_node_ids: set[str] = set()
    node_records_by_id: dict[str, dict[str, Any]] = {}
    node_kind_by_id: dict[str, str] = {}
    node_category_counts: dict[str, int] = {cat: 0 for cat in policy.allowed_node_categories}
    duplicate_ids: list[str] = []

    for cat in policy.allowed_node_categories:
        cat_list = raw_nodes.get(cat, [])
        if not isinstance(cat_list, list):
            errors.append(ValidationError(
                code="ERR_INVALID_CATEGORY_TYPE",
                severity=Severity.ERROR.value,
                message=f"Node category '{cat}' must be a list, got {type(cat_list).__name__}.",
                entity_type="node",
                expected="list",
                actual=type(cat_list).__name__,
                suggested_action=f"Define raw_nodes['{cat}'] as a list of node records."
            ))
            continue

        singular_kind = cat.removesuffix("s")  # suppliers -> supplier

        for idx, node in enumerate(cat_list):
            node_category_counts[cat] += 1
            if not isinstance(node, dict):
                errors.append(ValidationError(
                    code="ERR_MALFORMED_NODE_RECORD",
                    severity=Severity.ERROR.value,
                    message=f"Node at index {idx} in category '{cat}' is not a dict.",
                    entity_type="node",
                    expected="dict",
                    actual=type(node).__name__,
                    suggested_action="Ensure every node record is a JSON object."
                ))
                continue

            nid = node.get("id")
            if nid is None:
                errors.append(ValidationError(
                    code="ERR_MISSING_NODE_ID",
                    severity=Severity.CRITICAL.value,
                    message=f"Node at index {idx} in category '{cat}' is missing required 'id'.",
                    entity_type="node",
                    expected="non-empty string",
                    actual=None,
                    suggested_action="Assign a unique string identifier (e.g., 'SUP-01', 'PART-01') to 'id'."
                ))
                continue
            elif not isinstance(nid, str) or not nid.strip():
                errors.append(ValidationError(
                    code="ERR_EMPTY_NODE_ID",
                    severity=Severity.CRITICAL.value,
                    message=f"Node at index {idx} in category '{cat}' has empty or non-string id: {nid!r}.",
                    entity_type="node",
                    expected="non-empty string",
                    actual=repr(nid),
                    suggested_action="Provide a valid, non-blank string for the node identifier."
                ))
                continue

            # Duplicate ID check in raw records
            if nid in seen_node_ids:
                duplicate_ids.append(nid)
                errors.append(ValidationError(
                    code="ERR_DUPLICATE_NODE_ID",
                    severity=Severity.CRITICAL.value,
                    message=f"Duplicate node identifier '{nid}' detected in raw node records.",
                    entity_type="node",
                    entity_id=nid,
                    expected="unique node identifier",
                    actual=f"Duplicate id '{nid}' in category '{cat}'",
                    suggested_action="Ensure all entity IDs are globally unique across all categories."
                ))
            else:
                seen_node_ids.add(nid)
                node_records_by_id[nid] = node

            # Kind attribute verification
            kind = node.get("kind")
            if kind != singular_kind:
                errors.append(ValidationError(
                    code="ERR_INVALID_NODE_KIND",
                    severity=Severity.ERROR.value,
                    message=f"Node '{nid}' has kind '{kind}', expected '{singular_kind}'.",
                    entity_type="node",
                    entity_id=nid,
                    expected=singular_kind,
                    actual=kind,
                    suggested_action=f"Set 'kind': '{singular_kind}' on node '{nid}'."
                ))
            node_kind_by_id[nid] = kind or singular_kind

            # Required attribute checks per category
            if not node.get("label"):
                errors.append(ValidationError(
                    code="ERR_MISSING_NODE_LABEL",
                    severity=Severity.ERROR.value,
                    message=f"Node '{nid}' is missing required 'label'.",
                    entity_type="node",
                    entity_id=nid,
                    expected="string",
                    actual=node.get("label"),
                    suggested_action=f"Add a descriptive 'label' to node '{nid}'."
                ))

            if singular_kind == "supplier":
                if not node.get("supplier_id"):
                    errors.append(ValidationError(
                        code="ERR_MISSING_SUPPLIER_ID",
                        severity=Severity.ERROR.value,
                        message=f"Supplier node '{nid}' missing 'supplier_id'.",
                        entity_type="node",
                        entity_id=nid,
                        suggested_action="Add 'supplier_id' matching the node id."
                    ))
                if not node.get("location"):
                    errors.append(ValidationError(
                        code="ERR_MISSING_LOCATION",
                        severity=Severity.WARNING.value,
                        message=f"Supplier node '{nid}' missing 'location'.",
                        entity_type="node",
                        entity_id=nid,
                        suggested_action="Specify a geographic location for the supplier."
                    ))

            elif singular_kind == "part":
                if not node.get("part_id"):
                    errors.append(ValidationError(
                        code="ERR_MISSING_PART_ID",
                        severity=Severity.ERROR.value,
                        message=f"Part node '{nid}' missing 'part_id'.",
                        entity_type="node",
                        entity_id=nid,
                    ))
                for num_field in ("stock_on_hand", "daily_consumption", "days_of_supply"):
                    val = node.get(num_field)
                    if val is None or not isinstance(val, (int, float)) or val < 0:
                        errors.append(ValidationError(
                            code="ERR_INVALID_PART_NUMERIC_FIELD",
                            severity=Severity.ERROR.value,
                            message=f"Part '{nid}' field '{num_field}' must be a non-negative number, got {val!r}.",
                            entity_type="node",
                            entity_id=nid,
                            expected="numeric >= 0",
                            actual=val,
                            suggested_action=f"Provide a valid non-negative numeric value for '{num_field}'."
                        ))

            elif singular_kind == "product":
                if not node.get("product_id"):
                    errors.append(ValidationError(
                        code="ERR_MISSING_PRODUCT_ID",
                        severity=Severity.ERROR.value,
                        message=f"Product node '{nid}' missing 'product_id'.",
                        entity_type="node",
                        entity_id=nid,
                    ))

            elif singular_kind == "order":
                if not node.get("order_id"):
                    errors.append(ValidationError(
                        code="ERR_MISSING_ORDER_ID",
                        severity=Severity.ERROR.value,
                        message=f"Order node '{nid}' missing 'order_id'.",
                        entity_type="node",
                        entity_id=nid,
                    ))
                qty = node.get("quantity")
                if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
                    errors.append(ValidationError(
                        code="ERR_INVALID_ORDER_QUANTITY",
                        severity=Severity.ERROR.value,
                        message=f"Order '{nid}' quantity must be a positive number, got {qty!r}.",
                        entity_type="node",
                        entity_id=nid,
                        expected="number > 0",
                        actual=qty,
                        suggested_action="Specify a quantity greater than zero."
                    ))
                if not node.get("deadline"):
                    errors.append(ValidationError(
                        code="ERR_MISSING_DEADLINE",
                        severity=Severity.ERROR.value,
                        message=f"Order '{nid}' missing required 'deadline'.",
                        entity_type="node",
                        entity_id=nid,
                    ))

    summary["node_count"] = len(seen_node_ids)
    summary["supplier_count"] = node_category_counts.get("suppliers", 0)
    summary["part_count"] = node_category_counts.get("parts", 0)
    summary["product_count"] = node_category_counts.get("products", 0)
    summary["order_count"] = node_category_counts.get("orders", 0)

    # Record node duplicate check
    if duplicate_ids:
        checks.append(ValidationCheck(
            check_id="NODE_DUPLICATES",
            status=CheckStatus.FAIL.value,
            message=f"Duplicate node IDs detected in raw records: {duplicate_ids}",
            details={"duplicates": duplicate_ids}
        ))
    else:
        checks.append(ValidationCheck(
            check_id="NODE_DUPLICATES",
            status=CheckStatus.PASS.value,
            message="All node identifiers are unique across raw records."
        ))

    # ─────────────────────────────────────────────────────────────
    # Check 3: Edge Integrity, Nonexistent References, and Direction
    # ─────────────────────────────────────────────────────────────
    edge_type_counts: dict[str, int] = {et: 0 for et in policy.allowed_edge_types}
    total_valid_edges = 0
    invalid_edges: list[dict[str, Any]] = []

    for edge_type in policy.allowed_edge_types:
        edge_list = raw_edges.get(edge_type, [])
        if not isinstance(edge_list, list):
            errors.append(ValidationError(
                code="ERR_INVALID_EDGE_CATEGORY_TYPE",
                severity=Severity.ERROR.value,
                message=f"Edge category '{edge_type}' must be a list, got {type(edge_list).__name__}.",
                entity_type="edge",
                expected="list",
                actual=type(edge_list).__name__,
            ))
            continue

        rule = policy.direction_rules.get(edge_type)
        expected_src_kind = rule[0] if rule else None
        expected_tgt_kind = rule[1] if rule else None
        expected_rel_str = rule[2] if rule else None

        for idx, edge in enumerate(edge_list):
            edge_type_counts[edge_type] += 1
            if not isinstance(edge, dict):
                errors.append(ValidationError(
                    code="ERR_MALFORMED_EDGE_RECORD",
                    severity=Severity.ERROR.value,
                    message=f"Edge at index {idx} in '{edge_type}' is not a dict.",
                    entity_type="edge",
                    expected="dict",
                    actual=type(edge).__name__,
                ))
                continue

            src = edge.get("source")
            tgt = edge.get("target")

            if not src or not isinstance(src, str):
                errors.append(ValidationError(
                    code="ERR_MISSING_EDGE_SOURCE",
                    severity=Severity.CRITICAL.value,
                    message=f"Edge in '{edge_type}' missing valid 'source'.",
                    entity_type="edge",
                    actual=src,
                    suggested_action="Specify a valid node identifier for 'source'."
                ))
                invalid_edges.append(edge)
                continue

            if not tgt or not isinstance(tgt, str):
                errors.append(ValidationError(
                    code="ERR_MISSING_EDGE_TARGET",
                    severity=Severity.CRITICAL.value,
                    message=f"Edge in '{edge_type}' from '{src}' missing valid 'target'.",
                    entity_type="edge",
                    actual=tgt,
                    suggested_action="Specify a valid node identifier for 'target'."
                ))
                invalid_edges.append(edge)
                continue

            # Reference existence checks
            src_exists = src in seen_node_ids
            tgt_exists = tgt in seen_node_ids

            if not src_exists:
                errors.append(ValidationError(
                    code="ERR_NONEXISTENT_SOURCE_NODE",
                    severity=Severity.CRITICAL.value,
                    message=f"Edge references nonexistent source node '{src}'.",
                    entity_type="edge",
                    entity_id=(src, tgt),
                    expected=f"Existing node in {list(seen_node_ids)[:5]}...",
                    actual=src,
                    suggested_action=f"Define node '{src}' in raw_nodes before referencing it."
                ))
            if not tgt_exists:
                errors.append(ValidationError(
                    code="ERR_NONEXISTENT_TARGET_NODE",
                    severity=Severity.CRITICAL.value,
                    message=f"Edge references nonexistent target node '{tgt}'.",
                    entity_type="edge",
                    entity_id=(src, tgt),
                    expected=f"Existing node in {list(seen_node_ids)[:5]}...",
                    actual=tgt,
                    suggested_action=f"Define node '{tgt}' in raw_nodes before referencing it."
                ))

            if not src_exists or not tgt_exists:
                invalid_edges.append(edge)
                continue

            # Relation name check
            rel = edge.get("relation")
            if expected_rel_str and rel != expected_rel_str:
                errors.append(ValidationError(
                    code="ERR_INVALID_RELATION_NAME",
                    severity=Severity.ERROR.value,
                    message=f"Edge '{src} -> {tgt}' in category '{edge_type}' has relation '{rel}', expected '{expected_rel_str}'.",
                    entity_type="edge",
                    entity_id=(src, tgt),
                    expected=expected_rel_str,
                    actual=rel,
                    suggested_action=f"Set 'relation': '{expected_rel_str}' on this edge."
                ))

            # Edge Direction check (Supplier -> Part -> Product -> Order)
            src_kind = node_kind_by_id.get(src)
            tgt_kind = node_kind_by_id.get(tgt)

            if expected_src_kind and src_kind != expected_src_kind:
                errors.append(ValidationError(
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
                    suggested_action=f"Ensure '{edge_type}' edges originate from a '{expected_src_kind}'."
                ))
                invalid_edges.append(edge)
                continue

            if expected_tgt_kind and tgt_kind != expected_tgt_kind:
                errors.append(ValidationError(
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
                    suggested_action=f"Ensure '{edge_type}' edges terminate at a '{expected_tgt_kind}'."
                ))
                invalid_edges.append(edge)
                continue

            total_valid_edges += 1

    summary["edge_count"] = sum(edge_type_counts.values())
    summary["supplies_count"] = edge_type_counts.get("supplies", 0)
    summary["used_in_count"] = edge_type_counts.get("used_in", 0)
    summary["fulfills_count"] = edge_type_counts.get("fulfills", 0)

    # Edge Reference Check
    has_ref_errors = any(
        e.code in ("ERR_NONEXISTENT_SOURCE_NODE", "ERR_NONEXISTENT_TARGET_NODE", "ERR_MISSING_EDGE_SOURCE", "ERR_MISSING_EDGE_TARGET")
        for e in errors
    )
    if has_ref_errors:
        checks.append(ValidationCheck(
            check_id="EDGE_REFERENCES",
            status=CheckStatus.FAIL.value,
            message="One or more edges reference nonexistent or invalid node endpoints.",
        ))
    else:
        checks.append(ValidationCheck(
            check_id="EDGE_REFERENCES",
            status=CheckStatus.PASS.value,
            message="All edges connect valid existing nodes."
        ))

    # Edge Direction Check
    has_dir_errors = any(e.code == "ERR_INVALID_EDGE_DIRECTION" for e in errors)
    if has_dir_errors:
        checks.append(ValidationCheck(
            check_id="EDGE_DIRECTIONS",
            status=CheckStatus.FAIL.value,
            message="One or more edges violate the agreed supply-chain dependency direction.",
        ))
    else:
        checks.append(ValidationCheck(
            check_id="EDGE_DIRECTIONS",
            status=CheckStatus.PASS.value,
            message="All edges follow the agreed supply-chain direction (Supplier -> Part -> Product -> Order)."
        ))

    # ─────────────────────────────────────────────────────────────
    # Check 4: Baseline Count Validation (Configurable)
    # ─────────────────────────────────────────────────────────────
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
            errors.append(ValidationError(
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
                suggested_action="Verify if the input data represents the canonical 19-node Sprint 1 baseline graph."
            ))
            checks.append(ValidationCheck(
                check_id="BASELINE_NODE_COUNTS",
                status=CheckStatus.FAIL.value,
                message="Node counts do not match baseline expected counts.",
                details={"expected": bc.to_dict(), "actual": summary}
            ))
        else:
            checks.append(ValidationCheck(
                check_id="BASELINE_NODE_COUNTS",
                status=CheckStatus.PASS.value,
                message="Expected baseline node counts match exactly (19 nodes: 2 sup, 5 part, 2 prod, 10 ord)."
            ))

        if not edge_counts_match:
            errors.append(ValidationError(
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
                suggested_action="Verify if the input data represents the canonical 21-edge Sprint 1 baseline graph."
            ))
            checks.append(ValidationCheck(
                check_id="BASELINE_EDGE_COUNTS",
                status=CheckStatus.FAIL.value,
                message="Edge counts do not match baseline expected counts.",
                details={"expected": bc.to_dict(), "actual": summary}
            ))
        else:
            checks.append(ValidationCheck(
                check_id="BASELINE_EDGE_COUNTS",
                status=CheckStatus.PASS.value,
                message="Expected baseline edge counts match exactly (21 edges: 6 supplies, 5 used_in, 10 fulfills)."
            ))
    else:
        checks.append(ValidationCheck(
            check_id="BASELINE_COUNTS",
            status=CheckStatus.SKIP.value,
            message="Baseline count verification skipped (integrity mode active)."
        ))

    # ─────────────────────────────────────────────────────────────
    # Check 5: Graph Directedness & Conditional Acyclicity (DAG)
    # ─────────────────────────────────────────────────────────────
    # Only build DiGraph if there were no duplicate node IDs and endpoints exist
    if not duplicate_ids and not any(e.code in ("ERR_NONEXISTENT_SOURCE_NODE", "ERR_NONEXISTENT_TARGET_NODE") for e in errors):
        G = nx.DiGraph()
        for nid, nattrs in node_records_by_id.items():
            G.add_node(nid, **nattrs)
        for edge_type in policy.allowed_edge_types:
            for edge in raw_edges.get(edge_type, []):
                if isinstance(edge, dict) and "source" in edge and "target" in edge:
                    edge_attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
                    G.add_edge(edge["source"], edge["target"], **edge_attrs)

        checks.append(ValidationCheck(
            check_id="GRAPH_DIRECTED",
            status=CheckStatus.PASS.value,
            message="Graph is a valid directed graph (DiGraph)."
        ))

        # Acyclicity Validation
        _evaluate_acyclicity(G, policy, checks, errors, warnings)
    else:
        checks.append(ValidationCheck(
            check_id="GRAPH_DIRECTED",
            status=CheckStatus.SKIP.value,
            message="DiGraph construction skipped due to fatal duplicate ID or nonexistent endpoint errors."
        ))
        checks.append(ValidationCheck(
            check_id="GRAPH_ACYCLICITY",
            status=CheckStatus.SKIP.value,
            message="Acyclicity check skipped due to invalid node/edge entities."
        ))

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
        return validate_raw_graph_data(data_or_graph, policy=policy)
    else:
        raise TypeError(f"Unsupported data type for validation: {type(data_or_graph).__name__}. Expected dict or nx.DiGraph.")
