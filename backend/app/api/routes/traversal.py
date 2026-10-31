"""
Project: RE:Flow
Sprint: 1
File: backend/app/api/routes/traversal.py

Primary Owner: Preetam
Role: Graph Traversal and BFS

Purpose:
Graph traversal and downstream impact tracing route definitions.

Responsibilities:
- Implement POST /api/traversal endpoint.
- Parse and validate TraversalRequestSchema JSON payload.
- Invoke TraversalService to execute downstream trace.
- Return 200 OK with blast radius results, or 404 Not Found for unknown node IDs.

Dependencies:
- Preetam: Traversal service (backend/app/services/traversal_service.py).
- Deep: Traversal schemas (backend/app/schemas/traversal.py).

Deliverables:
- Working POST /api/traversal endpoint with complete schema validation and error responses.

Status: NOT STARTED
"""
