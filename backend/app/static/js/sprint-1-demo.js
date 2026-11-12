/* ═══════════════════════════════════════════════
     Constants & colour mapping
     ═══════════════════════════════════════════════ */
const COLOR = {
  supplier: '#D6436E',
  part: '#F5A623',
  product: '#1AABB8',
  order: '#2C5F8A',
};
const RADIUS = {
  supplier: 26,
  part: 22,
  product: 28,
  order: 20,
};
const COLUMN_X = { supplier: 0, part: 1, product: 2, order: 3 };
const COLUMNS = 4;

let graphData = { nodes: [], edges: [] };
let selectedNode = null;
let highlightedIds = new Set();

/* Serverless backend is stateless → the browser keeps delete/undo state */
let removedIds = [];     // all node ids currently removed from the graph
let undoStack = [];     // [{ ids, node_id, label, kind, edges_removed, elapsed_ms, complexity }]
const removedQS = () => removedIds.length ? `?removed=${encodeURIComponent(removedIds.join(','))}` : '';

/* ═══════════════════════════════════════════════
   Fetch graph data
   ═══════════════════════════════════════════════ */
async function fetchGraph() {
  const res = await fetch('/api/graph' + removedQS());
  graphData = await res.json();
  render();
}

/* ═══════════════════════════════════════════════
   Layout — deterministic column-based positioning
   ═══════════════════════════════════════════════ */
function computeLayout(nodes, width, height) {
  const isDockMinimized = document.getElementById('bottom-output-panel')?.classList.contains('minimized');
  const bottomPad = isDockMinimized ? 65 : 225;
  const pad = { top: 55, bottom: bottomPad, left: 100, right: 100 };
  const usableW = width - pad.left - pad.right;
  const usableH = height - pad.top - pad.bottom;
  const colWidth = usableW / (COLUMNS - 1);

  // Group by kind
  const groups = { supplier: [], part: [], product: [], order: [] };
  nodes.forEach(n => groups[n.kind]?.push(n));

  const positions = {};
  for (const [kind, list] of Object.entries(groups)) {
    const col = COLUMN_X[kind];
    const x = pad.left + col * colWidth;
    const gap = usableH / (list.length + 1);
    list.forEach((n, i) => {
      positions[n.id] = { x, y: pad.top + gap * (i + 1) };
    });
  }
  return positions;
}

/* ═══════════════════════════════════════════════
   Render
   ═══════════════════════════════════════════════ */
