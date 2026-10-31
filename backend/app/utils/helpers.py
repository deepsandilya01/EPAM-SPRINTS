from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def safe_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely traverse a nested dictionary using dot-separated keys."""
    keys = path.split(".")
    curr: Any = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return default
    return curr


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Sanitize dictionary keys and strip leading/trailing string whitespace."""
    clean: dict[str, Any] = {}
    for k, v in data.items():
        clean_k = str(k).strip()
        if isinstance(v, str):
            clean[clean_k] = v.strip()
        elif isinstance(v, dict):
            clean[clean_k] = sanitize_dict(v)
        elif isinstance(v, list):
            clean[clean_k] = [sanitize_dict(item) if isinstance(item, dict) else item for item in v]
        else:
            clean[clean_k] = v
    return clean


def timer_decorator(func: Callable[..., T]) -> Callable[..., tuple[T, float]]:
    """Decorator measuring execution time in milliseconds."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> tuple[T, float]:
        t0 = time.perf_counter_ns()
        result = func(*args, **kwargs)
        t1 = time.perf_counter_ns()
        elapsed_ms = (t1 - t0) / 1_000_000.0
        return result, round(elapsed_ms, 6)
    return wrapper
