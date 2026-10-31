# Frontend Architecture & Visualization

## Overview

The RE:Flow frontend is an interactive, zero-build single-page application built with standard **HTML5**, **CSS3**, and **D3.js v7**. It is served directly by Flask from `backend/app/static/`, requiring no Node.js runtime, npm dependencies, or client-side bundlers.

```
backend/app/static/
├── sprint-1-demo.html      # Structural layout and modal dialogs
├── css/
│   └── sprint-1-demo.css   # Dark theme styles, responsive layout, animations
└── js/
    └── sprint-1-demo.js    # D3 force layout, event handlers, API integration
```

---

## Visual Design & Tier Encoding

Nodes are visually partitioned into distinct vertical hierarchical columns representing the four supply chain tiers:

| Tier | Category | Visual Badge Color | Accent Hex | Shape / Icon |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Suppliers | Emerald Green | `#10b981` | Hexagon / Warehouse |
| **Tier 2** | BOM Parts | Cyan | `#06b6d4` | Circle / Gear |
| **Tier 3** | Products | Indigo | `#6366f1` | Rounded Rect / Box |
| **Tier 4** | Orders | Amber | `#f59e0b` | Diamond / Cart |

Edges are rendered as directed SVG spline paths with directional arrowhead markers:
- `SUPPLIES`: Emerald dashed lines
- `USED_IN`: Cyan solid lines
- `FULFILLS`: Indigo solid lines

---

## Interactive Features

### 1. Blast Radius Downstream Highlighting
- Clicking on any node triggers a downstream BFS traversal query (`GET /api/downstream/<node_id>`).
- All reachable downstream nodes and connecting edges are highlighted with animated glowing pulses, while unaffected elements are softly dimmed.
- The sidebar immediately updates to display:
  - Visited node count and list.
  - Tier breakdown (count of impacted parts, products, orders).
  - Traversal execution latency (sub-millisecond).

### 2. Cascading Node Deletion & Simulation
- Clicking the **"Simulate Disruption"** button on an active node triggers `DELETE /api/node/<node_id>`.
- The backend cascades deletion to all dependent children. The D3 visualization smoothly removes the affected sub-tree with transition animations.
- The **Undo** button illuminates, enabling one-click restoration.

### 3. Undo & Graph Reset
- **Undo (`POST /api/undo`)**: Immediately restores the previous graph state from the backend undo stack without reloading the page.
- **Reset (`POST /api/reset`)**: Restores the canonical 19-node baseline graph and clears the undo stack.

### 4. Live Validation Audit Modal
- Clicking **"Run Validation"** queries `GET /api/validation`.
- Displays an interactive audit panel showing:
  - Overall status (`PASS` or `FAIL`).
  - Active validation mode (`baseline` or `integrity`).
  - Assertion check results table (`GRAPH_DIRECTED`, `GRAPH_ACYCLICITY`, `EDGE_REFERENCES`, `EDGE_DIRECTIONS`, `BASELINE_COUNTS`).
  - Detailed errors or warnings with suggested remediation actions.

### 5. SLA Latency Benchmark Widget
- Clicking **"Benchmark SLA"** queries `GET /api/benchmark/tracing`.
- Displays real-time traversal latency statistics:
  - p95 latency vs. the **10.0 ms SLA** limit.
  - Mean, median, and maximum observed traversal durations.
  - Compliance badge (`SLA MET: PASS`).

