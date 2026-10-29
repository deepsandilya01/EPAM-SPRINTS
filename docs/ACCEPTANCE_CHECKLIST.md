# Team Photon — Acceptance Criteria Checklist & Traceability Matrix

## 1. Traceability Matrix Overview

This document provides a verifiable, evidence-backed evaluation of the **Team Photon** Sprint 1 graph structure validation module, downstream traversal engine, and API integration.

### Status Vocabulary
- **`PASS`**: Formally tested, executed, and verified against repository source code and test outputs.
- **`FAIL`**: Executed and failed to meet acceptance threshold.
- **`NOT RUN`**: Verification procedure defined but not yet executed.
- **`BLOCKED`**: Cannot be verified due to external dependency or preceding failure.
- **`N/A`**: Non-applicable to Sprint 1 scope (marked as future enhancement).

---

## 2. Core Acceptance Criteria Matrix

| ID | Requirement Description | Verification Method | Executed Evidence & Artifacts | Status | Technical Notes |
|---|---|---|---|:---:|---|
| **AC-01** | **Expected Node-Type Counts**<br>Suppliers: 2<br>Parts: 5<br>Products: 2<br>Orders: 10 | Automated unit tests asserting exact category lengths in raw JSON & NetworkX graph. | `tests/test_node_counts.py::test_exact_node_category_counts`<br>`tests/test_node_counts.py::test_canonical_graph_node_counts` | **PASS** | Validated against `photon_sprint1_graph_data.json`. All 4 categories match baseline specification. |
| **AC-02** | **Expected Node/Edge Totals & Relationships**<br>Total nodes: 19<br>Total edges: 21<br>(`supplies`: 6, `used_in`: 5, `fulfills`: 10) | Automated edge counting assertions and `/api/graph` payload audit. | `tests/test_edge_integrity.py::test_canonical_edge_counts`<br>`tests/test_edge_integrity.py::test_exact_edge_category_counts`<br>`tests/test_api_integration.py::test_api_graph_returns_canonical_counts` | **PASS** | `validate_raw_graph_data()` verifies `BASELINE_NODE_COUNTS` and `BASELINE_EDGE_COUNTS`. |
| **AC-03** | **Unique Node IDs & Valid Edge References**<br>No duplicate IDs; pre-construction check prevents NetworkX overwrite; no dangling edge references. | Pre-construction raw JSON audit and edge endpoint foreign-key verification. | `tests/test_duplicate_ids.py::test_duplicate_node_id_within_same_category`<br>`tests/test_duplicate_ids.py::test_networkx_silent_collapse_proof`<br>`tests/test_edge_integrity.py::test_nonexistent_source_reference_detected` | **PASS** | Proves that `ERR_DUPLICATE_NODE_ID` triggers before `nx.DiGraph` silently collapses duplicate nodes. |
| **AC-04** | **Edge Direction & Valid Schema Relationships**<br>Strict flow: `Supplier -> Part -> Product -> Order`. Inverted or tier-skipping edges rejected. | Direction rules audit against `direction_rules` policy map. | `tests/test_edge_direction.py::test_all_canonical_edges_follow_valid_direction`<br>`tests/test_edge_direction.py::test_reversed_supplies_edge_detected`<br>`tests/test_edge_direction.py::test_invalid_tier_jump_supplies_to_product` | **PASS** | Trapping reversed edges and tier jumping (`part -> order`) with error code `ERR_INVALID_EDGE_DIRECTION`. |
| **AC-05** | **Verified Supplier Reachability**<br>`SUP-01`: exactly 10 downstream descendants.<br>`SUP-02`: exactly 15 downstream descendants. | Deterministic BFS reachability set assertion using `nx.descendants`. | `tests/test_tracing.py::test_exact_supplier_01_reachability`<br>`tests/test_tracing.py::test_exact_supplier_02_reachability`<br>`tests/test_api_integration.py::test_api_downstream_reachability_integration` | **PASS** | `SUP-01` reaches 3 parts, 1 product, 6 orders = 10.<br>`SUP-02` reaches 3 parts, 2 products, 10 orders = 15. |
| **AC-06** | **Unknown Supplier & Malformed Data Handling**<br>Graceful handling of missing keys, corrupted payloads, unknown IDs, and negative stock without server crash. | Parametrized fuzzing tests and edge-case payload validation. | `tests/test_malformed_data.py::test_non_dict_top_level_payload`<br>`tests/test_missing_entities.py::test_negative_part_stock_detected`<br>`tests/test_tracing.py::test_unknown_supplier_reachability_handled_gracefully`<br>`tests/test_api_integration.py::test_api_benchmark_tracing_unknown_node` | **PASS** | Returns structured error reports (`ValidationError`) and proper HTTP status codes (`400`, `404`, `422`). |
| **AC-07** | **Conditional DAG / Cycle Validation**<br>Canonical graph verified acyclic. Configurable policy (`REQUIRE_DAG`, `ALLOW_CYCLES`, `UNSPECIFIED`). | Synthetic cyclic graph injection and policy verification tests. | `tests/test_acyclicity.py::test_canonical_graph_is_acyclic`<br>`tests/test_acyclicity.py::test_cyclic_graph_fails_when_dag_required`<br>`tests/test_acyclicity.py::test_cyclic_graph_permitted_when_policy_allows_cycles`<br>`tests/test_acyclicity.py::test_unspecified_acyclicity_policy_reports_warning` | **PASS** | Canonical graph is verified acyclic (`is_directed_acyclic_graph == True`). Policy switch tested and working. |
| **AC-08** | **Downstream Traversal Latency Benchmark (< 10 ms)**<br>$p95$ traversal latency across `SUP-01` and `SUP-02` must be strictly $\le 10.0\text{ ms}$. | High-resolution monotonic timer (`time.perf_counter_ns()`), 50 warmup + 1000 measured runs per node (2,000 runs). | CLI Benchmark Output & Report:<br>`backend/reports/graph_benchmark_report.json`<br>- Min: **0.0103 ms**<br>- Mean: **0.0188 ms**<br>- Median: **0.0140 ms**<br>- **$p95$: 0.0329 ms** (Target: $< 10.0\text{ ms}$)<br>- Max: **0.1585 ms** | **PASS** | Measured traversal latency is over **300 times faster** than the 10.0 ms ceiling. |
| **AC-09** | **Reproducible Setup, Testing & Documentation**<br>Clean virtual environment install, all 73 tests passing, and documentation written into repository. | Pytest full suite run and repository file verification. | Command: `pytest tests/ -v`<br>**Result**: `73 passed in 0.83s`<br>**Coverage**: `91%` across `graph_validation`<br>**Docs**: 5 guides created in `docs/` | **PASS** | Verified on Windows 11, Python 3.12.14, NetworkX 3.4.2. |

