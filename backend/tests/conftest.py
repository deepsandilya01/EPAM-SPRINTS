from __future__ import annotations

import copy
from typing import Any

import networkx as nx
import pytest
from fastapi.testclient import TestClient

from backend.app.data.loader import get_data_file_path, load_scenario_dataset
from backend.app.graph.builder import build_graph
from backend.app.main import app
from backend.app.services.graph_service import GRAPH, UNDO_STACK
from backend.app.validation import ValidationPolicy


class FastAPITestResponseWrapper:
    """Compatibility wrapper providing both Flask and FastAPI response interfaces."""

    def __init__(self, response):
        self._response = response
        self.status_code = response.status_code
        self.content = response.content
        self.data = response.content
        self.headers = response.headers

    def get_json(self):
        return self._response.json()

    def json(self):
        return self._response.json()


class FastAPITestClientWrapper:
    """Client wrapper providing seamless test API access."""

    def __init__(self, client: TestClient):
        self._client = client

    def get(self, *args, **kwargs):
        res = self._client.get(*args, **kwargs)
        return FastAPITestResponseWrapper(res)

    def post(self, *args, **kwargs):
        res = self._client.post(*args, **kwargs)
        return FastAPITestResponseWrapper(res)

    def delete(self, *args, **kwargs):
        res = self._client.delete(*args, **kwargs)
        return FastAPITestResponseWrapper(res)

    def put(self, *args, **kwargs):
        res = self._client.put(*args, **kwargs)
        return FastAPITestResponseWrapper(res)


@pytest.fixture(scope="session")
def raw_baseline_json() -> dict[str, Any]:
    """Load pristine canonical graph data once per test session."""
    data_file = get_data_file_path()
    assert data_file.exists(), f"Graph data file missing at: {data_file}"
    return load_scenario_dataset(data_file)


@pytest.fixture
def raw_data(raw_baseline_json: dict[str, Any]) -> dict[str, Any]:
    """Provide a fresh, deep copy of canonical graph data for mutation testing."""
    return copy.deepcopy(raw_baseline_json)


@pytest.fixture
def canonical_graph(raw_data: dict[str, Any]) -> nx.DiGraph:
    """Build a fresh DiGraph from canonical baseline data."""
    return build_graph(raw_data)


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
    Provide an isolated FastAPI test client with automatic graph state cleanup.
    Ensures mutations (deletion, undo, reset) in one test do not leak into another.
    """
    orig_nodes = copy.deepcopy(dict(GRAPH.nodes(data=True)))
    orig_edges = copy.deepcopy(list(GRAPH.edges(data=True)))
    orig_undo = copy.deepcopy(UNDO_STACK)

    with TestClient(app) as client:
        wrapped_client = FastAPITestClientWrapper(client)
        yield wrapped_client

    # Restore global state after test
    GRAPH.clear()
    for n, d in orig_nodes.items():
        GRAPH.add_node(n, **d)
    for u, v, d in orig_edges:
        GRAPH.add_edge(u, v, **d)
    UNDO_STACK.clear()
    UNDO_STACK.extend(orig_undo)


# Target aliases for complete test-harness compatibility
sample_raw_data = raw_data
built_graph = canonical_graph
test_client = app_client