function render() {
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();

  const container = document.getElementById('graph-container');
  const width = container.clientWidth;
  const height = container.clientHeight;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  const positions = computeLayout(graphData.nodes, width, height);

  // ── Defs: arrowheads & glow filter ──
  const defs = svg.append('defs');

  // Per-kind arrow markers
  for (const [kind, col] of Object.entries(COLOR)) {
    defs.append('marker')
      .attr('id', `arrow-${kind}`)
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 28).attr('refY', 5)
      .attr('markerWidth', 7).attr('markerHeight', 7)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,0 L10,5 L0,10 Z')
      .attr('fill', col);
  }

  // Default dim arrow
  defs.append('marker')
    .attr('id', 'arrow-dim')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 28).attr('refY', 5)
    .attr('markerWidth', 7).attr('markerHeight', 7)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,0 L10,5 L0,10 Z')
    .attr('fill', 'rgba(255,255,255,0.12)');

  // Glow filter
  const filter = defs.append('filter').attr('id', 'glow').attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%');
  filter.append('feGaussianBlur').attr('stdDeviation', '6').attr('result', 'blur');
  filter.append('feMerge').selectAll('feMergeNode').data(['blur', 'SourceGraphic']).enter().append('feMergeNode').attr('in', d => d);

  // ── Edge group ──
  const edgeG = svg.append('g').attr('class', 'edges-layer');

  const edgeEls = edgeG.selectAll('.edge-line')
    .data(graphData.edges)
    .enter()
    .append('path')
    .attr('class', 'edge-line')
    .attr('d', d => {
      const s = positions[d.source];
      const t = positions[d.target];
      if (!s || !t) return '';
      const dx = t.x - s.x;
      return `M${s.x},${s.y} C${s.x + dx * 0.45},${s.y} ${t.x - dx * 0.45},${t.y} ${t.x},${t.y}`;
    })
    .attr('marker-end', 'url(#arrow-dim)')
    .each(function (d) { d._el = this; });

  // ── Node group ──
  const nodeG = svg.append('g').attr('class', 'nodes-layer');

  const nodeGroups = nodeG.selectAll('.node-group')
    .data(graphData.nodes.filter(n => positions[n.id]))
    .enter()
    .append('g')
    .attr('class', 'node-group')
    .attr('transform', d => `translate(${positions[d.id].x}, ${positions[d.id].y})`)
    .each(function (d) { d._el = this; });

  // Outer glow circle
  nodeGroups.append('circle')
    .attr('class', 'node-glow')
    .attr('r', d => RADIUS[d.kind] + 10)
    .attr('fill', d => COLOR[d.kind])
    .attr('opacity', 0);

  // Main circle
  nodeGroups.append('circle')
    .attr('class', 'node-circle')
    .attr('r', d => RADIUS[d.kind])
    .attr('fill', d => COLOR[d.kind])
    .style('color', d => COLOR[d.kind]);

  // Label
  nodeGroups.append('text')
    .attr('class', 'node-label')
    .attr('dy', '0.35em')
    .text(d => d.id);

  // ── Interactions ──
  nodeGroups
    .on('mouseenter', function (event, d) { showTooltip(event, d); })
    .on('mousemove', function (event) { moveTooltip(event); })
    .on('mouseleave', function () { hideTooltip(); })
    .on('click', function (event, d) { handleNodeClick(d, positions); event.stopPropagation(); });

  svg.on('click', () => clearSelection());

  updateSubtitle();
  updateUndoBtn();
}

/* ═══════════════════════════════════════════════
   Tooltip
   ═══════════════════════════════════════════════ */
const tooltip = document.getElementById('tooltip');

function showTooltip(event, d) {
  const kindColors = { supplier: COLOR.supplier, part: COLOR.part, product: COLOR.product, order: COLOR.order };
  const kindBg = { supplier: 'rgba(214,67,110,0.18)', part: 'rgba(245,166,35,0.18)', product: 'rgba(26,171,184,0.18)', order: 'rgba(44,95,138,0.18)' };

  let rows = '';
  const skip = new Set(['id', 'kind', 'label', '_el']);
  for (const [k, v] of Object.entries(d)) {
    if (skip.has(k)) continue;
    const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    rows += `<div class="tt-row"><span class="tt-label">${label}</span><span class="tt-value">${v}</span></div>`;
  }

  tooltip.innerHTML = `
      <div class="tt-title">${d.label || d.id}</div>
      <span class="tt-kind" style="background:${kindBg[d.kind]};color:${kindColors[d.kind]}">${d.kind}</span>
      ${rows}
    `;
  tooltip.classList.add('visible');
  moveTooltip(event);
}
function moveTooltip(event) {
  const pad = 16;
  let x = event.clientX + pad;
  let y = event.clientY + pad;
  if (x + 320 > window.innerWidth) x = event.clientX - 330;
  if (y + 260 > window.innerHeight) y = event.clientY - 270;
  tooltip.style.left = x + 'px';
  tooltip.style.top = y + 'px';
}
function hideTooltip() { tooltip.classList.remove('visible'); }

/* ═══════════════════════════════════════════════
   Node Click → highlight downstream & update Bottom Output Box
   ═══════════════════════════════════════════════ */
