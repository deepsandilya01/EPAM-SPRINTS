"""
Project: RE:Flow
Sprint: 1
File: backend/tests/integration/test_api.py

Primary Owner: Shanu
Role: Automated Testing and Integration Testing

Purpose:
Integration tests verifying HTTP endpoints, routing, and response schemas.

Responsibilities:
- Test GET /api/health returns 200 OK with expected JSON structure.
- Test GET /api/graph returns 200 OK with 19 nodes and 21 edges.
- Test POST /api/traversal with valid node returns 200 OK with blast radius.
- Test POST /api/traversal with invalid node returns 404 Not Found.
- Test GET /api/validation returns 200 OK with passing audit summary.
- Test GET /api/benchmarks returns 200 OK with latency metrics.

Dependencies:
- Divyanshu, Ansh, Preetam, Soumya, Kanak: Route implementations in backend/app/api/routes/.
- Shanu: test_client fixture from conftest.py.

Deliverables:
- End-to-end API integration test suite verifying all REST endpoints.

Status: NOT STARTED
"""
