"""
Project: RE:Flow
Sprint: 1
File: backend/tests/unit/test_validation.py

Primary Owner: Shanu
Role: Automated Testing and Integration Testing

Purpose:
Unit tests verifying topological and schema validation rules.

Responsibilities:
- Test DAG acyclicity validator on baseline graph (should pass).
- Test cycle detection by injecting synthetic cycle (should fail with cycle report).
- Test edge direction validator against invalid tier jumps (e.g. Supplier -> Product).
- Test schema validator with missing required attributes.

Dependencies:
- Soumya: Validation service and validators (backend/app/validation/).
- Shanu: conftest.py fixtures.

Deliverables:
- Complete unit test suite for graph validation rules.

Status: NOT STARTED
"""
