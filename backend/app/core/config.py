from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass, field

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent


@dataclass(frozen=True)
class Settings:
    """Type-safe application configuration settings."""

    app_name: str = "RE:Flow — Supply Chain Graph"
    version: str = "1.0.0"
    environment: str = field(default_factory=lambda: os.getenv("FLASK_ENV", "development"))
    host: str = field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "5050")))
    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "0") == "1")

    # Canonical dataset path
    dataset_path: pathlib.Path = field(
        default_factory=lambda: REPO_ROOT / "data" / "raw" / "scenario_dataset.json"
    )

    # Static assets path
    static_dir: pathlib.Path = field(default_factory=lambda: BASE_DIR / "static")

    # SLA Performance Thresholds
    max_traversal_latency_ms: float = 10.0


# Global singleton settings instance
settings = Settings()


def get_settings() -> Settings:
    """Retrieve global settings object."""
    return settings
