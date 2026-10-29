# Team Photon — Acceptance Test Report (EPAM Sprint 1 Final Submission)

**Project:** Proactive Supply-Chain Decision, Ripple & Recovery Intelligence System  
**Evaluation Target:** EPAM Sprint 1 Final Technical Gate  
**Execution Environment:** macOS Darwin 24.6.0 (arm64), Python 3.9.6, Flask 3.1.3, NetworkX 3.2.1, Pytest 8.4.2  
**Date of Audit:** October 2026  
**Auditor:** Senior Software Engineer, QA Engineer & Deployment Specialist  

---

## 1. Executive Summary

This report maps the actual EPAM acceptance criteria to concrete, executed test suites, negative failure test cases, API integration tests, and benchmark performance metrics. 

Every claim in this report has been validated by executing live commands against the codebase.

- **Total Automated Tests Executed:** 95
- **Passed:** 95
- **Failed:** 0
- **Skipped:** 0
- **Test Execution Time:** 0.14 seconds
- **Code Coverage:** 88% across backend codebase (90% validator, 100% schema, 94% tracing, 93% Flask app)
- **Code Quality / Linting:** 0 errors (`ruff check .` clean)
- **Benchmark Traversal SLA ($p_{95}$):** $0.0042\text{ ms} \ll 10.0\text{ ms}$ (PASS)

---

## 2. EPAM Acceptance Criteria Traceability Matrix

