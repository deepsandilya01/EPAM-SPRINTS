# Troubleshooting Guide

This guide covers common issues, debugging procedures, and resolutions when working with RE:Flow.

---

## 1. Port Collision / Address Already in Use

### Symptom
```text
OSError: [Errno 48] Address already in use
```

### Cause
Another process is already listening on port `5050`.

### Solution
Either kill the occupying process or assign a different port:

```bash
# Option A: Run on an alternate port
PORT=5055 python3 scripts/run_local.py

# Option B: Identify and terminate the occupying process (macOS / Linux)
lsof -ti :5050 | xargs kill -9
```

---

## 2. Missing Dependencies / Import Errors

### Symptom
```text
ModuleNotFoundError: No module named 'flask'
# or
ModuleNotFoundError: No module named 'networkx'
```

### Cause
Dependencies were not installed.

### Solution
Install dependencies using editable mode from the repository root:

```bash
pip install -e .
```

---

## 3. Validation Baseline Count Mismatch

### Symptom
```json
{
  "code": "ERR_BASELINE_COUNT_MISMATCH",
  "severity": "ERROR",
  "message": "Live graph counts do not match original baseline counts."
}
```

### Cause
The graph was queried with `mode=baseline` after one or more nodes were deleted during disruption simulation.

### Solution
- **For post-mutation auditing**: Use integrity mode instead (`GET /api/validation?mode=integrity`). Integrity mode verifies structural validity (DAG acyclicity, valid endpoints, correct tier directions) without requiring exact baseline counts.
- **To restore canonical baseline**: Trigger the reset endpoint (`POST /api/reset`) or click **Reset Graph** in the UI.

---

## 4. Node Not Found on Deletion (404)

### Symptom
```json
{
  "error": "Node 'PART-01' not found",
  "status": 404
}
```

### Cause
The target node does not exist in the active graph. If an upstream supplier was previously deleted (e.g. `SUP-01`), `PART-01` was already removed via cascading deletion.

### Solution
Inspect active nodes via `GET /api/graph` or click **Reset** to restore the full graph topology.

---

## 5. Undo Stack Exhausted (400)

### Symptom
```json
{
  "error": "Nothing to undo",
  "status": 400
}
```

### Cause
`POST /api/undo` was called when the undo history stack was empty (e.g. no deletions have occurred or all previous deletions have already been undone).

### Solution
Verify that a deletion has occurred before invoking undo, or inspect the `"can_undo"` flag returned by graph mutation endpoints.

---

## 6. Cyclic Dependency Detected (`ERR_CYCLE_DETECTED`)

### Symptom
```json
{
  "code": "ERR_CYCLE_DETECTED",
  "severity": "CRITICAL",
  "message": "Cycle detected in supply-chain dependency graph: PART-01 -> PROD-01 -> PART-01."
}
```

### Cause
A custom scenario payload or relationship modification introduced a directed cycle, violating the DAG requirement.

### Solution
Inspect the `actual` field in the validation error, which provides the resolved cycle path (e.g. `A -> B -> A`). Remove the circular edge to ensure dependencies strictly flow from Supplier → Part → Product → Order.