async function handleNodeClick(d, positions) {
  selectedNode = d;

  // Fetch downstream from server (computed by NetworkX)
  const res = await fetch(`/api/downstream/${d.id}${removedQS()}`);
  const data = await res.json();

  highlightedIds = new Set([d.id, ...data.downstream]);

  // Dim everything, then highlight
  d3.selectAll('.node-circle').classed('dimmed', n => !highlightedIds.has(n.id));
  d3.selectAll('.node-label').classed('dimmed', n => !highlightedIds.has(n.id));
  d3.selectAll('.node-glow').classed('active', n => highlightedIds.has(n.id));

  d3.selectAll('.edge-line')
    .classed('dimmed', e => !highlightedIds.has(e.source) && !highlightedIds.has(e.target))
    .classed('highlighted', e => highlightedIds.has(e.source) && highlightedIds.has(e.target))
    .each(function (e) {
      const isHl = highlightedIds.has(e.source) && highlightedIds.has(e.target);
      if (isHl) {
        // Figure out the target kind to pick arrow color
        const targetNode = graphData.nodes.find(n => n.id === e.target);
        const kind = targetNode ? targetNode.kind : 'dim';
        d3.select(this)
          .attr('stroke', COLOR[kind] || 'rgba(255,255,255,0.12)')
          .attr('marker-end', `url(#arrow-${kind})`);
      } else {
        d3.select(this)
          .attr('stroke', null)
          .attr('marker-end', 'url(#arrow-dim)');
      }
    });

  openInfoPanel(d, data.downstream);
  updateImpactPreview(d, data.downstream);
}

function clearSelection() {
  selectedNode = null;
  highlightedIds.clear();
  d3.selectAll('.node-circle').classed('dimmed', false);
  d3.selectAll('.node-label').classed('dimmed', false);
  d3.selectAll('.node-glow').classed('active', false);
  d3.selectAll('.edge-line')
    .classed('dimmed', false)
    .classed('highlighted', false)
    .attr('stroke', null)
    .attr('marker-end', 'url(#arrow-dim)');
  closeInfoPanel();
  initDefaultImpactPreview();
}

/* ═══════════════════════════════════════════════
   Bottom Output Box — Impact Preview Logic
   ═══════════════════════════════════════════════ */
function initDefaultImpactPreview() {
  const badge = document.getElementById('impact-target-badge');
  if (badge) badge.style.display = 'none';

  const container = document.getElementById('impact-preview-body');
  if (!container) return;
  container.innerHTML = `
      <div class="impact-card-empty">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--col-product);flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <div>
          <div><strong>Select any node</strong> in the graph above to preview what will happen if it is deleted.</div>
          <div style="font-size:0.69rem;color:var(--text-secondary);margin-top:3px;">
            In this supply chain, deleting an entity removes it and cuts its consecutive connected edges. Downstream dependencies cascade in <span class="complexity-tag">O(V + E)</span> time.
          </div>
        </div>
      </div>
    `;
}

