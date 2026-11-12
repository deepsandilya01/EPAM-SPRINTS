# REST API Reference

The Flask backend exposes **12 registered routes** across **10 unique handler functions**. All programmatic endpoints are prefixed with `/api` (with `/` serving the interactive UI and static assets).

---

## Endpoint Summary

| Route Rule | HTTP Method | Handler Function | Purpose |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | `main.index` | Serves interactive D3.js web visualizer |
| `/api/health` | `GET` | `routes.health.api_health` | Service health status & active entity counts |
| `/api/graph` | `GET` | `routes.graph.api_graph` | Active graph nodes & edges |
| `/api/node/<node_id>` | `DELETE` | `routes.graph.api_delete_node` | Cascading node disruption/deletion |
| `/api/undo` | `POST` | `routes.graph.api_undo` | Reverts last deletion from undo stack |
| `/api/reset` | `POST` | `routes.graph.api_reset` | Resets graph to original 19-node state |
| `/api/downstream/<node_id>` | `GET` | `routes.traversal.api_downstream` | Downstream reachable node IDs via BFS |
| `/api/impact/<node_id>` | `GET` | `routes.traversal.api_impact` | Blast radius impact summary |
| `/api/traversal` | `POST` | `routes.traversal.api_traversal` | Parameterized downstream traversal query |
| `/api/validation` | `GET` | `routes.validation.api_validation` | Structural integrity & schema audit |
| `/api/benchmarks` | `GET` | `routes.benchmarks.api_benchmark_tracing` | Traversal latency benchmark against 10ms SLA |
| `/api/benchmark/tracing` | `GET` | `routes.benchmarks.api_benchmark_tracing` | Traversal latency benchmark against 10ms SLA |

---

## Detailed Endpoint Specifications

### 1. Health

