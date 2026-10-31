# TEAM PHOTON — Corrected Individual Task & File Ownership

**Project:** EPAM PHOTON / RE:Flow  
**Repository:** `EPAM-SPRINTS`  
**Current Scope:** Sprint 1 — Supply Chain Graph & Scenario Generator  
**Team Size:** 12 Members

---

## 1. Assignment Rules

This allocation is designed to prevent overlapping responsibilities and unnecessary file assignments.

1. Every member has one clearly defined primary responsibility.
2. The **Owned Files** section identifies the files a member is responsible for working on.
3. The **Reference Files** section contains files to understand only. They are not automatically assigned for modification.
4. No member should modify another member's owned files without coordination.
5. Do not create old or removed files just because they appear in an earlier project plan.
6. Do not start Sprint 2, 3 or 4 implementation under this Sprint 1 assignment.
7. Every code change must preserve existing APIs and pass relevant tests.

---

# 2. Individual Task Allocation

## Member 1 — MISHTI

**Role: Sprint Coordinator & Integration Lead**

**Primary responsibility:** Coordinate all 12 members, monitor progress and ensure that completed modules integrate correctly.

**Owned responsibility:**
- Maintain task completion status.
- Track dependencies between members.
- Organize integration and review meetings.
- Identify blockers and communicate them to the team.
- Verify that Sprint 1 acceptance criteria are covered.
- Collect final updates from all members.

**Files to read:**
- [`README.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/README.md)
- [`docs/team-guide.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/team-guide.md)
- [`docs/architecture.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/architecture.md)
- [`docs/project-structure.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/project-structure.md)

**Files to modify:** No backend implementation files assigned.

**Final deliverable:**
- Sprint progress tracker.
- Integration status.
- Pending issues and blockers list.
- Sprint 1 completion summary.

**Not responsible for:** Writing graph algorithms, changing datasets, implementing validation or writing all project documentation.

---

## Member 2 — DEEP

**Role: Domain Models & API Data Contracts**

**Primary responsibility:** Understand and maintain the project's domain-level representation of nodes, edges and graph-related data contracts.

**Owned Files:**
- [`backend/app/models/nodes.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/nodes.py)
- [`backend/app/models/edges.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/edges.py)
- [`backend/app/models/graph.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/graph.py)
- [`backend/app/schemas/graph.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/schemas/graph.py)
- [`backend/app/schemas/traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/schemas/traversal.py)
- [`backend/app/schemas/validation.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/schemas/validation.py)

**Reference Files:**
- [`backend/app/core/constants.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/core/constants.py)
- [`docs/graph-model.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/graph-model.md)
- [`docs/api-reference.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/api-reference.md)

**Actual tasks:**
1. Understand Supplier, BOM Part, Finished Product and Customer Order models.
2. Understand the three relationship types:
   - `SUPPLIES`
   - `USED_IN`
   - `FULFILLS`
3. Understand the difference between domain models and API schemas.
4. Check consistency between node/edge definitions and API data structures.
5. Report contract inconsistencies to the relevant developer before changing shared definitions.

**Final deliverable:**
- Domain model explanation.
- Node and edge contract reference.
- Any identified model/schema inconsistency report.

**Not responsible for:** Creating the dataset, building the NetworkX graph, implementing traversal or writing validation algorithms.

---

## Member 3 — ANUSHKA

**Role: Canonical Dataset Owner**

**Primary responsibility:** Maintain the actual supply-chain scenario data and ensure that its entities and relationships are consistent.

**Owned File:**
- [`backend/app/data/datasets/scenario_dataset.json`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/data/datasets/scenario_dataset.json)

**Reference Files:**
- [`backend/app/data/schemas/graph_schema.json`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/data/schemas/graph_schema.json)
- [`backend/app/models/nodes.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/nodes.py)
- [`backend/app/models/edges.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/edges.py)
- [`docs/graph-model.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/graph-model.md)

**Actual tasks:**
1. Understand the complete JSON dataset.
2. Verify supplier, part, product and order records.
3. Verify IDs and references between entities.
4. Check whether every relationship follows the approved supply-chain mapping.
5. Identify missing, duplicate or invalid references.
6. Coordinate any dataset changes with Deep and Ansh.

**Sprint 1 baseline to understand:**

| Entity | Expected count |
|---|---:|
| Suppliers | 2 |
| BOM Parts | 5 |
| Finished Products | 2 |
| Customer Orders | 10 |
| Total Nodes | 19 |
| Total Edges | 21 |

**Final deliverable:**
- Verified canonical dataset.
- Dataset consistency report.
- List of any corrected or missing relationships.

**Not responsible for:** Writing the JSON loader, building the graph or implementing graph validation.

---

## Member 4 — ANSH

**Role: NetworkX Graph Builder**