function updateImpactPreview(d, downstreamIds) {
  const badge = document.getElementById('impact-target-badge');
  const container = document.getElementById('impact-preview-body');
  if (!container) return;

  const kindColors = { supplier: COLOR.supplier, part: COLOR.part, product: COLOR.product, order: COLOR.order };
  const kindBg = { supplier: 'rgba(214,67,110,0.18)', part: 'rgba(245,166,35,0.18)', product: 'rgba(26,171,184,0.18)', order: 'rgba(44,95,138,0.18)' };

  if (badge) {
    badge.style.display = 'inline-flex';
    badge.innerHTML = `Selected: <span style="color:${kindColors[d.kind]}">${d.id} (${d.label || d.id})</span>`;
  }

  // Direct consecutive edges
  const outgoing = graphData.edges.filter(e => e.source === d.id);
  const incoming = graphData.edges.filter(e => e.target === d.id);
  const consecutiveEdges = [...outgoing, ...incoming];

  // Downstream entities
  const downstreamNodes = graphData.nodes.filter(n => downstreamIds.includes(n.id) && n.id !== d.id);
  const byKind = { supplier: [], part: [], product: [], order: [] };
  downstreamNodes.forEach(n => byKind[n.kind]?.push(n));

  let edgePills = outgoing.map(e => `<span class="impact-pill" style="border-left:2px solid ${COLOR[d.kind]}">${e.source} ➔ ${e.target}</span>`).join(' ');
  if (incoming.length) {
    edgePills += ' ' + incoming.map(e => `<span class="impact-pill" style="opacity:0.8">${e.source} ➔ ${e.target}</span>`).join(' ');
  }
  if (!edgePills) edgePills = '<span style="color:var(--text-secondary);font-size:0.68rem">No connected edges</span>';

  let affectedPills = '';
  ['part', 'product', 'order'].forEach(k => {
    if (byKind[k]?.length) {
      affectedPills += byKind[k].map(n => `<span class="impact-pill" style="color:${COLOR[k]};background:rgba(255,255,255,0.06)">${n.id}</span>`).join(' ') + ' ';
    }
  });
  if (!affectedPills) affectedPills = '<span style="color:var(--text-secondary);font-size:0.68rem">None (Leaf node)</span>';

  const totalNodesAffected = 1 + downstreamNodes.length;
  const totalEdgesAffected = consecutiveEdges.length;

  container.innerHTML = `
      <div class="impact-grid">
        <div class="impact-box">
          <span class="impact-box-label">Target Entity Deletion</span>
          <div class="impact-box-val">
            <span class="impact-pill" style="background:${kindBg[d.kind]};color:${kindColors[d.kind]}">${d.kind.toUpperCase()}</span>
            <span>${d.id} — ${d.label || d.id}</span>
          </div>
          <span style="font-size:0.65rem;color:var(--text-secondary)">This node will be permanently excised from NetworkX.</span>
        </div>

        <div class="impact-box">
          <span class="impact-box-label">Consecutive Connected Edges (${consecutiveEdges.length})</span>
          <div class="impact-box-val">${edgePills}</div>
          <span style="font-size:0.65rem;color:var(--text-secondary)">Incident edges will be severed immediately.</span>
        </div>

        <div class="impact-box">
          <span class="impact-box-label">Downstream Affected Cascade (${downstreamNodes.length})</span>
          <div class="impact-box-val">${affectedPills}</div>
          <span style="font-size:0.65rem;color:var(--text-secondary)">Dependent parts, products, and customer orders disrupted.</span>
        </div>

        <div class="impact-box" style="border-color:rgba(26,171,184,0.3);background:rgba(26,171,184,0.04)">
          <span class="impact-box-label" style="color:#7dd3fc">Algorithmic Time Complexity</span>
          <div class="impact-box-val">
            <span class="complexity-tag">O(V + E)</span>
            <span style="font-size:0.68rem;color:var(--text-secondary)">Linear DAG Traversal</span>
          </div>
          <span style="font-size:0.65rem;color:var(--text-secondary)">Visits ${totalNodesAffected} vertices and ${totalEdgesAffected} incident edges.</span>
        </div>
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:2px;">
        <span style="font-size:0.68rem;color:var(--text-secondary)">Ready to delete this supply-chain branch?</span>
        <button class="btn btn--danger btn--sm" id="btn-dock-quick-delete" style="padding:4px 12px;font-size:0.72rem">
          Delete Node ${d.id}
        </button>
      </div>
    `;

  document.getElementById('btn-dock-quick-delete')?.addEventListener('click', () => confirmDelete(d));
}

/* ═══════════════════════════════════════════════
   Info Panel (Right sidebar)
   ═══════════════════════════════════════════════ */
function openInfoPanel(d, downstream) {
  const panel = document.getElementById('info-panel');
  const content = document.getElementById('panel-content');
  const kindColors = { supplier: COLOR.supplier, part: COLOR.part, product: COLOR.product, order: COLOR.order };
  const kindBg = { supplier: 'rgba(214,67,110,0.18)', part: 'rgba(245,166,35,0.18)', product: 'rgba(26,171,184,0.18)', order: 'rgba(44,95,138,0.18)' };

  let rows = '';
  const skip = new Set(['id', 'kind', 'label', '_el']);
  for (const [k, v] of Object.entries(d)) {
    if (skip.has(k)) continue;
    const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    rows += `<div class="panel-row"><span class="panel-label">${label}</span><span class="panel-value">${v}</span></div>`;
  }

  const downstreamCount = downstream.length;

  content.innerHTML = `
      <div class="panel-title">${d.label || d.id}</div>
      <span class="panel-kind" style="background:${kindBg[d.kind]};color:${kindColors[d.kind]}">${d.kind}</span>
      ${rows}
      <div class="panel-row" style="margin-top:8px;border-top:1px solid var(--border-glass);padding-top:8px;">
        <span class="panel-label">Downstream nodes</span>
        <span class="panel-value">${downstreamCount}</span>
      </div>
      <div class="panel-actions">
        <button class="btn btn--danger" id="btn-delete-node" title="Delete this node and all downstream">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          Delete node
        </button>
      </div>
    `;

  document.getElementById('btn-delete-node').addEventListener('click', () => confirmDelete(d));
  panel.classList.add('open');
}

