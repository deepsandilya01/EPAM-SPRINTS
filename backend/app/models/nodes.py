"""
Project: RE:Flow
Sprint: 1
File: backend/app/models/nodes.py

Primary Owner: Deep
Role: Graph Domain Models and Data Contracts

Purpose:
Domain models for supply chain graph nodes across tiers.

Responsibilities:
- Define SupplierNode (id, name, location, contact, risk_score).
- Define BOMPartNode (id, name, part_number, lead_time_days, cost).
- Define FinishedProductNode (id, name, sku, category, unit_price).
- Define CustomerOrderNode (id, order_number, customer_name, quantity, status).

Dependencies:
- Anushka: Approved scenario dataset field definitions.
- Deep: Tier constants in constants.py.

Deliverables:
- Domain dataclasses or Pydantic models for all 4 supply chain tiers.
- Unit tests passing under backend/tests/unit/test_graph.py.

Status: NOT STARTED
"""
