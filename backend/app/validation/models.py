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
    """Policy options for enforcing acyclicity on the dependency graph."""

    REQUIRE_DAG = "require_dag"
    ALLOW_CYCLES = "allow_cycles"
    UNSPECIFIED = "unspecified"


class CheckStatus(str, Enum):
    """Outcome status for an individual validation assertion."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class Severity(str, Enum):
    """Severity classification for validation findings."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class BaselineCounts:
    """Expected entity and relationship counts for the canonical Sprint 1 graph."""

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
    """Configuration governing validation rules, assertions, and strictness."""

    check_baseline_counts: bool = True
    acyclicity_policy: AcyclicityPolicy = AcyclicityPolicy.REQUIRE_DAG
    baseline_counts: BaselineCounts = field(default_factory=BaselineCounts)
    allowed_node_categories: tuple[str, ...] = (
        "suppliers",
        "parts",
        "products",
        "orders",
    )
    allowed_edge_types: tuple[str, ...] = ("supplies", "used_in", "fulfills")

    direction_rules: dict[str, tuple[str, str, str]] = field(
        default_factory=lambda: {
            "supplies": ("supplier", "part", "SUPPLIES"),
            "used_in": ("part", "product", "USED_IN"),
            "fulfills": ("product", "order", "FULFILLS"),
        }
    )

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
    """Structured details of an individual validation finding or failure."""

    code: str
    severity: str
    message: str
    entity_type: str
    entity_id: str | list[Any] | tuple[Any, ...] | None = None
    expected: Any = None
    actual: Any = None
    suggested_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "entity_type": self.entity_type,
        }
        if self.entity_id is not None:
            data["entity_id"] = (
                list(self.entity_id)
                if isinstance(self.entity_id, tuple)
                else self.entity_id
            )
        if self.expected is not None:
            data["expected"] = self.expected
        if self.actual is not None:
            data["actual"] = self.actual
        if self.suggested_action is not None:
            data["suggested_action"] = self.suggested_action
        return data


@dataclass
class ValidationCheck:
    """Evaluation summary of an individual high-level validation assertion."""

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
    """Structured audit report returned by validation routines."""

    valid: bool
    graph_name: str
    mode: str
    summary: dict[str, Any]
    checks: list[ValidationCheck]
    errors: list[ValidationError]
    warnings: list[ValidationError]
    policy: dict[str, Any]
    timestamp: str

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

