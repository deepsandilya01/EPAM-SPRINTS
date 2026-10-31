"""
Project: RE:Flow
Sprint: 1
File: backend/app/data/loader.py

Primary Owner: Aadee
Role: Data Loading and Normalization

Purpose:
Dataset loading utilities for parsing raw scenario JSON files.

Responsibilities:
- Read and parse data/raw/scenario_dataset.json from disk.
- Handle FileNotFoundError and JSONDecodeError gracefully with clear error logging.
- Return raw dictionary representation of the supply chain scenario.

Dependencies:
- Anushka: Approved raw dataset (data/raw/scenario_dataset.json).
- Application configuration (backend/app/core/config.py).

Deliverables:
- Robust load_scenario_dataset(path) function with error handling.

Status: NOT STARTED
"""
