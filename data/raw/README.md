# Raw Scenario Dataset Ownership & Specification

> **Sprint 1 Ownership & Task Assignment**
> - **Primary Owner**: Anushka
> - **Role**: Scenario Dataset Preparation
> - **Target File**: `data/raw/scenario_dataset.json`
> - **Companion Doc**: `data/raw/README.md`
> - **Status**: NOT STARTED

## Purpose
This directory holds the canonical raw supply chain scenario dataset for RE:Flow Sprint 1. The target file `data/raw/scenario_dataset.json` contains the baseline supply chain network topology.

*(Note: In accordance with JSON standards (RFC 8259), comments are not embedded inside `scenario_dataset.json` so that parsers do not encounter syntax errors. All ownership, requirements, and structural documentation are maintained in this companion file.)*

## Exact Responsibilities
1. Prepare the approved Sprint 1 baseline supply chain dataset.
2. Structure the dataset across all 4 sequential tiers:
   - **2 Suppliers**: Primary raw material providers.
   - **5 BOM Parts**: Bill of materials components supplied by the suppliers.
   - **2 Finished Products**: Manufactured goods assembled from BOM parts.
   - **10 Customer Orders**: Retail and commercial fulfillment orders.
3. Validate total graph counts:
   - **Total Nodes**: Exactly 19 nodes.
   - **Total Directed Edges**: Exactly 21 directed edges.
4. Ensure edge directions follow approved relationship rules:
   - `SUPPLIES`: Supplier -> BOM Part
   - `USED_IN`: BOM Part -> Finished Product
   - `FULFILLS`: Finished Product -> Customer Order
5. Do not invent missing business relationships or unapproved entity links.

## Expected Deliverables
- Valid, well-formed `data/raw/scenario_dataset.json` containing the approved 19 nodes and 21 edges.
- Complete attribute fields for every node (id, name, tier, attributes) and edge (source, target, relationship_type, attributes).

## Dependencies
- **Domain Models & Schemas**: Graph models and schema constraints (`backend/app/models/` and `data/schemas/graph_schema.json`; implemented by Deep, Team Maintained).
- **Aadee**: Data loader and normalizer format requirements (`backend/app/data/`).
- **Sonal**: Supply chain mapping verification (`docs/reports/mapping_verification.md`).

## Verification
- Verified by automated unit tests in `backend/tests/unit/test_graph.py` and schema checks in `backend/app/validation/schema_validator.py`.
