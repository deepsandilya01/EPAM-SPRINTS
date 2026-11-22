# Team Photon — Sprint 2 | Anushka's Feature 4

## Feature
**Stockout Predictor & 2-Order Matcher** — Predictive intelligence layer detecting the zero-stock inflection hour ($T_{\text{stockout}} = 8.0\text{h}$) and matching failing customer delivery commitments (`ORD-01`, `ORD-02`).

## Acceptance Criteria Ownership
- **AC-06**: Exactly 2 customer orders identified (Benchmark Anchor: `ORD-01`, `ORD-02`)
- **AC-08**: Stockout timestamp predicted (`T_stockout == 8.0h`)

## Files in this contribution
- `backend/app/models/stockout.py` — `BreachedOrder` and `StockoutPredictionResult` Pydantic models.
- `backend/app/simulation/stockout.py` — `predict_stockout_and_orders()` core predictive algorithm.
- `backend/app/models/__init__.py` — Clean exports for `BreachedOrder` and `StockoutPredictionResult`.
- `backend/tests/unit/test_stockout.py` — Acceptance tests verifying AC-06, AC-08, edge cases, and missing deadlines.

## Official Benchmark
```python
result = predict_stockout_and_orders(
    depletion=depletion,  # From Sonal's simulate_inventory_depletion()
    impact=impact,        # From Aadee's propagate_ripple_effect()
    order_deadlines=order_deadlines, # From Kanak's scenario_dataset.json
)
```

Expected:
- `result.stockout_hour == 8.0` (AC-08)
- `result.total_breached == 2` (AC-06)
- `[o.order_id for o in result.breached_orders] == ["ORD-01", "ORD-02"]`
- `result.no_stockout is False`

## Run Tests
Run from the repository root:

```bash
pytest -q backend/tests/unit/test_stockout.py
```

## Integration Contract
- **Inputs Consumed**:
  - Sonal (Feature 3): `InventoryDepletionTimeline` (`stockout_hour = 8.0h`).
  - Aadee (Feature 2): `RippleImpactSummary` (`affected_orders = ["ORD-01", "ORD-02", "ORD-03", ...]`).
  - Kanak (Feature 6): `order_deadlines` (`{"ORD-01": 10.0, "ORD-02": 12.0, ...}`).
- **Outputs Produced**:
  - Mishti (Feature 5): Receives `StockoutPredictionResult.stockout_hour` to calculate the Intervention Window ($\Delta T = 8.0 - 0.0 - 5.0 = +3.0\text{h}$).
  - Ansh (Feature 7): Imports `predict_stockout_and_orders()` into Step 4 of the master 25ms simulation engine pipeline (`engine.py`).
