from __future__ import annotations

from backend.app.data.loader import _load_raw_data, load_scenario_dataset
from backend.app.graph.builder import _build_graph, build_graph
from backend.app.graph.operations import _graph_to_json, _restore, _snapshot
from backend.app.graph.traversal import _downstream, get_downstream
from backend.app.main import app, create_app
from backend.app.services.graph_service import (
    HISTORY,
    RAW,
    UNDO_STACK,
    _apply_delete,
    _rebuild_from_history,
    service_instance,
)

# On module load/reload, ensure state starts from clean canonical baseline
service_instance.reset()
GRAPH = service_instance.graph

__all__ = [
    "app",
    "create_app",
    "GRAPH",
    "UNDO_STACK",
    "HISTORY",
    "RAW",
    "service_instance",
    "_load_raw_data",
    "load_scenario_dataset",
    "_build_graph",
    "build_graph",
    "_downstream",
    "get_downstream",
    "_snapshot",
    "_restore",
    "_graph_to_json",
    "_apply_delete",
    "_rebuild_from_history",
]
