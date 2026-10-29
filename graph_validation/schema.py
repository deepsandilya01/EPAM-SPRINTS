"""
Team Photon — Graph Structure Validation Module
─────────────────────────────────────────────────
Provides schema definitions, validation policies, and reporting structures
for supply-chain dependency graphs.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional, Union


class AcyclicityPolicy(str, Enum):
    """Acyclicity enforcement policy for graph validation."""
    REQUIRE_DAG = "require_dag"
    ALLOW_CYCLES = "allow_cycles"
    UNSPECIFIED = "unspecified"


class CheckStatus(str, Enum):
    """Validation check outcome status vocabulary."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class Severity(str, Enum):
    """Validation issue severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class BaselineCounts:
    """Configurable baseline counts for the Team Photon Sprint 1 graph."""
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
    Policy settings controlling graph validation behavior.
    
    Allows distinguishing between initial baseline checks (where exact node/edge
    counts are asserted) and live graph integrity checks (where nodes may have
    been legitimately deleted, but remaining edges/direction/DAG must stay valid).
    """
    check_baseline_counts: bool = True
    acyclicity_policy: AcyclicityPolicy = AcyclicityPolicy.REQUIRE_DAG
    baseline_counts: BaselineCounts = field(default_factory=BaselineCounts)
    allowed_node_categories: tuple[str, ...] = ("suppliers", "parts", "products", "orders")
    allowed_edge_types: tuple[str, ...] = ("supplies", "used_in", "fulfills")
    
    # Allowed supply-chain direction rules:
    # edge_type -> (allowed_source_kind, allowed_target_kind, expected_relation_str)
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
    """Structured error or warning detailing a validation finding."""
    code: str
    severity: str
    message: str
    entity_type: str  # "node", "edge", "graph", "structure", "metadata"
    entity_id: Optional[Union[str, list[Any], tuple[Any, ...]]] = None
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
    """Status record of an individual validation check."""
    check_id: str
    status: str  # PASS, FAIL, WARN, SKIP
    message: str
    details: Optional[dict[str, Any]] = None

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
    """Full, JSON-serializable validation report."""
    valid: bool
    graph_name: str
    mode: str  # "baseline" or "integrity"
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

