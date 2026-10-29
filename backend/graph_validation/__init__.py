"""
Graph structure validation and downstream tracing package.
"""

from .reporting import format_console_report, save_json_report
from .schema import (
    AcyclicityPolicy,
    BaselineCounts,
    CheckStatus,
    Severity,
    ValidationCheck,
    ValidationError,
    ValidationPolicy,
    ValidationReport,
)
from .tracing import trace_downstream_with_metrics
from .validator import (
    validate_graph,
    validate_networkx_graph,
    validate_raw_graph_data,
)

__all__ = [
    "AcyclicityPolicy",
    "BaselineCounts",
    "CheckStatus",
    "Severity",
    "ValidationCheck",
    "ValidationError",
    "ValidationPolicy",
    "ValidationReport",
    "validate_graph",
    "validate_networkx_graph",
    "validate_raw_graph_data",
    "trace_downstream_with_metrics",
    "format_console_report",
    "save_json_report",
]
