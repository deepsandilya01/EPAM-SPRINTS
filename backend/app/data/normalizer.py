"""
Project: RE:Flow
Sprint: 1
File: backend/app/data/normalizer.py

Primary Owner: Aadee
Role: Data Loading and Normalization

Purpose:
Data normalization and sanitization utilities for incoming records.

Responsibilities:
- Sanitize raw JSON dictionary keys and structure.
- Normalize tier names into canonical TierType enums.
- Validate node ID formats and ensure unique IDs.
- Transform raw edge lists into normalized edge dictionaries (source, target, type, attributes).

Dependencies:
- Aadee: Raw data output from loader.py.
- Deep: Core constants and domain models (backend/app/core/constants.py).

Deliverables:
- normalize_scenario_data(raw_dict) function producing clean domain dictionaries.

Status: NOT STARTED
"""