**Primary responsibility:** Convert the loaded scenario data into the project's directed NetworkX graph.

**Owned Files:**
- [`backend/app/graph/builder.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/builder.py)
- [`backend/app/graph/operations.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/operations.py)

**Reference Files:**
- [`backend/app/models/graph.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/graph.py)
- [`backend/app/models/nodes.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/nodes.py)
- [`backend/app/models/edges.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/edges.py)
- [`backend/app/core/constants.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/core/constants.py)
- [`backend/app/data/datasets/scenario_dataset.json`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/data/datasets/scenario_dataset.json)

**Actual tasks:**
1. Understand how the graph is constructed.
2. Understand NetworkX `DiGraph`.
3. Verify how nodes and directed edges are added.
4. Maintain the correct direction of all three relationship types.
5. Ensure graph construction uses the existing model and dataset contracts.
6. Coordinate graph changes with Deep and Anushka.

**Final deliverable:**
- Working graph construction module.
- Explanation of the graph-building process.
- Graph construction test evidence.

**Not responsible for:** Editing the canonical dataset, implementing downstream traversal or owning validation logic.

---

## Member 5 — AADEE

**Role: Dataset Loading & Initialization**

**Primary responsibility:** Handle reading the existing dataset and passing loaded data into the graph initialization flow.

**Owned File:**
- [`backend/app/data/loader.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/data/loader.py)

**Reference Files:**
- [`backend/app/data/datasets/scenario_dataset.json`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/data/datasets/scenario_dataset.json)
- [`backend/app/core/config.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/core/config.py)
- [`backend/app/services/graph_service.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/services/graph_service.py)

**Actual tasks:**
1. Understand how the JSON dataset is loaded.
2. Understand how the dataset path is resolved.
3. Check file-not-found and invalid-data handling.
4. Understand the loader's output format.
5. Verify that the loaded data is passed correctly into the existing graph initialization flow.
6. Report loading-related errors without changing graph-building logic.

**Final deliverable:**
- Reliable dataset-loading flow.
- Loader error-handling verification.
- Explanation of dataset-to-graph handoff.

**Not responsible for:** Maintaining dataset relationships, building the graph or creating a new normalizer/repository architecture.

---

## Member 6 — PREETAM

**Role: Downstream Traversal & Dependency Tracing**

**Primary responsibility:** Implement and maintain the traversal logic used to identify downstream dependencies from a selected supplier or graph node.

**Owned File:**
- [`backend/app/graph/traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/traversal.py)

**Reference Files:**
- [`backend/app/models/graph.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/graph.py)
- [`backend/app/services/graph_service.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/services/graph_service.py)
- [`backend/app/api/routes/traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/api/routes/traversal.py)
- [`backend/tests/unit/test_traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_traversal.py)

**Actual tasks:**
1. Understand the existing traversal algorithm.
2. Understand BFS and directed graph traversal.
3. Trace downstream parts, products and customer orders.
4. Handle valid starting nodes and relevant invalid/isolated-node cases.
5. Ensure the traversal result follows the existing API contract.
6. Coordinate traversal changes with Ansh and Shanu.

**Final deliverable:**
- Correct downstream traversal implementation.
- Example supplier dependency trace.
- Traversal test results.

**Not responsible for:** Building the graph, owning API routes or running the complete project benchmark suite.

---

## Member 7 — SONAL

**Role: Supply-Chain Mapping Verification**

**Primary responsibility:** Independently verify whether the built graph represents the approved supply-chain scenario correctly.

**Owned responsibility:**
- Mapping verification.
- Relationship consistency review.
- Verification report.

**Files to read:**
- [`backend/app/data/datasets/scenario_dataset.json`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/data/datasets/scenario_dataset.json)
- [`backend/app/graph/builder.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/builder.py)
- [`backend/app/models/nodes.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/nodes.py)
- [`backend/app/models/edges.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/models/edges.py)
- [`docs/graph-model.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/graph-model.md)

**Generated report to inspect:**
- `backend/reports/graph_validation_report.json`

**Actual tasks:**
1. Verify which supplier supplies which BOM part.
2. Verify which BOM part belongs to which finished product.
3. Verify which finished product fulfils which customer order.
4. Compare the actual graph mapping against the approved scenario.
5. Identify missing, unexpected or incorrectly directed relationships.
6. Report findings to Anushka and Ansh.

**Final deliverable:**
- Mapping verification report.
- Correct/incorrect relationship list.
- Evidence of any mismatch found.

**Not responsible for:** Writing the canonical dataset, changing the graph builder or implementing the validation subsystem.

---

## Member 8 — SOUMYA

**Role: Graph Validation Module**

**Primary responsibility:** Maintain the validation subsystem that checks graph nodes, edges and cycles.

