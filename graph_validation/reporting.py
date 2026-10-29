"""
Team Photon — Validation Reporting Utilities
─────────────────────────────────────────────
Generates human-readable console reports and persists JSON validation artifacts.
"""

import json
from pathlib import Path
from typing import Union

from .schema import ValidationReport


def format_console_report(report: ValidationReport) -> str:
    """Format a ValidationReport into an organized, readable terminal text report."""
    status_str = "PASS" if report.valid else "FAIL"
    summary = report.summary

    lines = [
        "=" * 72,
        "  TEAM PHOTON — GRAPH STRUCTURE VALIDATION REPORT",
        "=" * 72,
        f"  Graph Name    : {report.graph_name}",
        f"  Validation Mode: {report.mode.upper()}",
        f"  Overall Status: [{status_str}]",
        f"  Timestamp     : {report.timestamp}",
        "-" * 72,
        "  ENTITY SUMMARY COUNTS:",
        f"    Total Nodes : {summary.get('node_count', 0):<5} (Suppliers: {summary.get('supplier_count', 0)}, Parts: {summary.get('part_count', 0)}, Products: {summary.get('product_count', 0)}, Orders: {summary.get('order_count', 0)})",
        f"    Total Edges : {summary.get('edge_count', 0):<5} (Supplies: {summary.get('supplies_count', 0)}, Used In: {summary.get('used_in_count', 0)}, Fulfills: {summary.get('fulfills_count', 0)})",
        "-" * 72,
        "  VALIDATION CHECKS:",
    ]

    for check in report.checks:
        badge = f"[{check.status}]"
        lines.append(f"    {badge:<8} {check.check_id:<22} - {check.message}")

    if report.warnings:
        lines.append("-" * 72)
        lines.append(f"  WARNINGS ({len(report.warnings)}):")
        for w in report.warnings:
            lines.append(f"    • [{w.code}] {w.message}")
            if w.suggested_action:
                lines.append(f"      Action: {w.suggested_action}")

    if report.errors:
        lines.append("-" * 72)
        lines.append(f"  ERRORS ({len(report.errors)}):")
        for e in report.errors:
            lines.append(f"    • [{e.code}] ({e.severity}) {e.message}")
            if e.entity_id:
                lines.append(f"      Entity: {e.entity_id}")
            if e.expected is not None and e.actual is not None:
                lines.append(f"      Expected: {e.expected} | Actual: {e.actual}")
            if e.suggested_action:
                lines.append(f"      Suggested Action: {e.suggested_action}")

    lines.append("=" * 72)
    return "\n".join(lines)


def save_json_report(
    report: ValidationReport,
    filepath: Union[str, Path]
) -> Path:
    """Save a ValidationReport to a JSON file."""
    path = Path(filepath).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    return path

