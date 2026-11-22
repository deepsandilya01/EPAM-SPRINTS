Run Sonal's acceptance tests from the repository root:

    pytest -q backend/tests/unit/test_inventory_simulator.py

The tests verify the official 8-hour benchmark, 73 hourly points, blocked supply
hours 0–7, non-negative stock, no-stockout behavior, and invalid input handling.
