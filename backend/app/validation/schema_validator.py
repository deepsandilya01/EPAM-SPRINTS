"""
Project: RE:Flow
Sprint: 1
File: backend/app/validation/schema_validator.py

Primary Owner: Soumya
Role: Graph and Data Validation

Purpose:
Schema conformance validation for nodes and relationship properties.

Responsibilities:
- Validate scenario JSON against data/schemas/graph_schema.json.
- Verify all required fields exist for each tier (e.g. name, lead_time, unit_price).
- Detect duplicate node IDs and duplicate edge definitions.

Dependencies:
- JSON schema specification in data/schemas/graph_schema.json (Implemented by Deep; Team Maintained).
- Anushka: Raw scenario dataset (data/raw/scenario_dataset.json).

Deliverables:
- validate_dataset_schema(raw_data) function returning schema compliance details.

Status: NOT STARTED
"""
