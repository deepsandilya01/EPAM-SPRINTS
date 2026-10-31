from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure unified logging format for the application."""
    format_str = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Provide a named logger instance with standardized formatting."""
    return logging.getLogger(name)
