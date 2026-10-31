"""
Project: RE:Flow
Sprint: 1
File: backend/app/core/exceptions.py

Ownership: Team Maintained
Role: Custom Domain Exceptions
Status: COMPLETED

Ownership: Team Maintained (Implemented by Deep during Sprint 1)
Role: Custom Domain Exceptions
Status: COMPLETED

Purpose:
Custom domain exception classes for RE:Flow error handling.
"""

from typing import Any, Dict, List, Optional


class ReflowException(Exception):
    """Base exception class for all RE:Flow domain errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to structured dictionary for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ModelValidationError(ReflowException):
    """Raised when node or edge attributes fail domain model validation."""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="MODEL_VALIDATION_ERROR", details=details)
        self.field = field


class NodeNotFoundError(ReflowException):
    """Raised when a requested node ID does not exist in the graph."""
    def __init__(self, node_id: str):
        super().__init__(
            f"Node with ID '{node_id}' was not found in the graph.",
            code="NODE_NOT_FOUND",
            details={"node_id": node_id},
        )
        self.node_id = node_id


class InvalidEdgeError(ReflowException):
    """Raised when an edge definition violates relationship rules or creates illegal transitions."""
    def __init__(self, message: str, source: Optional[str] = None, target: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="INVALID_EDGE", details=details)
        self.source = source
        self.target = target


class SchemaValidationError(ReflowException):
    """Raised when incoming dataset payloads fail schema validation against graph_schema.json."""
    def __init__(self, message: str, errors: Optional[List[Any]] = None):
        super().__init__(message, code="SCHEMA_VALIDATION_ERROR", details={"errors": errors or []})
        self.errors = errors or []


class GraphCycleDetectedError(ReflowException):
    """Raised when an operation would introduce or detect a cycle in the DAG."""
    def __init__(self, cycle_path: Optional[List[str]] = None):
        super().__init__(
            f"Cycle detected in Directed Acyclic Graph: {' -> '.join(cycle_path or [])}",
            code="CYCLE_DETECTED",
            details={"cycle_path": cycle_path or []},
        )
        self.cycle_path = cycle_path or []
