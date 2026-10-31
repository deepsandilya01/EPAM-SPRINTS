"""
Project: RE:Flow
Sprint: 1
File: backend/tests/unit/test_graph.py

Primary Owner: Shanu
Role: Automated Testing and Integration Testing

Purpose:
Unit tests verifying graph builder and NetworkX DiGraph representation.

Responsibilities:
- Assert total node count equals 19 (2 Suppliers, 5 Parts, 2 Products, 10 Orders).
- Assert total edge count equals 21.
- Assert node attributes (tier, name, cost/lead_time) are properly attached.
- Assert directed edge attributes and directions.

Dependencies:
- Ansh: Graph builder (backend/app/graph/builder.py).
- Shanu: built_graph fixture from conftest.py.

Deliverables:
- Complete unit test suite for graph structure and builder.

Status: NOT STARTED
"""
