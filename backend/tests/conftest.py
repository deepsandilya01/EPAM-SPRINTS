"""
Pytest fixtures and test harnesses.
Provides isolated dataset copies and a Flask test client with automatic state cleanup.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import networkx as nx
import pytest

from graph_validation.schema import ValidationPolicy

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
DATA_FILE = BASE_DIR / "data" / "photon_sprint1_graph_data.json"
if not DATA_FILE.exists():
    for _candidate in (
        REPO_ROOT / "data" / "photon_sprint1_graph_data.json",
        Path("backend/data") / "photon_sprint1_graph_data.json",
        Path("data") / "photon_sprint1_graph_data.json",
        BASE_DIR / "photon_sprint1_graph_data.json",
    ):
        if _candidate.exists():
            DATA_FILE = _candidate
            break



@pytest.fixture(scope="session")
def raw_baseline_json() -> dict[str, Any]:
    """Load pristine canonical graph data once per test session."""
    assert DATA_FILE.exists(), f"Graph data file missing at: {DATA_FILE}"
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture
def raw_data(raw_baseline_json: dict[str, Any]) -> dict[str, Any]:
    """Provide a fresh, deep copy of canonical graph data for mutation testing."""
    return copy.deepcopy(raw_baseline_json)


@pytest.fixture
def canonical_graph(raw_data: dict[str, Any]) -> nx.DiGraph:
    """Build a fresh DiGraph from canonical baseline data."""
    G = nx.DiGraph()
    for cat in ("suppliers", "parts", "products", "orders"):
        for node in raw_data["nodes"].get(cat, []):
            G.add_node(node["id"], **node)
    for edge_type in ("supplies", "used_in", "fulfills"):
        for edge in raw_data["edges"].get(edge_type, []):
            attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
            G.add_edge(edge["source"], edge["target"], **attrs)
    return G


@pytest.fixture
def baseline_policy() -> ValidationPolicy:
    """Validation policy configured for baseline verification."""
    return ValidationPolicy(check_baseline_counts=True)


@pytest.fixture
def integrity_policy() -> ValidationPolicy:
    """Validation policy configured for live structural integrity (e.g. post-deletion)."""
    return ValidationPolicy(check_baseline_counts=False)


@pytest.fixture
def app_client():
    """
    Provide an isolated Flask test client with automatic graph state cleanup.
    Ensures mutations (deletion, undo, reset) in one test do not leak into another.
    """
    from app import GRAPH, UNDO_STACK, app

    # Snapshot current global state
    orig_nodes = copy.deepcopy(dict(GRAPH.nodes(data=True)))
    orig_edges = copy.deepcopy(list(GRAPH.edges(data=True)))
    orig_undo = copy.deepcopy(UNDO_STACK)

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

    # Restore global state after test
    GRAPH.clear()
    for n, d in orig_nodes.items():
        GRAPH.add_node(n, **d)
    for u, v, d in orig_edges:
        GRAPH.add_edge(u, v, **d)
    UNDO_STACK.clear()
    UNDO_STACK.extend(orig_undo)

