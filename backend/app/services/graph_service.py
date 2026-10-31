"""
Project: RE:Flow
Sprint: 1
File: backend/app/services/graph_service.py

Primary Owner: Ansh
Role: NetworkX Graph Builder

Purpose:
Service layer managing graph lifecycle, state, and coordination.

Responsibilities:
- Manage singleton / cached NetworkX DiGraph instance.
- Coordinate data loading from data repository on startup.
- Provide thread-safe access methods for graph queries and downstream services.
- Expose serialized graph dictionary matching GraphResponseSchema.

Dependencies:
- Aadee: Data repository (backend/app/data/repository.py).
- Ansh: Graph builder (backend/app/graph/builder.py).
- Deep: Graph response schema (backend/app/schemas/graph.py).

Deliverables:
- GraphService class providing unified graph access for API routes and services.

Status: NOT STARTED
"""
