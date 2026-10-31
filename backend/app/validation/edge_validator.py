"""
Project: RE:Flow
Sprint: 1
File: backend/app/validation/edge_validator.py

Primary Owner: Soumya
Role: Graph and Data Validation

Purpose:
Edge validity and tier connection constraint verification.

Responsibilities:
- Verify SUPPLIES edges only connect Supplier -> BOM Part.
- Verify USED_IN edges only connect BOM Part -> Finished Product.
- Verify FULFILLS edges only connect Finished Product -> Customer Order.
- Detect dangling edges referencing non-existent source or target node IDs.

Dependencies:
- Tier constants and edge models (backend/app/core/constants.py; Implemented by Deep, Team Maintained).

Deliverables:
- validate_edge_relationships(graph) function returning edge direction audit results.

Status: NOT STARTED
"""
