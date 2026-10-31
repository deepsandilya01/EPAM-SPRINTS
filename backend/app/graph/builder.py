"""
Project: RE:Flow
Sprint: 1
File: backend/app/graph/builder.py

Primary Owner: Ansh
Role: NetworkX Graph Builder

Purpose:
Construct the supply chain directed graph (NetworkX DiGraph).

Responsibilities:
- Instantiate NetworkX DiGraph.
- Iterate normalized nodes and add to graph with tier and attribute metadata.
- Iterate normalized edges and add directed edges with relationship attributes.
- Validate node count (19) and edge count (21) against baseline scenario requirements.

Dependencies:
- Deep: Graph models and contracts (backend/app/models/).
- Aadee: Normalized scenario data (backend/app/data/normalizer.py).
- Anushka: Approved dataset (data/raw/scenario_dataset.json).

Deliverables:
- Working graph builder function/class returning populated nx.DiGraph.
- Passing unit tests in backend/tests/unit/test_graph.py.

Status: NOT STARTED
"""
