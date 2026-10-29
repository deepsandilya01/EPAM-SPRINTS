# Team Photon — Frontend Validation & Interaction Guide

## 1. Overview & Current Frontend Architecture

The **Team Photon** frontend is a high-performance, single-page web application implemented in vanilla JavaScript and **D3.js (v7)** located at [`static/index.html`](../backend/static/index.html). It connects directly to the Flask backend to visualize the multi-tier supply-chain dependency network.

### 1.1 Rendering Technology & Design Principles
- **Visualization Library**: D3.js (v7.8.5) using standard SVG `<svg>` rendering.
- **Styling & Layout**: Custom modern dark-mode theme ("Photon Dark"), glassmorphism cards, and responsive CSS Grid/Flexbox.
- **Typography**: Inter and JetBrains Mono (via Google Fonts).
- **Layout Architecture**: 4-column tier layout separating graph entities from left to right:
  $$\text{Tier 0: Suppliers} \longrightarrow \text{Tier 1: Parts} \longrightarrow \text{Tier 2: Products} \longrightarrow \text{Tier 3: Customer Orders}$$
- **State Management**: Client-side graph model synchronized via asynchronous `fetch()` API calls against backend endpoints.

---

## 2. Implemented Frontend Features & Interaction Flow

The following features are **fully implemented and verified** in [`static/index.html`](../backend/static/index.html):

```
+-------------------------------------------------------------------------------+
|  HEADER: [Logo] Team Photon | LNCT Photon    [Undo (Disabled)] [Reset Graph]  |
+------------------------------------------------------+------------------------+
|                                                      |  SIDEBAR: Node Details |
|                                                      |  --------------------- |
|  SVG GRAPH CANVAS                                    |  Entity Badges         |
|  - 4 Tier Columns (Supplier -> Part -> Prod -> Order)|  Attributes & Values   |
|  - Force Simulation + Dragging                       |  [Impact Preview Box]  |
|  - Hover Tooltips & Downstream Highlight             |  [Delete Node Button]  |
|                                                      |                        |
+------------------------------------------------------+------------------------+
|  BOTTOM DOCK: Action Logs, Elapsed Times & Complexity Metrics  [Clear] [Toggle] |
+-------------------------------------------------------------------------------+
```

### 2.1 Graph Initialization & Loading Flow
1. On page load, `DOMContentLoaded` triggers `fetch('/api/graph')`.
2. The JSON payload (`{ nodes: [...], edges: [...] }`) is passed to `renderGraph()`.
3. Node positions are initialized based on tier index $X$-coordinates with initial vertical spacing.
4. A D3 force simulation (`d3.forceSimulation`) stabilizes node positions while maintaining horizontal column separation.
5. Zoom and pan behavior is bound to the primary SVG canvas via `d3.zoom()`.

### 2.2 Node Selection & Downstream Highlight
- **Click Event**: Clicking a node selects it as the active entity and opens the right-hand inspection sidebar.
- **Downstream Traversal Call**: The client invokes `fetch('/api/downstream/${d.id}')`.
- **Visual Highlighting**:
  - Selected root node: Pulsing amber halo.
  - Reachable downstream nodes: Illuminated with vivid cyan border.
  - Active downstream edges: Highlighted with directional stroke markers.
  - Unrelated nodes & edges: Dimmed to 15% opacity to minimize cognitive load.

### 2.3 Impact Preview & Cascade Analysis
- When a node is selected, the sidebar renders an **Impact Analysis** section:
  - Calls `fetch('/api/impact/${d.id}')` to retrieve non-mutating preview metadata.
  - Displays total count of affected downstream nodes and edges.
  - Lists exact downstream item identifiers and incident relations.
  - Displays theoretical time complexity: $\mathcal{O}(V + E)$.

### 2.4 Node Deletion & Cascading Removal
- Clicking **"Delete this node and all downstream"** triggers a confirmation modal.
- On confirmation, the client sends `DELETE /api/node/${d.id}`.
- The server performs cascade removal, returns the pruned graph, and pushes a snapshot to `UNDO_STACK`.
- The client re-renders the canvas with exit transitions and logs the deletion with elapsed milliseconds and complexity in the bottom dock.
- An undo floating toast appears with a 5-second countdown progress bar.