function closeInfoPanel() {
  document.getElementById('info-panel').classList.remove('open');
}
document.getElementById('panel-close-btn').addEventListener('click', () => { closeInfoPanel(); clearSelection(); });

/* ═══════════════════════════════════════════════
   Delete with confirmation
   ═══════════════════════════════════════════════ */
function confirmDelete(d) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
      <div class="modal-box">
        <h3>Delete "${d.label || d.id}"?</h3>
        <p>This will permanently remove the node <strong>${d.id}</strong> and <em>all consecutive connected edges &amp; downstream dependencies</em> from the NetworkX graph. You can undo this action.</p>
        <div class="modal-actions">
          <button class="btn" id="modal-cancel">Cancel</button>
          <button class="btn btn--danger" id="modal-confirm">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            Delete
          </button>
        </div>
      </div>
    `;
  document.body.appendChild(overlay);

  document.getElementById('modal-cancel').addEventListener('click', () => overlay.remove());
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });

  document.getElementById('modal-confirm').addEventListener('click', async () => {
    overlay.remove();
    const res = await fetch(`/api/node/${d.id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ removed: removedIds })
    });
    const result = await res.json();
    if (result.error) { showToast(`Error: ${result.error}`); return; }
    graphData = result.graph;
    removedIds = removedIds.concat(result.deleted);
    undoStack.push({
      ids: result.deleted,
      node_id: result.deleted_node_id,
      label: result.deleted_label,
      kind: result.deleted_kind,
      details: result.deleted_details,
      edges_removed: result.edges_removed,
      elapsed_ms: result.elapsed_ms,
      complexity: result.time_complexity,
      complexity_details: result.time_complexity_details
    });
    closeInfoPanel();
    clearSelection();
    render();
    showToast(`Deleted ${result.deleted.length} node(s)`);

    // Add to dock operation log
    addLogEntry('delete', {
      id: d.id,
      label: d.label || d.id,
      kind: d.kind,
      nodeCount: result.deleted.length,
      edgeCount: result.edges_removed,
      elapsed_ms: result.elapsed_ms,
      complexity: result.time_complexity || 'O(V + E)'
    });
  });
}

/* ═══════════════════════════════════════════════
   Undo — Displays 5-second popup with Time Complexity and Deletion Timing
   ═══════════════════════════════════════════════ */
document.getElementById('btn-undo').addEventListener('click', async () => {
  if (!undoStack.length) { showToast('Nothing to undo'); return; }
  const snap = undoStack.pop();
  const remaining = removedIds.filter(id => !snap.ids.includes(id));
  const res = await fetch('/api/undo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ removed: remaining })
  });
  const data = await res.json();
  if (data.error) { undoStack.push(snap); showToast(data.error); return; }
  removedIds = remaining;
  Object.assign(data, {
    restored_node_id: snap.node_id,
    restored_label: snap.label,
    restored_kind: snap.kind,
    deleted_details: snap.details,
    edges_removed: snap.edges_removed,
    delete_elapsed_ms: snap.elapsed_ms,
    time_complexity: snap.complexity,
    time_complexity_details: snap.complexity_details
  });
  graphData = data.graph;
  closeInfoPanel();
  clearSelection();
  render();
  showToast('Undo successful — Node restored');

  // Add to dock operation log
  addLogEntry('undo', {
    id: data.restored_node_id || 'Node',
    label: data.restored_label || '',
    undo_elapsed_ms: data.undo_elapsed_ms,
    delete_elapsed_ms: data.delete_elapsed_ms,
    complexity: data.time_complexity || 'O(V + E)'
  });

  // 5-SECOND POPUP SHOWING TIME COMPLEXITY & HOW MUCH TIME WAS TAKEN TO DELETE THAT NODE
  showUndoTimingPopup(data);
});

