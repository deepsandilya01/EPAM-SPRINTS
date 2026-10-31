from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

try:
    from datetime import UTC  # type: ignore[attr-defined]
except ImportError:
    UTC = timezone.utc  # noqa: UP017


def _iso_now() -> str:
    """Return ISO 8601 formatted timestamp in UTC."""
    return datetime.now(UTC).isoformat()


class AcyclicityPolicy(str, Enum):
    """How strictly to enforce DAG acyclicity."""
    REQUIRE_DAG = "require_dag"
    ALLOW_CYCLES = "allow_cycles"
    UNSPECIFIED = "unspecified"


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class BaselineCounts:
    """Expected counts for the canonical Sprint 1 dataset (19 nodes, 21 edges)."""
    total_nodes: int = 19
    suppliers: int = 2
    parts: int = 5
    products: int = 2
    orders: int = 10
    total_edges: int = 21
    supplies: int = 6
    used_in: int = 5
    fulfills: int = 10

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationPolicy:
    """
    Configures which checks to run.
    Allows toggling between baseline checks (exact count enforcement)
    and live integrity checks (valid endpoints, directions, DAG).
    """
    check_baseline_counts: bool = True
    acyclicity_policy: AcyclicityPolicy = AcyclicityPolicy.REQUIRE_DAG
    baseline_counts: BaselineCounts = field(default_factory=BaselineCounts)
    allowed_node_categories: tuple[str, ...] = ("suppliers", "parts", "products", "orders")
    allowed_edge_types: tuple[str, ...] = ("supplies", "used_in", "fulfills")

    # Allowed direction rules: (expected_source_kind, expected_target_kind, relation_name)
    direction_rules: dict[str, tuple[str, str, str]] = field(default_factory=lambda: {
        "supplies": ("supplier", "part", "SUPPLIES"),
        "used_in": ("part", "product", "USED_IN"),
        "fulfills": ("product", "order", "FULFILLS"),
    })

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_baseline_counts": self.check_baseline_counts,
            "acyclicity_policy": self.acyclicity_policy.value,
            "baseline_counts": self.baseline_counts.to_dict(),
            "allowed_node_categories": list(self.allowed_node_categories),
            "allowed_edge_types": list(self.allowed_edge_types),
            "direction_rules": {
                k: {"source_kind": v[0], "target_kind": v[1], "relation": v[2]}
                for k, v in self.direction_rules.items()
            },
        }


@dataclass
class ValidationError:
    """Details of an individual validation finding or failure."""
    code: str
    severity: str
    message: str
    entity_type: str
    entity_id: str | list[Any] | tuple[Any, ...] | None = None
    expected: Any = None
    actual: Any = None
    suggested_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "entity_type": self.entity_type,
            "entity_id": list(self.entity_id) if isinstance(self.entity_id, tuple) else self.entity_id,
            "expected": self.expected,
            "actual": self.actual,
            "suggested_action": self.suggested_action,
        }


@dataclass
class ValidationCheck:
    """Summary of an individual validation check step."""
    check_id: str
    status: str
    message: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "check_id": self.check_id,
            "status": self.status,
            "message": self.message,
        }
        if self.details is not None:
            res["details"] = self.details
        return res


@dataclass
class ValidationReport:
    """Structured report returned by the validator and API endpoints."""
    valid: bool
    graph_name: str
    mode: str
    summary: dict[str, Any]
    checks: list[ValidationCheck] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "graph_name": self.graph_name,
            "mode": self.mode,
            "summary": self.summary,
            "checks": [c.to_dict() for c in self.checks],
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "policy": self.policy,
            "timestamp": self.timestamp,
        }

