"""
Project: RE:Flow
Sprint: 1
File: backend/app/data/repository.py

Primary Owner: Aadee
Role: Data Loading and Normalization

Purpose:
Repository pattern implementation for graph data retrieval and caching.

Responsibilities:
- Provide ScenarioRepository class to encapsulate data access.
- Cache normalized data in memory to prevent repeated disk reads.
- Expose get_scenario_data(), get_raw_nodes(), and get_raw_edges() methods.

Dependencies:
- Aadee: loader.py and normalizer.py modules.

Deliverables:
- ScenarioRepository class ready for injection into GraphService.

Status: NOT STARTED
"""
