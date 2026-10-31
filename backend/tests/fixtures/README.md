# Test Fixtures Ownership & Specification

> **Sprint 1 Ownership & Task Assignment**
> - **Primary Owner**: Anushka
> - **Role**: Scenario Dataset Preparation
> - **Target File**: `backend/tests/fixtures/sample_scenario.json`
> - **Companion Doc**: `backend/tests/fixtures/README.md`
> - **Status**: NOT STARTED

## Purpose
Holds test fixtures for automated Pytest unit and integration suites. `sample_scenario.json` provides an immutable, standardized scenario dataset for deterministic test execution.

*(Note: Per RFC 8259, comments are omitted from `sample_scenario.json` to maintain valid JSON parsing. Documentation is maintained here.)*

## Exact Responsibilities
1. Create and maintain `sample_scenario.json` as a minimal, deterministic test fixture mirroring the baseline scenario structure.
2. Ensure consistent node IDs and edge relationships for automated test assertions.
3. Keep test fixtures synchronized with canonical schema changes.

## Expected Deliverables
- Valid JSON fixture in `backend/tests/fixtures/sample_scenario.json`.

## Dependencies
- **Shanu**: Test fixture requirements in `backend/tests/conftest.py`.
- **Domain Models**: Domain models in `backend/app/models/` (Implemented by Deep; Team Maintained).

## Verification
- Verified during Pytest fixture loading in `backend/tests/conftest.py`.
