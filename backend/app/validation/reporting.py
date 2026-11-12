from __future__ import annotations

import json
import pathlib
from typing import Any


def format_console_report(report: Any) -> str:
    """Format a human-readable ASCII terminal report from a ValidationReport."""
    lines: list[str] = [
        "=" * 72,
        "  TEAM PHOTON — GRAPH STRUCTURE VALIDATION REPORT",
        "=" * 72,
        f"  Graph Name    : {report.graph_name}",
        f"  Validation Mode: {report.mode.upper()}",
        f"  Overall Status: [{'PASS' if report.valid else 'FAIL'}]",
        f"  Timestamp     : {report.timestamp}",
        "-" * 72,
        "  ENTITY SUMMARY COUNTS:",
        f"    Total Nodes : {report.summary.get('node_count', 0):<5} "
        f"(Suppliers: {report.summary.get('supplier_count', 0)}, "
        f"Parts: {report.summary.get('part_count', 0)}, "
        f"Products: {report.summary.get('product_count', 0)}, "
        f"Orders: {report.summary.get('order_count', 0)})",
        f"    Total Edges : {report.summary.get('edge_count', 0):<5} "
        f"(Supplies: {report.summary.get('supplies_count', 0)}, "
        f"Used In: {report.summary.get('used_in_count', 0)}, "
        f"Fulfills: {report.summary.get('fulfills_count', 0)})",
        "-" * 72,
        "  VALIDATION CHECKS:",
    ]

    for check in report.checks:
        status_tag = f"[{check.status}]"
        lines.append(f"    {status_tag:<8} {check.check_id:<22} - {check.message}")

    if report.errors:
        lines.append("-" * 72)
        lines.append(f"  ERRORS DETECTED ({len(report.errors)}):")
        for err in report.errors:
            lines.append(f"    [{err.code}] {err.message}")
            if err.suggested_action:
                lines.append(f"      Action: {err.suggested_action}")

    if report.warnings:
        lines.append("-" * 72)
        lines.append(f"  WARNINGS ({len(report.warnings)}):")
        for w in report.warnings:
            lines.append(f"    [{w.code}] {w.message}")

    lines.append("=" * 72)
    return "\n".join(lines)


def save_json_report(report: Any, file_path: str | pathlib.Path) -> pathlib.Path:
    """Save the validation report to disk as indented JSON."""
    out_path = pathlib.Path(file_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    return out_path
