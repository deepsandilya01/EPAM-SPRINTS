# Graph Schema JSON Specification Ownership

> **Sprint 1 Ownership & Task Assignment**
> - **Ownership**: Team Maintained (Implemented by Deep during Sprint 1)
> - **Role**: Graph Domain Models and Data Contracts
> - **Target File**: `data/schemas/graph_schema.json`
> - **Companion Doc**: `data/schemas/README.md`
> - **Status**: COMPLETED / ACTIVE

## Purpose
Holds the formal JSON Schema specification for validating scenario datasets. `graph_schema.json` enforces structural validation rules prior to ingestion.

*(Note: Per RFC 8259, comments are omitted from `graph_schema.json` to ensure valid JSON schema evaluation.)*

## Exact Responsibilities
1. Define JSON Schema (Draft 7 or Draft 2020-12) specifying required properties, types, and constraints for scenario JSON files.
2. Enforce node schema validation:
   - `id`: string (unique)
   - `name`: string
   - `tier`: enum ("SUPPLIER", "BOM_PART", "FINISHED_PRODUCT", "CUSTOMER_ORDER")
   - `attributes`: object
3. Enforce edge schema validation:
   - `source`: string (valid node id)
   - `target`: string (valid node id)
   - `relationship_type`: enum ("SUPPLIES", "USED_IN", "FULFILLS")
   - `attributes`: object

## Expected Deliverables
- Valid JSON Schema in `data/schemas/graph_schema.json`.

## Dependencies
- **Anushka**: Dataset format alignment.
- **Soumya**: Schema validator implementation in `backend/app/validation/schema_validator.py`.

## Verification
- Evaluated by `jsonschema` validation in `backend/app/validation/schema_validator.py` and test suite `backend/tests/unit/test_validation.py`.
