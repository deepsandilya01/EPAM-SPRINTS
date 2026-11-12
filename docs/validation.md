# Graph Validation Engine

## Overview

RE:Flow features a decoupled, modular validation engine located in `backend/app/validation/`. The validation engine audits graph datasets both **pre-construction** (from raw JSON dictionaries) and **post-construction** (on live in-memory `networkx.DiGraph` instances).

---

## Modular Architecture

The validation subsystem is organized into single-responsibility modules:

| Module | Purpose | Key Symbols |
| :--- | :--- | :--- |
| **`models.py`** | Data structures, enums, policy configurations, and error reports | `ValidationReport`, `ValidationError`, `ValidationCheck`, `ValidationPolicy`, `BaselineCounts`, `CheckStatus`, `Severity`, `AcyclicityPolicy` |
| **`cycles.py`** | Graph cycle detection and DAG acyclicity validation | `evaluate_acyclicity` |
| **`nodes.py`** | Node record parsing, uniqueness defense, and tier-specific schema checks | `validate_node_records` |
| **`edges.py`** | Edge record validation, endpoint reference checking, and direction rules | `validate_edge_records`, `validate_edge_relationships` |
| **`validator.py`** | High-level orchestrator exposing public validation APIs | `validate_raw_graph_data`, `validate_networkx_graph`, `validate_graph`, `validate_dataset_schema`, `validate_graph_topology` |
| **`reporting.py`** | Console ASCII rendering and JSON file persistence | `format_console_report`, `save_json_report` |
| **`__init__.py`** | Unified public package interface | Clean re-exports of all public functions and models |

---

## Dual Validation Modes

The validation engine supports two operational modes:

### 1. Baseline Mode (`mode=baseline`)
- Enforces strict canonical dataset counts: **19 nodes** (2 suppliers, 5 parts, 2 products, 10 orders) and **21 edges** (6 supplies, 5 used_in, 10 fulfills).
- Enforces strict DAG acyclicity and tier direction rules.
- Any deviation in node or edge counts results in a failing report (`ERR_BASELINE_COUNT_MISMATCH`).

### 2. Integrity Mode (`mode=integrity`)
- Relaxes exact count constraints to accommodate dynamic graph mutations during simulation scenarios (e.g. cascading node deletions).
- Continues enforcing structural invariants:
  - Directed Acyclic Graph (DAG) acyclicity (`GRAPH_ACYCLICITY`).
  - Valid endpoint references (`EDGE_REFERENCES`).
  - Proper tier progression directions (`EDGE_DIRECTIONS`).

---

## Standard Error Codes

| Error Code | Severity | Description |
| :--- | :--- | :--- |
| `ERR_INVALID_TOP_LEVEL_TYPE` | CRITICAL | Root JSON payload is not an object/dictionary |
| `ERR_MISSING_NODES_KEY` | CRITICAL | Missing required `'nodes'` dictionary |
| `ERR_MISSING_EDGES_KEY` | CRITICAL | Missing required `'edges'` dictionary |
| `ERR_INVALID_CATEGORY_TYPE` | ERROR | A category field (e.g. `suppliers`) is not a list |
| `ERR_MALFORMED_NODE_RECORD` | ERROR | Individual node record is not an object |
| `ERR_MISSING_NODE_ID` | CRITICAL | Node record is missing required `'id'` field |
| `ERR_EMPTY_NODE_ID` | CRITICAL | Node `'id'` is empty or non-string |
| `ERR_DUPLICATE_NODE_ID` | CRITICAL | Global duplicate node identifier detected across categories |
| `ERR_INVALID_NODE_KIND` | ERROR | Node `'kind'` does not match its category |
| `ERR_MISSING_NODE_LABEL` | ERROR | Node is missing descriptive `'label'` |
| `ERR_INVALID_PART_NUMERIC_FIELD` | ERROR | Negative or non-numeric stock/consumption/days of supply |
| `ERR_INVALID_ORDER_QUANTITY` | ERROR | Customer order quantity is zero or negative |
| `ERR_MISSING_DEADLINE` | ERROR | Order node is missing delivery `'deadline'` |
| `ERR_MISSING_EDGE_SOURCE` | CRITICAL | Edge record missing valid `'source'` endpoint |
| `ERR_MISSING_EDGE_TARGET` | CRITICAL | Edge record missing valid `'target'` endpoint |
| `ERR_NONEXISTENT_SOURCE_NODE` | CRITICAL | Edge references an unregistered source node |
| `ERR_NONEXISTENT_TARGET_NODE` | CRITICAL | Edge references an unregistered target node |
| `ERR_INVALID_RELATION_NAME` | ERROR | Relationship label does not match tier category |
| `ERR_INVALID_EDGE_DIRECTION` | CRITICAL | Edge violates tier hierarchy (e.g. reverse transition or tier skip) |
| `ERR_CYCLE_DETECTED` | CRITICAL | Directed cycle detected in graph dependency structure |
| `ERR_BASELINE_COUNT_MISMATCH` | ERROR | Entity or relationship count does not match expected baseline |

---

## Standalone CLI Usage

To run the validation audit from the command line:

```bash
python3 scripts/validate_graph.py
```

This runs both baseline dataset validation and live graph topology checks, outputting a formatted console table and updating `backend/reports/graph_validation_report.json`.

