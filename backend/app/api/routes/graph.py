"""
Project: RE:Flow
Sprint: 1
File: backend/app/api/routes/graph.py

Primary Owner: Ansh
Role: NetworkX Graph Builder

Purpose:
Graph query and topological data retrieval route definitions.

Responsibilities:
- Implement GET /api/graph endpoint.
- Query GraphService to retrieve active graph topology.
- Return validated JSON response with all 19 nodes, 21 edges, and tier groupings.

Dependencies:
- Ansh: Graph service (backend/app/services/graph_service.py).
- Graph response schema in backend/app/schemas/graph.py (Implemented by Deep; Team Maintained).

Deliverables:
- Working GET /api/graph endpoint returning HTTP 200 with complete graph payload.

Status: NOT STARTED
"""