### 2.5 Undo & Reset Operations
- **Undo Button (`#btn-undo`)**: Sends `POST /api/undo`. Restores the previous graph state and re-enables/disables the button based on stack depth.
- **Reset Button (`#btn-reset`)**: Sends `POST /api/reset`. Restores the canonical 19-node baseline graph and clears the undo stack.

---

## 3. Validation API Contract (Frontend Readiness)

The backend exposes dedicated endpoints to support frontend validation and performance reporting. These contracts are verified by automated tests in [`tests/test_frontend_validation_contract.py`](../backend/tests/test_frontend_validation_contract.py):

### 3.1 Structure Validation Contract (`GET /api/validation`)

| Field | Type | Description |
|---|---|---|
| `valid` | `boolean` | Overall graph health (`true` if all checks pass, `false` if errors exist). |
| `graph_name` | `string` | Display name of the active dataset. |
| `mode` | `string` | Active policy mode: `"baseline"` or `"integrity"`. |
| `summary` | `object` | Entity counts: `node_count`, `edge_count`, `supplier_count`, `part_count`, `product_count`, `order_count`, `supplies_count`, `used_in_count`, `fulfills_count`. |
| `checks` | `array` | List of check objects containing `check_id`, `status` (`PASS`, `FAIL`, `WARN`, `SKIP`), and `message`. |
| `errors` | `array` | List of error objects containing `code`, `severity`, `message`, `entity_type`, and `suggested_action`. |
| `warnings` | `array` | List of non-fatal warnings (e.g. unconstrained policies). |
| `timestamp` | `string` | ISO 8601 evaluation timestamp. |

### 3.2 Performance Traversal Contract (`GET /api/benchmark/tracing?node_id=SUP-01`)

| Field | Type | Description |
|---|---|---|
| `source_node_id` | `string` | Root identifier tested (e.g., `"SUP-01"`). |
| `source_exists` | `boolean` | Whether the source node exists in the current graph. |
| `downstream_node_ids` | `array[string]` | Sorted list of all reachable descendant IDs. |
| `visited_count` | `integer` | Count of reachable downstream nodes. |
| `elapsed_ms` | `number` | High-resolution pure traversal duration in milliseconds. |
| `threshold_ms` | `number` | Configured SLA threshold (default: `10.0`). |
| `under_threshold` | `boolean` | Whether `elapsed_ms <= threshold_ms`. |
| `status` | `string` | `"PASS"` if under threshold, else `"FAIL"`. |
| `time_complexity` | `string` | Algorithmic notation (`"O(V + E)"`). |

---

## 4. Status Vocabulary & Interpretation

When displaying validation and benchmark results, the status codes carry specific meanings:

| Status | Meaning in Structure Validation | Meaning in Benchmark Tracing | UI Treatment |
|---|---|---|---|
| **`PASS`** | The rule is completely satisfied (e.g. zero cycles, exact baseline counts, all endpoints valid). | Pure traversal completed strictly below the 10.0 ms target. | Green badge (`#10b981`), checkmark icon. |
| **`FAIL`** | A structural constraint is violated (e.g. cycle detected, duplicate ID, invalid reference). | Traversal exceeded 10.0 ms or source node failed traversal. | Red badge (`#ef4444`), alert icon. |
| **`WARN`** | Non-breaking condition (e.g., policy left unspecified, post-deletion graph tested under baseline mode). | Traversal passed but within 80% of threshold. | Amber badge (`#f59e0b`), warning triangle. |
| **`SKIP` / `NOT RUN`** | Check was bypassed (e.g. baseline count check skipped in `integrity` mode). | Benchmark has not been executed yet for the selected node. | Slate badge (`#64748b`), dash icon. |

---

## 5. Proposed Frontend Validation Panel Extension

While the backend and contract tests are fully implemented and verified, integrating a dedicated validation dashboard into the frontend UI can be accomplished by adding a slide-out modal or sidebar tab.

