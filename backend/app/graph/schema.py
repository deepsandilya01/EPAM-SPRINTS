"""
Project: RE:Flow
Sprint: 1
File: backend/app/graph/schema.py

Primary Owner: Ansh
Role: NetworkX Graph Builder

Purpose:
Graph topological specifications and tier relationship rules for builder.

Responsibilities:
- Define allowed tier connectivity transitions (SUPPLIER -> BOM_PART -> FINISHED_PRODUCT -> CUSTOMER_ORDER).
- Define required node attribute keys for NetworkX node data dictionaries.
- Define required edge attribute keys for NetworkX edge data dictionaries.

Dependencies:
- Deep: models/nodes.py, models/edges.py, core/constants.py.

Deliverables:
- Rule and constraint specification module for graph construction.

Status: NOT STARTED
"""