/* ═══════════════════════════════════════════════
   Reset
   ═══════════════════════════════════════════════ */
document.getElementById('btn-reset').addEventListener('click', async () => {
  const res = await fetch('/api/reset', { method: 'POST' });
  const data = await res.json();
  removedIds = [];
  undoStack = [];
  graphData = data.graph;
  closeInfoPanel();
  clearSelection();
  render();
  showToast('Graph reset to original 19 nodes');
  addLogEntry('reset', { nodeCount: graphData.nodes.length });
});

/* ═══════════════════════════════════════════════
   Toast notifications
   ═══════════════════════════════════════════════ */
function showToast(msg) {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 2800);
}

/* ═══════════════════════════════════════════════
   Subtitle counts
   ═══════════════════════════════════════════════ */
function updateSubtitle() {
  const counts = { supplier: 0, part: 0, product: 0, order: 0 };
  graphData.nodes.forEach(n => counts[n.kind]++);
  document.getElementById('graph-subtitle').textContent =
    `${graphData.nodes.length} entities  ·  ${counts.supplier} suppliers  ·  ${counts.part} parts  ·  ${counts.product} products  ·  ${counts.order} orders  ·  ${graphData.edges.length} edges`;
}

function updateUndoBtn() {
  document.getElementById('btn-undo').disabled = !undoStack.length;
}

/* ═══════════════════════════════════════════════
   Resize handler
   ═══════════════════════════════════════════════ */
window.addEventListener('resize', () => { if (graphData.nodes.length) render(); });

/* ═══════════════════════════════════════════════
   Dock Log History
   ═══════════════════════════════════════════════ */
const logList = document.getElementById('dock-log-list');

function addLogEntry(action, details) {
  if (!logList) return;
  const item = document.createElement('div');
  const now = new Date().toLocaleTimeString();

  if (action === 'delete') {
    item.className = 'log-item delete';
    item.innerHTML = `
        <div class="log-item-header">
          <span class="log-item-action" style="color:var(--col-supplier)">✕ DELETED: ${details.id} (${details.label})</span>
          <span class="log-item-time">${now}</span>
        </div>
        <div style="font-size:0.69rem;color:var(--text-secondary);margin-top:2px;">
          Removed <strong>${details.nodeCount}</strong> nodes &amp; <strong>${details.edgeCount}</strong> edges in <strong style="color:#7dd3fc">${details.elapsed_ms.toFixed(3)} ms</strong> · <span class="complexity-tag">${details.complexity}</span>
        </div>
      `;
  } else if (action === 'undo') {
    item.className = 'log-item undo';
    item.innerHTML = `
        <div class="log-item-header">
          <span class="log-item-action" style="color:var(--col-product)">↺ UNDO: Restored ${details.id} (${details.label})</span>
          <span class="log-item-time">${now}</span>
        </div>
        <div style="font-size:0.69rem;color:var(--text-secondary);margin-top:2px;">
          Restored in <strong style="color:#7dd3fc">${details.undo_elapsed_ms.toFixed(3)} ms</strong> · Original delete took <strong style="color:var(--col-supplier)">${details.delete_elapsed_ms.toFixed(3)} ms</strong> · <span class="complexity-tag">${details.complexity}</span>
        </div>
      `;
  } else if (action === 'reset') {
    item.className = 'log-item reset';
    item.innerHTML = `
        <div class="log-item-header">
          <span class="log-item-action" style="color:var(--col-part)">⟳ RESET: All 19 Entities Restored</span>
          <span class="log-item-time">${now}</span>
        </div>
        <div style="font-size:0.69rem;color:var(--text-secondary);margin-top:2px;">
          Graph re-initialized to default state with 19 nodes and 18 edges.
        </div>
      `;
  }

  logList.prepend(item);
}

document.getElementById('btn-dock-clear')?.addEventListener('click', () => {
  if (logList) logList.innerHTML = '<div style="font-size:0.7rem;color:var(--text-secondary);padding:6px 0;">Log cleared.</div>';
});

