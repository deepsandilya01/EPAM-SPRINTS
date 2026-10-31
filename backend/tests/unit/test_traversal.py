"""
Project: RE:Flow
Sprint: 1
File: backend/tests/unit/test_traversal.py

Primary Owner: Shanu
Role: Automated Testing and Integration Testing

Purpose:
Unit tests verifying downstream graph traversal and reachability.

Responsibilities:
- Verify downstream traversal from Supplier 1 reaches expected BOM parts, products, and orders.
- Verify downstream traversal from Supplier 2 reaches expected downstream nodes.
- Verify path tracking accuracy and traversal depth calculations.
- Verify leaf node traversal returns empty downstream dependencies.

Dependencies:
- Preetam: Traversal algorithm (backend/app/graph/traversal.py).
- Shanu: conftest.py fixtures.

Deliverables:
- Complete unit test suite for downstream BFS traversal.

Status: NOT STARTED
"""
