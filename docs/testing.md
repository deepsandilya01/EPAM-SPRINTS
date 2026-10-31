# Testing Suite & Verification

## Overview

RE:Flow features a comprehensive automated test suite written for **pytest**. The test suite validates schema enforcement, graph data structures, traversal algorithms, validation rules, HTTP APIs, and error-handling edge cases across **130 automated test cases**.

The entire suite executes in approximately **0.10 seconds** on standard hardware.

---

## Test Organization

```
backend/tests/
├── conftest.py                     # Shared pytest fixtures (app_client, canonical_data)
├── integration/
│   └── test_api.py                 # End-to-end HTTP API integration tests (25 tests)
└── unit/
    ├── test_api_schemas.py         # Pydantic request & response contracts (9 tests)
    ├── test_domain_models.py       # Domain dataclasses & invariants (17 tests)
    ├── test_edge_cases.py          # Boundary checks & malformed inputs (21 tests)
    ├── test_graph.py               # Graph construction & count assertions (23 tests)
    ├── test_traversal.py           # Downstream BFS traversal & metrics (5 tests)
    └── test_validation.py          # Validation rules, cycles & reports (30 tests)
```

---

## Running Tests

### 1. Execute All Tests

Run pytest from the repository root:

```bash
python3 -m pytest backend/tests/ -v
```

Expected output:
```text
============================== 130 passed in 0.10s ==============================
```

### 2. Run Specific Test Modules

```bash
# Run unit tests only
python3 -m pytest backend/tests/unit/ -v

# Run integration tests only
python3 -m pytest backend/tests/integration/ -v

# Run validation engine tests only
python3 -m pytest backend/tests/unit/test_validation.py -v
```

### 3. Run Ruff Code Quality Linting

```bash
python3 -m ruff check backend/ scripts/
```

Expected output:
```text
All checks passed!
```

---

## Key Test Scenarios Covered

1. **Exact Baseline Entity Counts**: Confirms exactly 19 nodes (2 suppliers, 5 parts, 2 products, 10 orders) and 21 edges (6 supplies, 5 used_in, 10 fulfills).
2. **Deterministic Downstream Reachability**:
   - `SUP-01` reaches exactly 8 nodes: `PART-01`, `PART-02`, `PROD-01`, `ORD-001`, `ORD-002`, `ORD-003`, `ORD-004`, `ORD-005`.
   - `SUP-02` reaches exactly 11 nodes: `PART-03`, `PART-04`, `PART-05`, `PROD-02`, `ORD-006` through `ORD-010`, plus `PROD-01` and its orders via shared part `PART-03`.
3. **Cycle Rejection**: Ensures directed cycles are immediately flagged with `ERR_CYCLE_DETECTED` and fail validation.
4. **Endpoint Reference Integrity**: Asserts that edges pointing to or originating from nonexistent IDs are rejected with `ERR_NONEXISTENT_SOURCE_NODE` or `ERR_NONEXISTENT_TARGET_NODE`.
5. **Cascading Deletion Lifecycle**: Verifies that deleting a supplier removes dependent components and orders, that integrity mode validation passes on the reduced graph, and that undo completely restores original state.
6. **HTTP Error Handling**: Validates proper `400`, `404`, and `405` JSON responses for invalid parameters, missing nodes, and unsupported methods.

