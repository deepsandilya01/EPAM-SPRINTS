# Downstream Dependency Traversal

## Overview

This module implements the **Downstream Dependency Traversal** task for Team Photon’s EPAM Sprint 1 project.

It takes an already-built directed graph and a supplier ID, then identifies the reachable parts, finished products, and customer orders affected downstream of that supplier.

## Objective

When a supplier is disrupted, the system needs to identify which connected supply-chain entities may be affected. This module provides the traversal result that can be used by later impact-analysis or recovery-planning components.

## Scope

### Included
- Accepts an existing NetworkX directed graph.
- Validates that the requested supplier exists in the graph.
- Validates that the starting node is a supplier.
- Traverses downstream dependencies.
- Groups reachable node IDs into three categories:
  - `parts`
  - `products`
  - `orders`
- Sorts each category for consistent, easy-to-test output.
- Avoids duplicate node IDs by using NetworkX reachability results.

### Not included
- Building or loading the graph from JSON.
- Detecting whether a supplier disruption has occurred.
- Calculating financial loss, delay, or SLA impact.
- Selecting an alternative supplier.
- Recommending or executing a recovery plan.

These responsibilities can be handled by other project components.

## Expected Graph Structure

The function expects a directed graph (`networkx.DiGraph`) whose edges point downstream, for example:

```text
Supplier -> Part -> Product -> Customer Order
```

Each node should have a `kind` attribute with one of these values:

- `supplier`
- `part`
- `product`
- `order`

For compatibility, the function also accepts `node_type` as a fallback attribute.

## Function

```python
find_downstream_dependencies(graph, supplier_id)
```

### Parameters

| Parameter | Description |
|---|---|
| `graph` | An already-built NetworkX directed graph (`nx.DiGraph`). |
| `supplier_id` | ID of the supplier node from which traversal starts. |

### Return Value

Returns a dictionary containing sorted lists:

```python
{
    "parts": ["PART-01", "PART-02"],
    "products": ["PROD-01"],
    "orders": ["ORD-01", "ORD-02"]
}
```

The example above illustrates the output format; actual results depend on the graph provided.

### Errors

- Raises `ValueError` if the supplier ID does not exist in the graph.
- Raises `ValueError` if the starting node exists but is not marked as a supplier.

## Example Usage

```python
import networkx as nx
from downstream_traversal import find_downstream_dependencies

# `graph` must already be built and contain the project's nodes and edges.
result = find_downstream_dependencies(graph, "SUP-01")

print(result["parts"])
print(result["products"])
print(result["orders"])
```

If the module is stored in a different folder from the calling Python file, update the import or package structure accordingly.

## Installation

Install NetworkX if it is not already available in the project environment:

```bash
pip install networkx
```

If the repository already has a dependency file (for example, `requirements.txt`), add or verify `networkx` there rather than installing it separately on every machine.

## Integration Notes

1. Build or load the graph using the project's existing graph-building code.
2. Import `find_downstream_dependencies` from this module.
3. Call it with the graph and supplier ID.
4. Pass the categorized result to the next component, such as impact analysis.

**Important:** If the application already has a generic downstream traversal function, coordinate with the team before integrating this module so the traversal logic is not duplicated. This module's additional purpose is to categorize reachable nodes into parts, products, and orders.

## Complexity

For a graph with `V` nodes and `E` edges, downstream reachability traversal using NetworkX is generally `O(V + E)` in the worst case. Categorizing and sorting the returned node IDs adds work proportional to the number of reachable nodes, including sorting costs.

## Status

This README documents the assigned **Downstream Dependency Traversal** component. It describes the intended module interface and integration approach; it does not claim that the module has been integrated into or tested against the full application.
