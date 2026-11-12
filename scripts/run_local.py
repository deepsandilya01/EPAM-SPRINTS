from __future__ import annotations

import os
import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.app.main import app  # noqa: E402

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print("=" * 60)
    print(f"  RE:Flow Supply Chain Engine running on http://127.0.0.1:{port}")
    print(f"  Interactive Demo UI : http://127.0.0.1:{port}/")
    print(f"  Graph API           : http://127.0.0.1:{port}/api/graph")
    print(f"  Validation Audit    : http://127.0.0.1:{port}/api/validation")
    print(f"  Benchmark API       : http://127.0.0.1:{port}/api/benchmark/tracing")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=True)
