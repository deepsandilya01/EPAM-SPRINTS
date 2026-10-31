from __future__ import annotations

import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.app.services.graph_service import service_instance  # noqa: E402
from backend.app.validation import (  # noqa: E402
    ValidationPolicy,
    format_console_report,
    validate_networkx_graph,
)


def main():
    graph = service_instance.get_graph()
    policy = ValidationPolicy(check_baseline_counts=True)
    report = validate_networkx_graph(graph, policy=policy)
    report_text = format_console_report(report)
    print(report_text)
    sys.exit(0 if report.valid else 1)


if __name__ == "__main__":
    main()