**Owned Files:**
- [`backend/app/validation/nodes.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/nodes.py)
- [`backend/app/validation/edges.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/edges.py)
- [`backend/app/validation/cycles.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/cycles.py)
- [`backend/app/validation/validator.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/validator.py)

**Reference Files:**
- [`backend/app/validation/models.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/models.py)
- [`backend/app/validation/reporting.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/reporting.py)
- [`backend/app/services/validation_service.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/services/validation_service.py)
- [`backend/app/api/routes/validation.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/api/routes/validation.py)
- [`backend/tests/unit/test_validation.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_validation.py)

**Actual tasks:**
1. Understand node validation.
2. Verify unique IDs and required node attributes.
3. Understand edge source/target reference checks.
4. Verify valid relationship types and directions.
5. Understand cycle detection and DAG validation.
6. Ensure the validation orchestrator collects and reports errors correctly.
7. Coordinate validation changes with Deep and Shanu.

**Final deliverable:**
- Working graph validation module.
- Validation error examples.
- Validation test results.

**Not responsible for:** Independently verifying the complete business mapping, maintaining the dataset or writing the full test suite.

---

## Member 9 — DIVYANSHU

**Role: Edge-Case Analysis & Algorithm Complexity**

**Primary responsibility:** Identify boundary conditions and analyze the behaviour and complexity of existing graph and traversal algorithms.

**Owned responsibility:**
- Edge-case analysis.
- Complexity analysis.
- Additional test-case recommendations.

**Files to read:**
- [`backend/app/graph/traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/traversal.py)
- [`backend/app/graph/builder.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/builder.py)
- [`backend/app/validation/cycles.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/validation/cycles.py)
- [`backend/tests/unit/test_edge_cases.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_edge_cases.py)
- [`backend/tests/unit/test_traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_traversal.py)

**Actual tasks:**
1. Identify missing-node scenarios.
2. Identify isolated-node scenarios.
3. Examine duplicate node IDs and invalid edges.
4. Examine cyclic graph scenarios.
5. Analyze BFS time and space complexity ($O(V + E)$).
6. Identify how graph size can affect performance.
7. Share additional test cases with Shanu.

**Final deliverable:**
- Edge-case analysis document.
- Complexity explanation.
- Recommended additional test cases.

**Not responsible for:** Owning the testing framework, rewriting traversal, implementing validation or running the complete regression suite.

---

## Member 10 — SHANU

**Role: Testing & Regression**

**Primary responsibility:** Verify that existing functionality continues to work after changes made by developers.

**Owned responsibility:**
- Test suite maintenance.
- Regression verification.
- Integration test execution.

**Files to read:**
- [`backend/tests/conftest.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/conftest.py)
- [`backend/tests/fixtures/sample_scenario.json`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/fixtures/sample_scenario.json)
- [`backend/tests/unit/test_api_schemas.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_api_schemas.py)
- [`backend/tests/unit/test_domain_models.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_domain_models.py)
- [`backend/tests/unit/test_graph.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_graph.py)
- [`backend/tests/unit/test_traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_traversal.py)
- [`backend/tests/unit/test_validation.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/unit/test_validation.py)
- [`backend/tests/integration/test_api.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/tests/integration/test_api.py)

**Actual tasks:**
1. Understand existing test fixtures.
2. Verify domain model and schema tests.
3. Verify graph construction and traversal tests.
4. Verify validation tests.
5. Verify API integration tests.
6. Add regression tests for approved code changes.
7. Run the full test suite and report failures.

**Commands to understand and execute:**

```bash
python3 -m pytest backend/tests/ -v
```

```bash
python3 -m ruff check backend/ scripts/
```

```bash
python3 scripts/validate_graph.py
```

**Final deliverable:**
- Test execution report.
- Failed/passed test summary.
- Regression issue list.

**Not responsible for:** Developing every backend module or independently owning the complexity analysis.

---

## Member 11 — KANAK

**Role: Performance Benchmarking**

**Primary responsibility:** Measure graph/traversal performance using the existing benchmarking implementation.

**Owned Files:**
- [`backend/app/services/benchmark_service.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/services/benchmark_service.py)
- [`scripts/run_benchmarks.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/scripts/run_benchmarks.py)

**Reference Files:**
- [`backend/app/graph/traversal.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/graph/traversal.py)
- [`backend/app/api/routes/benchmarks.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/api/routes/benchmarks.py)
- [`docs/benchmarking.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/benchmarking.md)
- `backend/reports/graph_benchmark_report.json`

**Actual tasks:**
1. Understand how benchmark execution works.
2. Understand `time.perf_counter_ns()`.
3. Understand warm-up runs and repeated measurements.
4. Calculate and interpret mean, median and percentile values.
5. Compare traversal results against the Sprint 1 performance target (10.0 ms SLA).
6. Record benchmark methodology and results.
7. Coordinate performance-related issues with Preetam.