| Requirement | Test or evidence | Expected result | Actual result | Status |
|---|---|---|---|:---:|
| **AC-01: Baseline Node-Type Counts**<br>Suppliers: 2, Parts: 5, Products: 2, Orders: 10. | `backend/tests/test_node_counts.py::test_canonical_graph_node_counts`<br>`backend/tests/test_node_counts.py::test_exact_node_category_counts` | Exact category counts match baseline specification in JSON and NetworkX. | All 4 categories match baseline specification: 2 suppliers, 5 parts, 2 products, 10 orders. | **PASS** |
| **AC-02: Total Entities & Edge Types**<br>19 total nodes, 21 total edges (`supplies`: 6, `used_in`: 5, `fulfills`: 10). | `backend/tests/test_edge_integrity.py::test_canonical_edge_counts`<br>`backend/tests/test_edge_integrity.py::test_exact_edge_category_counts`<br>`backend/tests/test_api_integration.py::test_api_graph_returns_canonical_counts` | Graph has exactly 19 nodes and 21 directed edges. | Verified 19 nodes and 21 edges in both raw file and NetworkX DiGraph. | **PASS** |
| **AC-03: Unique Node Identifiers & Foreign Key References**<br>No duplicate node IDs across or within categories. Edge sources/targets must exist. | `backend/tests/test_duplicate_ids.py::test_duplicate_node_id_within_same_category`<br>`backend/tests/test_duplicate_ids.py::test_duplicate_node_id_across_different_categories`<br>`backend/tests/test_duplicate_ids.py::test_networkx_silent_collapse_proof` | Duplicate node IDs and dangling edges caught before graph creation. | Validator detects duplicates (`ERR_DUPLICATE_NODE_ID`) before NetworkX silent collapse. | **PASS** |
| **AC-04: 4-Tier Directional Progression**<br>Strict edge flow: `Supplier -> Part -> Product -> Order`. Inverted or tier-skipping edges prohibited. | `backend/tests/test_edge_direction.py::test_all_canonical_edges_follow_valid_direction`<br>`backend/tests/test_edge_direction.py::test_reversed_supplies_edge_detected`<br>`backend/tests/test_edge_direction.py::test_invalid_tier_jump_supplies_to_product` | Non-canonical edge directions rejected with informative error codes. | Inverted edges and tier skips caught with `ERR_INVALID_EDGE_DIRECTION`. | **PASS** |
| **AC-05: Verified Supplier Reachability**<br>`SUP-01`: 10 downstream descendants.<br>`SUP-02`: 15 downstream descendants. | `backend/tests/test_tracing.py::test_exact_supplier_01_reachability`<br>`backend/tests/test_tracing.py::test_exact_supplier_02_reachability`<br>`backend/tests/test_api_integration.py::test_api_downstream_reachability_integration` | BFS reachability returns exact descendant sets matching supply chain topology. | `SUP-01` reaches 10 nodes (3 parts, 1 product, 6 orders). `SUP-02` reaches 15 nodes (3 parts, 2 products, 10 orders). | **PASS** |
| **AC-06: Malformed Input & Defensive Parsing**<br>Non-dictionary payloads, wrong data types, empty graphs, and negative quantities handled safely. | `backend/tests/test_malformed_data.py::test_non_dict_top_level_payload`<br>`backend/tests/test_malformed_data.py::test_empty_graph_payload`<br>`backend/tests/test_missing_entities.py::test_negative_part_stock_detected` | Graceful failure returning structured `ValidationReport` without unhandled crashes. | Rejection with `ERR_INVALID_TOP_LEVEL_TYPE`, `ERR_MISSING_NODES_KEY`, and `ERR_INVALID_PART_NUMERIC_FIELD`. | **PASS** |
| **AC-07: Configurable Acyclicity / DAG Enforcement**<br>Canonical graph must be a strict DAG (`is_directed_acyclic_graph == True`). Policy switchable. | `backend/tests/test_acyclicity.py::test_canonical_graph_is_acyclic`<br>`backend/tests/test_acyclicity.py::test_cyclic_graph_fails_when_dag_required`<br>`backend/tests/test_acyclicity.py::test_cyclic_graph_permitted_when_policy_allows_cycles` | Graph verified acyclic; synthetic cycles rejected under `REQUIRE_DAG` policy. | Baseline graph is 100% acyclic. Cycle injection triggers `ERR_CYCLE_DETECTED`. Policy switch operational. | **PASS** |
| **AC-08: Traversal SLA Benchmark (< 10 ms)**<br>$p_{95}$ downstream reachability latency must be $< 10.0\text{ ms}$. | High-resolution monotonic timer benchmark (`backend/benchmarks/benchmark_tracing.py`), 50 warmup + 1,000 measured runs per supplier (2,000 runs total). | $p_{95}$ traversal latency strictly below 10.0 ms. | **Actual $p_{95}$: 0.0042 ms** ($> 2,000\times$ faster than the 10 ms ceiling). Report generated at `backend/reports/graph_benchmark_report.json`. | **PASS** |
| **AC-09: Live Web Application & REST Contract**<br>Flask web server serves D3.js frontend and exposes complete REST API. | Live execution on port 5050; curl verification of `GET /`, `GET /api/graph`, `GET /api/downstream/<id>`, `GET /api/impact/<id>`, `DELETE /api/node/<id>`, `POST /api/undo`, `POST /api/reset`. | HTTP 200/400/404 responses matching API schema; UI visualization rendered. | Root serves HTML (200), `/api/graph` returns 19 nodes & 21 edges, cascade deletion, undo, and reset verified live. | **PASS** |
| **AC-10: Failure & Rejection Negative Testing (Phase 5)**<br>Comprehensive error trapping for nonexistent nodes, invalid query params, empty undo stack, unsupported HTTP methods, and malformed inputs. | `backend/tests/test_negative_scenarios.py` (18 dedicated negative test cases covering edge cases). | Nonexistent nodes return 404; empty undo returns 400; bad query params return 400; bad methods return 405 JSON. Graph remains uncorrupted. | Verified: 404 on nonexistent nodes, 400 on empty undo stack, 400 on negative/string threshold, 405 JSON on invalid methods. Baseline graph remains 100% consistent. | **PASS** |
| **AC-11: Vercel Serverless Function Compatibility**<br>Project runnable on Vercel without architecture overhaul. WSGI adapter and route mapping. | `api/index.py` serverless adapter; `vercel.json` rewrite configuration; `test_vercel_serverless_entrypoint`. | Vercel Python runtime discovers `app` and serves routes without import or path resolution errors. | Verified locally: `from api.index import app` tested via test client; dataset resolved via portable paths; zero broken imports. | **PASS** |
| **AC-12: Serverless State Persistence & Cold-Start Analysis**<br>Verify in-memory state persistence across warm requests and cold-start resets. | `backend/tests/test_serverless_cold_start.py` (`test_warm_instance_sequential_requests`, `test_cold_start_simulation_demonstrates_in_memory_reset`, `test_cross_instance_concurrent_isolation`). | Warm instances retain mutations; cold starts cleanly reset to canonical baseline dataset without corrupted state. | Verified: Warm sequential requests persist state; cold starts reset safely to 19 nodes; concurrent container instances are strictly isolated. | **PASS** |

---

## 3. Negative Testing Breakdown (Phase 5 Mandatory Verification)

