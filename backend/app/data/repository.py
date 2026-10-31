from __future__ import annotations

import pathlib
from typing import Any

from backend.app.data.loader import load_scenario_dataset
from backend.app.data.normalizer import normalize_scenario_data


class ScenarioRepository:
    """
    In-memory cached repository encapsulating raw and normalized scenario data.
    """

    def __init__(self, data_path: str | pathlib.Path | None = None) -> None:
        self._data_path = data_path
        self._raw_data: dict[str, Any] | None = None
        self._normalized_data: dict[str, Any] | None = None

    def get_raw_data(self, force_reload: bool = False) -> dict[str, Any]:
        """Load and return the raw scenario dataset."""
        if self._raw_data is None or force_reload:
            self._raw_data = load_scenario_dataset(self._data_path)
        return self._raw_data

    def get_scenario_data(self, force_reload: bool = False) -> dict[str, Any]:
        """Return the normalized scenario dataset."""
        if self._normalized_data is None or force_reload:
            raw = self.get_raw_data(force_reload=force_reload)
            self._normalized_data = normalize_scenario_data(raw)
        return self._normalized_data

    def get_raw_nodes(self) -> list[dict[str, Any]]:
        """Return the list of normalized node records."""
        data = self.get_scenario_data()
        return data.get("nodes", [])

    def get_raw_edges(self) -> list[dict[str, Any]]:
        """Return the list of normalized edge records."""
        data = self.get_scenario_data()
        return data.get("edges", [])

    def get_domain_graph(self, force_reload: bool = False) -> Any:
        """Instantiate and return the SupplyChainGraph domain model aggregate."""
        from backend.app.models.graph import SupplyChainGraph

        raw = self.get_raw_data(force_reload=force_reload)
        return SupplyChainGraph.from_dict(raw)

    def clear_cache(self) -> None:
        """Clear cached data in memory."""
        self._raw_data = None
        self._normalized_data = None