---

## 3. Optional Enhancements & Future Scope (Sprint 2+)

| Enhancement ID | Scope Description | Planned Approach | Status | Justification / Notes |
|---|---|---|:---:|---|
| **ENH-01** | **Native UI Validation Dashboard** | Slide-out panel in `static/index.html` displaying live `/api/validation` checks and triggerable benchmark widget. | **PROPOSED** | Backend endpoints (`/api/validation`, `/api/benchmark/tracing`) and contract tests are 100% verified. Frontend UI extension is documented in `FRONTEND_VALIDATION_GUIDE.md`. |
| **ENH-02** | **Reverse Logistics Cyclic Modeling** | Support return packaging, defect exchanges, or material recycling loops (`Order -> Supplier`). | **N/A (Sprint 1)** | Current Sprint 1 domain specification defines a strict unidirectional forward-logistics DAG. Policy `AcyclicityPolicy.ALLOW_CYCLES` is ready for this future extension. |
| **ENH-03** | **Automated Capacity Feasibility Solver** | Validate that supplier capacity ($\text{units/day}$) $\ge \sum \text{daily consumption}$ of dependent parts. | **N/A (Sprint 1)** | Beyond Sprint 1 structural topology scope; capacity attributes are preserved in the schema for future linear programming solvers. |

---

## 4. Verification Command Summary

All acceptance criteria can be reproduced using the following commands:

```powershell
# 1. Run all 73 automated tests
pytest tests/ -v

# 2. Run with coverage measurement
pytest tests/ --cov=graph_validation --cov-report=term-missing

# 3. Run the statistical downstream tracing benchmark
python -m benchmarks.benchmark_tracing

# 4. Start the live application
python app.py
```