| Test Identifier | Category | Input / Scenario | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|:---:|
| `test_missing_required_entity_fields` | Schema Validation | Part missing required `'id'` field | Rejection (`valid=False`) | `ERR_MISSING_NODE_ID` detected | **PASS** |
| `test_edge_referencing_nonexistent_target_node` | Foreign Key Integrity | Edge to `"GHOST-NODE-999"` | Rejection (`valid=False`) | `ERR_NONEXISTENT_TARGET_NODE` detected | **PASS** |
| `test_edge_referencing_nonexistent_source_node` | Foreign Key Integrity | Edge from `"GHOST-SUPPLIER-00"` | Rejection (`valid=False`) | `ERR_NONEXISTENT_SOURCE_NODE` detected | **PASS** |
| `test_self_loop_rejection` | Topology Rule | Edge `PART-01 -> PART-01` | Cycle detected, rejected | `ERR_CYCLE_DETECTED` | **PASS** |
| `test_reverse_tier_progression_rejected` | Hierarchy Progression | Backward edge `ORD-01 -> SUP-01` | Hierarchy violation | `ERR_INVALID_EDGE_DIRECTION` | **PASS** |
| `test_api_downstream_nonexistent_node` | REST Endpoint | `GET /api/downstream/UNKNOWN-999` | HTTP 404 with error JSON | HTTP 404 `{"error": "Node UNKNOWN-999 not found"}` | **PASS** |
| `test_api_impact_nonexistent_node` | REST Endpoint | `GET /api/impact/UNKNOWN-999` | HTTP 404 with error JSON | HTTP 404 `{"error": "Node UNKNOWN-999 not found"}` | **PASS** |
| `test_api_delete_nonexistent_node` | Mutation Endpoint | `DELETE /api/node/UNKNOWN-999` | HTTP 404 with error JSON | HTTP 404 `{"error": "Node UNKNOWN-999 not found"}` | **PASS** |
| `test_api_undo_empty_stack` | State Management | `POST /api/undo` on empty stack | HTTP 400 with error JSON | HTTP 400 `{"error": "Nothing to undo"}` | **PASS** |
| `test_api_validation_invalid_mode_param` | Input Sanitization | `GET /api/validation?mode=ILLEGAL` | HTTP 400 with error JSON | HTTP 400 `{"error": "Invalid mode 'ILLEGAL'..."}` | **PASS** |
| `test_api_benchmark_invalid_threshold` | Input Sanitization | `GET /api/benchmark/tracing?threshold_ms=abc` and `?threshold_ms=-1` | HTTP 400 with error JSON | HTTP 400 `{"error": "Invalid threshold_ms value..."}` | **PASS** |
| `test_api_unsupported_http_methods` | HTTP Protocol | `POST /api/graph`, `GET /api/undo` | HTTP 405 Method Not Allowed | HTTP 405 `{"error": "Method not allowed", "status": 405}` | **PASS** |
| `test_api_nonexistent_route_404_json` | Error Routing | `GET /api/nonexistent/route` | JSON 404 (not HTML) | HTTP 404 `{"error": "Resource not found", "status": 404}` | **PASS** |
| `test_graph_consistency_after_rejected_operations` | Data Safety | Sequence of failed operations | Graph invariant preserved | Graph remains 19 nodes, 21 edges, 100% valid | **PASS** |
| `test_repeated_undo_operations` | State Invariant | Multi-delete, multi-undo exhaustion | Stack exhaust returns 400, baseline intact | Restores exact nodes in LIFO order; 3rd undo returns 400 | **PASS** |
| `test_trace_leaf_node_has_zero_downstream` | Graph Traversal | Trace starting at `ORD-01` | 0 descendants, $O(1)$ fast | Visited count: 0, $p_{95} \le 10\text{ ms}$ | **PASS** |
| `test_trace_nonexistent_node` | Graph Traversal | Trace starting at `SUP-999` | `source_exists=False` | Visited count: 0, status: PASS | **PASS** |

---

## 4. Verification Reproducibility Commands

To reproduce the exact verification results on any Unix/macOS or Linux system:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run static code analysis
ruff check .

# 3. Run complete automated test suite with coverage
pytest -v --cov=backend --cov-report=term-missing

# 4. Run the high-resolution downstream tracing benchmark
python -m backend.benchmarks.benchmark_tracing

# 5. Start the live application
python backend/app.py
```
