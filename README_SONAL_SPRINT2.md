# Team Photon — Sprint 2 | Sonal's Feature 3

## Feature
**Inventory Depletion Simulator** — discrete-time hourly simulation of warehouse stock during a supplier delay.

## Files in this contribution
Copy the `backend/` folder into the root of the Team Photon collaboration repository. The package contains:

- `backend/app/models/inventory.py` — `HourlyStockPoint` and `InventoryDepletionTimeline` Pydantic models.
- `backend/app/simulation/inventory.py` — `simulate_inventory_depletion()` implementation.
- `backend/tests/unit/test_inventory_simulator.py` — benchmark and edge-case tests.

The `backend/app/simulation/` folder includes `__init__.py` so it is importable as a Python package.

## Official benchmark
```python
result = simulate_inventory_depletion(
    part_id="P-01",
    initial_stock=40,
    hourly_consumption=5.0,
    delay_duration_hours=8.0,
)
```

Expected:
- Stock at hours 0–8: `40, 35, 30, 25, 20, 15, 10, 5, 0`
- `stockout_hour == 8.0`
- `len(timeline) == 73` (hour 0 through hour 72)
- `supply_blocked` is `True` for hours 0–7

## Run tests
Run from the collaboration repository root, in the same Python environment used by the project:

```bash
pytest -q backend/tests/unit/test_inventory_simulator.py
```

Dependencies: the project environment must include `pydantic` and `pytest`. Do not install a second dependency set if the repository already has a requirements file/environment.

## Integration contract
- Kanak supplies `initial_stock_units` and `hourly_consumption_units` from the calibrated scenario data.
- Divyanshu supplies `delay_duration_hours` from the disruption event.
- Anushka consumes `InventoryDepletionTimeline.timeline` and `stockout_hour`.
- Ansh imports `simulate_inventory_depletion()` into the simulation pipeline.

## Scope note
This contribution implements only Sonal's assigned Feature 3. It does not implement the scenario loader, disruption event, stockout predictor, orchestrator, API, or UI, which belong to other team members.

Before pushing, compare the imports and test command with the current repository layout and existing project conventions. This ZIP is a prepared contribution; it has not been merged into or tested against the live team repository.