// Dock Minimize/Expand button
const dockPanel = document.getElementById('bottom-output-panel');
const dockToggleBtn = document.getElementById('btn-dock-toggle');
dockToggleBtn?.addEventListener('click', () => {
  dockPanel.classList.toggle('minimized');
  const isMin = dockPanel.classList.contains('minimized');
  document.getElementById('dock-toggle-icon').textContent = isMin ? '+' : '−';
  document.getElementById('dock-toggle-text').textContent = isMin ? 'Expand' : 'Minimize';
  render();
});

/* ═══════════════════════════════════════════════
   5-SECOND UNDO TIMING & COMPLEXITY POPUP
   ═══════════════════════════════════════════════ */
let undoPopupTimer = null;
let undoCountdownInterval = null;

function showUndoTimingPopup(data) {
  const popup = document.getElementById('undo-timing-popup');
  if (!popup) return;

  // 1. Restored node details
  const nodeEl = document.getElementById('undo-stat-node');
  if (nodeEl) {
    const label = data.restored_label || data.restored_node_id || 'Node';
    const id = data.restored_node_id || '';
    nodeEl.innerHTML = `<span class="impact-pill" style="color:var(--col-product);background:rgba(26,171,184,0.15)">${id}</span> ${label}`;
  }

  // 2. How much time was taken to delete that node
  const deleteTimeEl = document.getElementById('undo-stat-delete-time');
  if (deleteTimeEl) {
    const deleteMs = (data.delete_elapsed_ms || 0).toFixed(3);
    deleteTimeEl.textContent = `${deleteMs} ms`;
  }

  // 3. Time complexity
  const complexityEl = document.getElementById('undo-stat-complexity');
  if (complexityEl) {
    complexityEl.textContent = data.time_complexity || 'O(V + E)';
  }
  const complexityDescEl = document.getElementById('undo-stat-complexity-desc');
  if (complexityDescEl) {
    complexityDescEl.textContent = data.time_complexity_details || 'NetworkX BFS graph traversal & cascading deletion';
  }

  // 4. Undo restoration time
  const undoTimeEl = document.getElementById('undo-stat-undo-time');
  if (undoTimeEl) {
    const undoMs = (data.undo_elapsed_ms || 0).toFixed(3);
    undoTimeEl.textContent = `${undoMs} ms`;
  }

  // 5. Entities restored count
  const countEl = document.getElementById('undo-stat-count');
  if (countEl) {
    const n = data.deleted_details ? data.deleted_details.length : 1;
    const e = data.edges_removed || 0;
    countEl.textContent = `${n} node(s), ${e} edge(s)`;
  }

  // Restart progress bar animation
  const bar = document.getElementById('undo-progress-bar');
  if (bar) {
    bar.style.animation = 'none';
    bar.offsetHeight; // force reflow
    bar.style.animation = 'undoProgressShrink 5s linear forwards';
  }

  // 5-second countdown ticker
  const timerTag = document.getElementById('undo-timer-countdown');
  let timeLeft = 5.0;
  if (timerTag) timerTag.textContent = '5.0s';

  if (undoCountdownInterval) clearInterval(undoCountdownInterval);
  undoCountdownInterval = setInterval(() => {
    timeLeft = Math.max(0, timeLeft - 0.1);
    if (timerTag) timerTag.textContent = `${timeLeft.toFixed(1)}s`;
    if (timeLeft <= 0) {
      clearInterval(undoCountdownInterval);
      undoCountdownInterval = null;
    }
  }, 100);

  // Make visible
  popup.classList.add('visible');

  // Auto-dismiss after EXACTLY 5 seconds (5000 ms)
  if (undoPopupTimer) clearTimeout(undoPopupTimer);
  undoPopupTimer = setTimeout(() => {
    popup.classList.remove('visible');
    undoPopupTimer = null;
    if (undoCountdownInterval) {
      clearInterval(undoCountdownInterval);
      undoCountdownInterval = null;
    }
  }, 5000);
}

/* ═══════════════════════════════════════════════
   Init
   ═══════════════════════════════════════════════ */
initDefaultImpactPreview();
fetchGraph();
