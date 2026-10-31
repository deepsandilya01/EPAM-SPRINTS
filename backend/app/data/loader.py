from __future__ import annotations

import json
import logging
import pathlib
from typing import Any

logger = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent.parent


CANONICAL_DATASET_PATH = REPO_ROOT / "data" / "raw" / "scenario_dataset.json"


def get_data_file_path(custom_path: str | pathlib.Path | None = None) -> pathlib.Path:
    """
    Resolve scenario dataset location.
    Defaults directly to the canonical root dataset: data/raw/scenario_dataset.json.
    """
    if custom_path:
        p = pathlib.Path(custom_path)
        if p.exists():
            return p

    if CANONICAL_DATASET_PATH.exists():
        return CANONICAL_DATASET_PATH

    # Fallback to test fixture if running in isolated test directory
    fixture_path = REPO_ROOT / "backend" / "tests" / "fixtures" / "sample_scenario.json"
    if fixture_path.exists():
        return fixture_path

    return CANONICAL_DATASET_PATH


def load_scenario_dataset(data_path: str | pathlib.Path | None = None) -> dict[str, Any]:
    """Load and parse the scenario JSON dataset from disk."""
    file_path = get_data_file_path(data_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Scenario dataset not found at {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {file_path}: {e}")
        raise


# Aliases for compatibility with original PHOTON source code
_load_raw_data = load_scenario_dataset
DATA_FILE = get_data_file_path()
