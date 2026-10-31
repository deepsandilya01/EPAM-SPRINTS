from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ValidationErrorItemSchema(BaseModel):
    """
    Structured representation of a blocking validation error.

    Why this exists:
    Identifies severe integrity violations that invalidate the graph (e.g.,
    cycles, self-loops, illegal tier jumps, or negative stock).
    """
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(..., description="Machine-readable error code (e.g. 'CYCLE_DETECTED', 'ILLEGAL_TIER_JUMP')")
    message: str = Field(..., description="Human-readable explanation of why the rule failed")
    field: Optional[str] = Field(None, description="Affected field name if attribute-specific")
    entity_id: Optional[str] = Field(None, description="Identifier of the offending node or edge")
    severity: str = Field(default="error", description="Severity level ('error' or 'critical')")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional diagnostic context")


class ValidationWarningItemSchema(BaseModel):
    """
    Structured representation of a non-blocking warning.

    Why this exists:
    Identifies potential operational risks that do not violate graph integrity
    (e.g., BOM part with days_of_supply < 3 days).
    """
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(..., description="Machine-readable warning code (e.g. 'LOW_DAYS_OF_SUPPLY')")
    message: str = Field(..., description="Human-readable warning description")
    entity_id: Optional[str] = Field(None, description="Identifier of the node or edge triggering the warning")
    severity: str = Field(default="warning", description="Severity level ('warning')")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional diagnostic context")


class ValidationRuleResultSchema(BaseModel):
    """
    Evaluation result for an individual validation rule executed during audit.
    """
    model_config = ConfigDict(populate_by_name=True)

    rule_name: str = Field(..., description="Name of the validation rule (e.g. 'acyclicity', 'tier_transitions')")
    passed: bool = Field(..., description="True if the graph satisfied this rule, False otherwise")
    severity: str = Field(default="error", description="Severity level assigned to this rule")
    message: str = Field(..., description="Summary of the rule evaluation")
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Specific violation occurrences")


class ValidationRequestSchema(BaseModel):
    """
    Query parameter schema for triggering validation (GET /api/validation).
    """
    model_config = ConfigDict(populate_by_name=True)

    mode: str = Field(default="baseline", description="Validation mode ('baseline' or 'integrity')")
    strict: bool = Field(default=True, description="Whether warnings should be treated as failures")


class ValidationResponseSchema(BaseModel):
    """
    Response schema for graph validation audit.

    Why this exists:
    Standardizes the validation report returned to the frontend and other services
    following Soumya's integrity validation checks.

    Canonical contract example:
    {
      "is_valid": true,
      "errors": [],
      "warnings": []
    }
    """
    model_config = ConfigDict(populate_by_name=True)

    is_valid: bool = Field(..., description="Overall graph validity (True only if 0 blocking errors)")
    errors: List[ValidationErrorItemSchema] = Field(
        default_factory=list,
        description="List of blocking validation errors",
    )
    warnings: List[ValidationWarningItemSchema] = Field(
        default_factory=list,
        description="List of non-blocking operational warnings",
    )
    total_rules: int = Field(default=0, ge=0, description="Total audit rules evaluated")
    passed_rules: int = Field(default=0, ge=0, description="Count of passed audit rules")
    failed_rules: int = Field(default=0, ge=0, description="Count of failed audit rules")
    rules: Optional[List[ValidationRuleResultSchema]] = Field(
        default=None,
        description="Detailed breakdown of individual rule evaluations",
    )
    timestamp: Optional[str] = Field(None, description="ISO 8601 audit completion timestamp")
