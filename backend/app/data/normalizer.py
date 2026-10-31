from __future__ import annotations

from typing import Any

from backend.app.core.constants import TierType
from backend.app.core.exceptions import ModelValidationError


def normalize_scenario_data(raw_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize and normalize raw scenario dictionary into canonical structures.

    Ensures:
      - All nodes have non-empty IDs, names, and recognized tier strings.
      - Node IDs are globally unique across all tiers.
      - All edges have source, target, and valid relation names.
    """
    if not isinstance(raw_dict, dict):
        raise ModelValidationError("Raw scenario data must be a JSON dictionary.")

    normalized_nodes: list[dict[str, Any]] = []
    normalized_edges: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Category-based extraction
    category_to_tier = {
        "suppliers": TierType.SUPPLIER.value,
        "parts": TierType.BOM_PART.value,
        "products": TierType.FINISHED_PRODUCT.value,
        "orders": TierType.CUSTOMER_ORDER.value,
    }

    for cat_key, tier_name in category_to_tier.items():
        items = raw_dict.get(cat_key, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            node_id = str(item.get("id", "")).strip()
            if not node_id:
                raise ModelValidationError("Encountered node with empty 'id'.", field="id")
            if node_id in seen_ids:
                raise ModelValidationError(f"Duplicate node ID detected: '{node_id}'", field="id")
            seen_ids.add(node_id)

            node_copy = dict(item)
            node_copy["id"] = node_id
            node_copy["tier"] = tier_name
            normalized_nodes.append(node_copy)

    # Edge extraction
    edge_keys = ("supplies", "used_in", "fulfills")
    for ek in edge_keys:
        edges = raw_dict.get(ek, [])
        if not isinstance(edges, list):
            continue
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src = str(edge.get("source", "")).strip()
            tgt = str(edge.get("target", "")).strip()
            rel = edge.get("relation", edge.get("type", ek))
            if not src or not tgt:
                raise ModelValidationError("Edge must contain non-empty 'source' and 'target'.")
            edge_copy = dict(edge)
            edge_copy["source"] = src
            edge_copy["target"] = tgt
            edge_copy["relation"] = rel
            normalized_edges.append(edge_copy)

    # Fallback to flat "nodes" and "edges" if category keys were empty
    if not normalized_nodes and "nodes" in raw_dict and isinstance(raw_dict["nodes"], list):
        for item in raw_dict["nodes"]:
            if not isinstance(item, dict):
                continue
            node_id = str(item.get("id", "")).strip()
            if not node_id:
                raise ModelValidationError("Encountered node with empty 'id'.", field="id")
            if node_id in seen_ids:
                raise ModelValidationError(f"Duplicate node ID detected: '{node_id}'", field="id")
            seen_ids.add(node_id)
            normalized_nodes.append(dict(item))

    if not normalized_edges and "edges" in raw_dict and isinstance(raw_dict["edges"], list):
        for edge in raw_dict["edges"]:
            if not isinstance(edge, dict):
                continue
            src = str(edge.get("source", "")).strip()
            tgt = str(edge.get("target", "")).strip()
            if not src or not tgt:
                raise ModelValidationError("Edge must contain non-empty 'source' and 'target'.")
            normalized_edges.append(dict(edge))

    return {
        "nodes": normalized_nodes,
        "edges": normalized_edges,
        "metadata": raw_dict.get("metadata", {}),
    }