#### `GET /api/health`
Returns service status and active graph counts.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "RE:Flow — Supply Chain Graph",
  "version": "1.0.0",
  "node_count": 19,
  "edge_count": 21
}
```

---

### 2. Graph State & Mutation

#### `GET /api/graph`
Returns all active nodes and edges formatted for visualization.

**Response `200 OK`**:
```json
{
  "directed": true,
  "multigraph": false,
  "nodes": [
    {
      "id": "SUP-01",
      "label": "Apex Microelectronics",
      "tier": "supplier",
      "kind": "supplier",
      "location": "Taipei, TW",
      "reliability_score": 0.96
    }
  ],
  "edges": [
    {
      "source": "SUP-01",
      "target": "PART-01",
      "relation": "SUPPLIES",
      "lead_time_days": 14
    }
  ]
}
```

#### `DELETE /api/node/<node_id>`
Simulates a supply chain disruption by removing a node and all downstream dependent parts, products, and customer orders. Previous state is saved to the undo stack.

**Path Parameters**:
- `node_id` (`str`, required): The node ID to remove (e.g. `SUP-01`).

**Response `200 OK`**:
```json
{
  "status": "success",
  "deleted_node": "SUP-01",
  "nodes_removed": ["SUP-01", "PART-01", "PART-02", "PROD-01", "ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005"],
  "edges_removed": 12,
  "can_undo": true,
  "current_node_count": 10,
  "current_edge_count": 9
}
```

**Errors**:
- `404 Not Found`: If `node_id` is not present in the active graph.

#### `POST /api/undo`
Restores the previous graph state from the in-memory undo stack.

**Response `200 OK`**:
```json
{
  "status": "success",
  "restored": true,
  "can_undo": false,
  "node_count": 19,
  "edge_count": 21
}
```

**Errors**:
- `400 Bad Request`: If the undo stack is empty (`"Nothing to undo"`).

#### `POST /api/reset`
Reloads the canonical 19-node, 21-edge dataset and clears the undo stack.

**Response `200 OK`**:
```json
{
  "status": "success",
  "message": "Graph reset to canonical baseline (19 nodes, 21 edges)",
  "node_count": 19,
  "edge_count": 21,
  "can_undo": false
}
```

---

### 3. Graph Traversal & Blast Radius

#### `POST /api/traversal`
Parameterized downstream traversal query accepting a JSON request body.

**Request Body**:
```json
{
  "start_node": "SUP-01",
  "direction": "downstream",
  "max_depth": 10
}
```

**Response `200 OK`**:
```json
{
  "start_node": "SUP-01",
  "downstream_nodes": ["PART-01", "PART-02", "PROD-01", "ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005"],
  "downstream_count": 8,
  "total_affected": 8,
  "execution_time_ms": 0.003
}
```

#### `GET /api/downstream/<node_id>`
Executes Breadth-First Search (BFS) to identify all downstream reachable nodes from `node_id`.

**Path Parameters**:
- `node_id` (`str`, required): The starting node identifier (e.g. `SUP-01`).

**Response `200 OK`**:
```json
{
  "start_node": "SUP-01",
  "downstream_nodes": [
    "PART-01",
    "PART-02",
    "PROD-01",
    "ORD-001",
    "ORD-002",
    "ORD-003",
    "ORD-004",
    "ORD-005"
  ],
  "downstream_count": 8,
  "total_affected": 8,
  "execution_time_ms": 0.003
}
```

**Errors**:
- `404 Not Found`: If `node_id` does not exist in the active graph.

#### `GET /api/impact/<node_id>`
Provides a categorized breakdown of affected downstream entities along with financial risk impact.

**Response `200 OK`**:
```json
{
  "node_id": "SUP-01",
  "affected_nodes": ["PART-01", "PART-02", "PROD-01", "ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005"],
  "total_affected": 8,
  "tier_breakdown": {
    "suppliers": 0,
    "parts": 2,
    "products": 1,
    "orders": 5
  },
  "at_risk_orders": ["ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005"],
  "total_revenue_at_risk": 1250000.0,
  "execution_time_ms": 0.004
}
```

---

### 4. Graph Validation

#### `GET /api/validation`
Runs the graph validation engine and returns a structured audit report.

**Query Parameters**:
- `mode` (`str`, optional): `'baseline'` (default) or `'integrity'`.
- `strict` (`bool`, optional): Treat warnings as errors (`true`/`false`, default `true`).

**Response `200 OK`**:
```json
{
  "is_valid": true,
  "valid": true,
  "graph_name": "Live NetworkX Graph",
  "mode": "baseline",
  "summary": {
    "node_count": 19,
    "edge_count": 21,
    "supplier_count": 2,
    "part_count": 5,
    "product_count": 2,
    "order_count": 10
  },
  "checks": [
    {
      "check_id": "GRAPH_DIRECTED",
      "status": "PASS",
      "message": "Graph is a valid directed graph."
    },
    {
      "check_id": "GRAPH_ACYCLICITY",
      "status": "PASS",
      "message": "Graph is a verified Directed Acyclic Graph (DAG) with zero cycles."
    }
  ],
  "errors": [],
  "warnings": [],
  "timestamp": "2026-10-31T16:00:00+00:00"
}
```

**Errors**:
- `400 Bad Request`: If an invalid `mode` parameter is passed.

---

### 5. Latency Benchmarking

#### `GET /api/benchmarks` / `GET /api/benchmark/tracing`
Executes downstream traversal latency benchmarking against the 10.0 ms SLA.

**Query Parameters**:
- `node_id` (`str`, optional): Starting node (default `"SUP-01"`).
- `threshold_ms` (`float`, optional): SLA threshold in ms (default `10.0`).

**Response `200 OK`**:
```json
{
  "node_id": "SUP-01",
  "iterations": 100,
  "sla_threshold_ms": 10.0,
  "mean_latency_ms": 0.0031,
  "median_latency_ms": 0.0029,
  "p95_latency_ms": 0.0042,
  "max_latency_ms": 0.0120,
  "sla_met": true,
  "status": "PASS",
  "reachable_nodes_count": 8
}
```