### 5.1 Architecture of the Proposed UI Panel
```html
<!-- Proposed Validation Panel Component -->
<div id="validation-panel" class="panel-slideout" style="display: none;">
  <div class="panel-header">
    <h3>Graph Validation & Health</h3>
    <button id="btn-close-validation">&times;</button>
  </div>
  
  <div class="panel-body">
    <!-- Overall Health Badge -->
    <div id="val-overall-status" class="status-card">
      <span class="status-indicator">NOT RUN</span>
      <span class="status-label">Graph Integrity Check</span>
    </div>

    <!-- Entity Summary Counts Grid -->
    <div class="counts-grid">
      <div class="count-item"><span>Suppliers</span><strong id="val-cnt-sup">-</strong></div>
      <div class="count-item"><span>Parts</span><strong id="val-cnt-part">-</strong></div>
      <div class="count-item"><span>Products</span><strong id="val-cnt-prod">-</strong></div>
      <div class="count-item"><span>Orders</span><strong id="val-cnt-ord">-</strong></div>
    </div>

    <!-- Per-Check Rule List -->
    <div id="val-checks-list" class="checks-container"></div>

    <!-- Quick Benchmark Trigger -->
    <div class="benchmark-box">
      <h4>Downstream Traversal SLA (< 10 ms)</h4>
      <select id="val-bench-node">
        <option value="SUP-01">SUP-01 (Apex Components)</option>
        <option value="SUP-02">SUP-02 (Bharat Precision)</option>
      </select>
      <button id="btn-run-benchmark" class="btn btn--sm">Run Benchmark</button>
      <div id="val-bench-result" class="bench-result-text"></div>
    </div>
  </div>
</div>
```

### 5.2 JavaScript Fetch & XSS-Safe DOM Population
```javascript
async function fetchAndRenderValidation(mode = 'baseline') {
  try {
    const res = await fetch(`/api/validation?mode=${mode}`);
    const data = await res.json();
    
    // Update overall badge
    const badge = document.getElementById('val-overall-status');
    badge.className = data.valid ? 'status-card pass' : 'status-card fail';
    badge.textContent = data.valid ? 'STATUS: PASS' : 'STATUS: FAIL';

    // Populate counts safely using textContent (prevent XSS)
    document.getElementById('val-cnt-sup').textContent = data.summary.supplier_count;
    document.getElementById('val-cnt-part').textContent = data.summary.part_count;
    document.getElementById('val-cnt-prod').textContent = data.summary.product_count;
    document.getElementById('val-cnt-ord').textContent = data.summary.order_count;

    // Render individual checks safely
    const container = document.getElementById('val-checks-list');
    container.replaceChildren(); // clear previous
    
    data.checks.forEach(check => {
      const row = document.createElement('div');
      row.className = `check-row check-${check.status.toLowerCase()}`;
      
      const statusSpan = document.createElement('span');
      statusSpan.className = 'badge';
      statusSpan.textContent = check.status;
      
      const msgSpan = document.createElement('span');
      msgSpan.textContent = `${check.check_id}: ${check.message}`;
      
      row.appendChild(statusSpan);
      row.appendChild(msgSpan);
      container.appendChild(row);
    });
  } catch (err) {
    console.error('Validation fetch failed:', err);
  }
}
```

---

## 6. Testing & Troubleshooting Frontend Integration

### 6.1 Testing Frontend / Backend Contract
Run the automated contract test suite to verify that the backend produces the exact payload format the frontend expects:
```powershell
pytest tests/test_frontend_validation_contract.py -v
```

### 6.2 Manual Verification Steps in Browser
1. Start Flask: `python app.py`.
2. Open DevTools (F12) $\to$ **Console** and **Network** tabs.
3. In Console, test the validation API:
   ```javascript
   fetch('/api/validation').then(r => r.json()).then(console.log);
   ```
4. Verify HTTP 200 response containing `valid: true` and 8 check items.
5. In Console, test the benchmark API:
   ```javascript
   fetch('/api/benchmark/tracing?node_id=SUP-01').then(r => r.json()).then(console.log);
   ```
6. Verify `elapsed_ms < 10.0` and `under_threshold: true`.

### 6.3 Common Troubleshooting Scenarios
- **D3 Graph Canvas Blank**: Check if `/api/graph` returned 200 with non-empty `nodes` and `edges`. Inspect console for syntax errors in SVG container sizing.
- **Node Clicks Do Not Highlight**: Confirm the `id` in the node datum matches the parameter passed to `/api/downstream/<node_id>`.
- **Validation Reports False After Node Deletion**: If a node is deleted, calling `/api/validation?mode=baseline` will report `FAIL` because node count is less than 19. Request `mode=integrity` to validate structural consistency after user edits.

