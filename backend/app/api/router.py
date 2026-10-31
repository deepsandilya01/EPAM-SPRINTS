"""
Project: RE:Flow
Sprint: 1
File: backend/app/api/router.py

Ownership: Team Maintained
Role: REST API Development and Routing

Purpose:
Central API router aggregating endpoint route blueprints.

Responsibilities:
- Create main '/api' Blueprint.
- Register health, graph, traversal, validation, and benchmark route sub-blueprints.
- Provide standardized error handling handlers for domain exceptions.

Dependencies:
- Health route (backend/app/api/routes/health.py).
- Ansh: Graph route (backend/app/api/routes/graph.py).
- Preetam: Traversal route (backend/app/api/routes/traversal.py).
- Soumya: Validation route (backend/app/api/routes/validation.py).
- Kanak: Benchmarks route (backend/app/api/routes/benchmarks.py).

Deliverables:
- Unified API router blueprint ready for registration in main.py.

Status: NOT STARTED
"""
