"""
Project: RE:Flow
Sprint: 1
File: backend/app/services/traversal_service.py

Primary Owner: Preetam
Role: Graph Traversal and BFS

Purpose:
Service layer coordinating graph traversal and blast-radius queries.

Responsibilities:
- Validate that start_node_id exists in the active graph; raise NodeNotFoundError if missing.
- Invoke BFS traversal algorithm with timing measurement.
- Aggregate impacted nodes and categorize blast radius by tier (BOM parts, finished products, customer orders).
- Format traversal output matching TraversalResponseSchema.

Dependencies:
- Preetam: Traversal algorithm (backend/app/graph/traversal.py).
- Ansh: Graph service (backend/app/services/graph_service.py).
- Traversal Response Schema: backend/app/schemas/traversal.py (Implemented by Deep; Team Maintained).

Deliverables:
- TraversalService class with trace_downstream_impact(start_node_id) method.

Status: NOT STARTED
"""
