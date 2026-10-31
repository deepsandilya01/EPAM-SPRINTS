"""
Project: RE:Flow
Sprint: 1
File: backend/app/models/edges.py

Primary Owner: Deep
Role: Graph Domain Models and Data Contracts

Purpose:
Domain models for directed dependency edges between supply chain nodes.

Responsibilities:
- Define BaseEdge (source, target, relationship_type, attributes).
- Define SuppliesEdge (supplier -> part with supply_capacity, lead_time).
- Define UsedInEdge (part -> product with quantity_required, unit_of_measure).
- Define FulfillsEdge (product -> order with quantity_allocated, fulfillment_date).

Dependencies:
- Deep: EdgeType constants in constants.py.
- Anushka: Approved scenario dataset edge attributes.

Deliverables:
- Domain models for all 3 directed relationship types with validation constraints.

Status: NOT STARTED
"""
