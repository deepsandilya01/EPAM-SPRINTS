# Team Photon — Sprint 1 BOM & Customer-Order Mapping (Sonal)

**Status:** Implementation aligned to the proposed `photon Sprint1 Dataset.xlsx` baseline. The workbook remains the proposed canonical source until the team confirms it.

## Purpose

This module builds and validates the Sprint 1 directed dependency graph:

`Supplier —SUPPLIES→ BOM Part —USED_IN→ Finished Product —FULFILLS→ Customer Order`

It preserves source attributes and verifies supplier reachability. Reachability means a dependency path exists; it does **not** prove that an order will be disrupted, delayed, or unfulfillable.

## Dataset contract

- 2 suppliers, 5 parts, 2 finished products, 10 customer orders = **19 nodes**.
- 6 `SUPPLIES`, 5 `USED_IN`, 10 `FULFILLS` relationships = **21 directed edges**.
- The shared `PART-05` is supplied by both `SUP-01` and `SUP-02` and is used by `PROD-01` (quantity 2 per product).
- `SUP-02` therefore reaches both products and all 10 orders through `PART-05 → PROD-01` and its direct dependencies to `PROD-02`.
- The Excel field `quantity_per_unit` is normalized to graph edge attribute `quantity_per_product`.
- Order `deadline` remains an ISO date string (`YYYY-MM-DD`), not `deadline_hours`.

## Files

- `scenario.json`: normalized scenario consumed by the program; includes all 19 nodes and 21 relationships.
- `data/*.csv`: source-table exports from the workbook for review and traceability.
- `expected_results.json`: supplier traversal expectations from the workbook's `Expected_Results` sheet.
- `main.py`: loader, contract validator, graph builder, traversal, expected-result verification, and console report.
- `tests/test_mapping.py`: positive and negative automated tests.

## Setup and run

Python 3.10+ recommended.

```bash
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
```

Expected console summary includes `19 nodes, 21 directed edges`, edge counts `SUPPLIES=6, USED_IN=5, FULFILLS=10`, and `Expected-results verification: PASS`.

## Validation performed for this package

The implementation validates node counts and kinds, non-empty and globally unique IDs, required attributes, edge endpoints, relation labels and direction, required numeric edge attributes, order product references, ISO dates, duplicate relationships, graph acyclicity, and expected reachability. The test suite includes exact relationship mapping and malformed-input cases.

## Sprint 1 scope boundary

Included: scenario loading, BOM/order mapping, dependency graph creation, schema validation, supplier traversal, tests, and documentation.

Not included: shortage prediction, ripple-effect calculations beyond reachability, inventory coverage calculations, recovery optimization, OR-Tools, live ERP feeds, or dashboard/control-tower UI.

## Handoff / confirmation needed

1. Team confirms `photon Sprint1 Dataset.xlsx` as canonical.
2. Keep `scenario.json`, CSV exports, `expected_results.json`, code, tests, and mapping guide synchronized if the workbook changes.
3. Run the commands above after any data change and attach actual console/test output as Sprint 1 evidence.