**Final deliverable:**
- Benchmark execution results.
- Performance report.
- Comparison against the 10 ms acceptance target.

**Not responsible for:** Changing traversal algorithms without coordination, owning graph construction or writing API documentation.

---

## Member 12 — SUMIT

**Role: Project Documentation & Demo Instructions**

**Primary responsibility:** Keep the project documentation accurate and prepare clear instructions for demonstrating the existing Sprint 1 application.

**Owned Files:**
- [`README.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/README.md)
- [`docs/running-locally.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/running-locally.md)
- [`docs/api-reference.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/api-reference.md)
- [`docs/frontend.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/frontend.md)

**Reference Files:**
- [`docs/architecture.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/architecture.md)
- [`docs/graph-model.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/graph-model.md)
- [`docs/testing.md`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/testing.md)
- [`render.yaml`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/render.yaml)
- [`backend/app/static/sprint-1-demo.html`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/static/sprint-1-demo.html)
- [`backend/app/static/js/sprint-1-demo.js`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/static/js/sprint-1-demo.js)
- [`backend/app/static/css/sprint-1-demo.css`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/static/css/sprint-1-demo.css)

**Actual tasks:**
1. Maintain the project overview and setup instructions.
2. Document the actual API endpoints and their request/response formats.
3. Document how the frontend communicates with the backend.
4. Prepare local execution instructions.
5. Document the existing demo workflow.
6. Verify documentation against actual implementation before publishing changes.

**Final deliverable:**
- Updated README and assigned documentation.
- API reference.
- Local run and demo instructions.

**Not responsible for:** Implementing backend APIs, changing frontend functionality or independently modifying deployment configuration.

---

# 3. Clear Ownership Matrix

| Member | Primary ownership | Main deliverable |
|---|---|---|
| Mishti | Coordination | Sprint tracker and integration status |
| Deep | Models and schemas | Domain/API contracts |
| Anushka | Scenario dataset | Verified dataset |
| Ansh | Graph builder | NetworkX graph construction |
| Aadee | Data loader | Dataset loading |
| Preetam | Traversal | Downstream dependency tracing |
| Sonal | Mapping verification | Mapping report |
| Soumya | Validation | Graph validation |
| Divyanshu | Edge-case analysis | Edge cases and complexity report |
| Shanu | Testing | Regression and test report |
| Kanak | Benchmarking | Performance report |
| Sumit | Documentation | README, API and demo guide |

---

# 4. Actual Development Flow

The following is the logical dependency flow. It does not mean every member must edit the same files.

1. **Anushka** maintains the canonical dataset.
2. **Aadee** loads the dataset.
3. **Deep** maintains the domain contracts used by the system.
4. **Ansh** constructs the NetworkX graph.
5. **Sonal** independently checks the business mapping.
6. **Soumya** validates graph structure and relationships.
7. **Preetam** handles downstream traversal.
8. **Divyanshu** identifies edge cases and analyzes complexity.
9. **Shanu** verifies the complete test suite and regression behaviour.
10. **Kanak** measures traversal performance.
11. **Sumit** documents the verified implementation and demo.
12. **Mishti** coordinates integration and tracks Sprint 1 completion.

---

# 5. File Ownership Rules

To avoid confusion during development:

- `scenario_dataset.json` — Anushka owns changes.
- `loader.py` — Aadee owns changes.
- `models/` and `schemas/` — Deep owns changes.
- `graph/builder.py` and `graph/operations.py` — Ansh owns changes.
- `graph/traversal.py` — Preetam owns changes.
- `validation/` implementation — Soumya owns changes.
- Test suite — Shanu owns test maintenance; developers can add tests for their own changes after coordination.
- Benchmark implementation — Kanak owns changes.
- Assigned documentation — Sumit owns changes.
- Mapping verification — Sonal reviews and reports; she does not independently rewrite the dataset or graph builder.
- Edge-case analysis — Divyanshu recommends and documents cases; Shanu integrates them into the test suite.
- Coordination — Mishti tracks work; she does not become the owner of every module.

**Shared-file rule:** If a change affects another member's owned file, discuss it with that owner first. One file should not have two independent owners.

---

# 6. What Every Member Must Submit

Every member must provide:

1. A short explanation of their assigned module.
2. A list of the functions/classes they studied or changed.
3. Input → Processing → Output explanation.
4. Dependencies on other modules.
5. Work completed and pending issues.
6. Test or verification evidence wherever applicable.

**Important:** Reading a reference file does not mean that file has been assigned to you for development. Your main responsibility is only the one explicitly listed under your role.

---

## Final Objective

Every member should have a clearly separated area of responsibility. The purpose is not to make all 12 members read the entire repository. The purpose is to ensure that each member understands and contributes to one specific part of PHOTON without duplicating another member's work.
