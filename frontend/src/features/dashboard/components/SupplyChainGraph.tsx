"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import * as d3 from "d3";
import { Network, RotateCcw, Trash2, Undo2, X } from "lucide-react";

import { dashboardApi } from "@/features/dashboard/services/dashboardApi";
import {
  deleteGraphNodeThunk,
  resetGraphThunk,
  undoGraphThunk,
} from "@/features/dashboard/slices/dashboardSlice";
import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { EmptyState } from "@/features/shared/components/EmptyState";
import type { GraphEdge, GraphNode } from "@/features/shared/types/graph";
import type { SimulationResponse } from "@/features/shared/types/simulation";
import { useAppDispatch, useAppSelector } from "@/store";

interface SupplyChainGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  simulation?: SimulationResponse | null;
}

interface PositionedNode {
  node: GraphNode;
  x: number;
  y: number;
}

interface HoverTooltipState {
  visible: boolean;
  x: number;
  y: number;
  node: GraphNode | null;
}

const TIER_ORDER: Record<string, number> = {
  supplier: 0,
  part: 1,
  product: 2,
  order: 3,
};

const TIER_LABELS = [
  "Tier 1 · Suppliers",
  "Tier 2 · BOM Parts",
  "Tier 3 · Finished Products",
  "Tier 4 · Customer Orders",
];

function getNodeTier(node: GraphNode): "supplier" | "part" | "product" | "order" {
  const raw = String(node.kind || node.tier || "").toLowerCase();
  if (raw === "supplier" || raw === "part" || raw === "product" || raw === "order") {
    return raw;
  }
  if (node.id.startsWith("SUP-")) return "supplier";
  if (node.id.startsWith("PART-") || node.id.startsWith("P-")) return "part";
  if (node.id.startsWith("PROD-")) return "product";
  return "order";
}

export function SupplyChainGraph({
  nodes,
  edges,
  simulation = null,
}: SupplyChainGraphProps) {
  const dispatch = useAppDispatch();
  const { canUndo, graphLoading, connectionStatus } = useAppSelector(
    (state) => state.dashboard
  );

  const containerRef = useRef<HTMLDivElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const [dimensions, setDimensions] = useState({ width: 920, height: 470 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [downstreamIds, setDownstreamIds] = useState<string[]>([]);
  const [loadingDownstream, setLoadingDownstream] = useState(false);
  const [tooltip, setTooltip] = useState<HoverTooltipState>({
    visible: false,
    x: 0,
    y: 0,
    node: null,
  });

  const simulationOverlay = useMemo(() => {
    if (!simulation) {
      return {
        active: false,
        breachedOrders: new Set<string>(),
        criticalPart: null as string | null,
        impactedNodes: new Set<string>(),
      };
    }

    const breachedOrders = new Set(
      simulation.stockout.breached_orders.map((b) => b.order_id)
    );
    const criticalPart =
      simulation.critical_part?.part_id ?? simulation.stockout.part_id ?? null;
    const impactedNodes = new Set<string>([
      simulation.impact.disrupted_supplier,
      ...simulation.impact.affected_parts,
      ...simulation.impact.affected_products,
      ...simulation.impact.affected_orders,
    ]);

    return {
      active: true,
      breachedOrders,
      criticalPart,
      impactedNodes,
    };
  }, [simulation]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const updateSize = () => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0) {
        setDimensions({
          width: Math.max(540, Math.floor(rect.width)),
          height: rect.width < 640 ? 430 : 470,
        });
      }
    };

    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(el);
    return () => observer.disconnect();
  }, [nodes.length]);

  const positions = useMemo(() => {
    const groups: Record<"supplier" | "part" | "product" | "order", GraphNode[]> = {
      supplier: [],
      part: [],
      product: [],
      order: [],
    };
    for (const n of nodes) {
      groups[getNodeTier(n)].push(n);
    }

    const pad = { top: 46, bottom: 24, left: 72, right: 72 };
    const usableW = dimensions.width - pad.left - pad.right;
    const usableH = dimensions.height - pad.top - pad.bottom;
    const colW = usableW / 3;

    const map = new Map<string, PositionedNode>();
    (Object.keys(groups) as Array<keyof typeof groups>).forEach((tier) => {
      const list = groups[tier];
      const colIdx = TIER_ORDER[tier] ?? 0;
      const x = pad.left + colIdx * colW;
      const gap = usableH / (list.length + 1);
      list.forEach((node, index) => {
        map.set(node.id, {
          node,
          x,
          y: pad.top + gap * (index + 1),
        });
      });
    });

    return map;
  }, [dimensions.height, dimensions.width, nodes]);

  useEffect(() => {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    const svg = d3.select(svgEl);
    svg.selectAll("*").remove();

    if (nodes.length === 0) return;

    const { width, height } = dimensions;
    svg
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", width)
      .attr("height", height);

    const defs = svg.append("defs");

    const addMarker = (id: string, color: string) => {
      defs
        .append("marker")
        .attr("id", id)
        .attr("viewBox", "0 0 10 10")
        .attr("refX", 26)
        .attr("refY", 5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,1 L10,5 L0,9 Z")
        .attr("fill", color);
    };

    addMarker("arrow-default", "#A3A3A3");
    addMarker("arrow-active", "#111111");
    addMarker("arrow-breached", "#991B1B");

    const padLeft = 72;
    const colW = (width - 144) / 3;
    const headerGroup = svg.append("g").attr("class", "tier-headers");
    TIER_LABELS.forEach((label, idx) => {
      const cx = padLeft + idx * colW;
      headerGroup
        .append("text")
        .attr("x", cx)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .attr("fill", "#777777")
        .attr("font-size", "10px")
        .attr("font-weight", "600")
        .attr("font-family", "var(--font-geist-mono)")
        .text(label.toUpperCase());

      if (idx < 3) {
        headerGroup
          .append("line")
          .attr("x1", cx + colW / 2)
          .attr("x2", cx + colW / 2)
          .attr("y1", 32)
          .attr("y2", height - 16)
          .attr("stroke", "#EFEFEF")
          .attr("stroke-dasharray", "3,3");
      }
    });

    const activeHighlightSet = selectedNode
      ? new Set([selectedNode.id, ...downstreamIds])
      : simulationOverlay.active
        ? simulationOverlay.impactedNodes
        : null;

    const edgeLayer = svg.append("g").attr("class", "edges");
    edgeLayer
      .selectAll("path")
      .data(edges)
      .enter()
      .append("path")
      .attr("fill", "none")
      .attr("d", (e) => {
        const s = positions.get(e.source);
        const t = positions.get(e.target);
        if (!s || !t) return "";
        const dx = t.x - s.x;
        return `M${s.x},${s.y} C${s.x + dx * 0.45},${s.y} ${t.x - dx * 0.45},${t.y} ${t.x},${t.y}`;
      })
      .attr("stroke", (e) => {
        if (
          simulationOverlay.active &&
          (simulationOverlay.breachedOrders.has(e.target) ||
            e.source === simulationOverlay.criticalPart ||
            e.target === simulationOverlay.criticalPart)
        ) {
          return "#991B1B";
        }
        if (activeHighlightSet) {
          return activeHighlightSet.has(e.source) && activeHighlightSet.has(e.target)
            ? "#111111"
            : "#E5E5E5";
        }
        return "#CCCCCC";
      })
      .attr("stroke-width", (e) => {
        if (!activeHighlightSet) return 1.3;
        return activeHighlightSet.has(e.source) && activeHighlightSet.has(e.target)
          ? 2
          : 1;
      })
      .attr("opacity", (e) => {
        if (!activeHighlightSet) return 0.9;
        return activeHighlightSet.has(e.source) && activeHighlightSet.has(e.target)
          ? 1
          : 0.35;
      })
      .attr("marker-end", (e) => {
        if (
          simulationOverlay.active &&
          simulationOverlay.breachedOrders.has(e.target)
        ) {
          return "url(#arrow-breached)";
        }
        if (
          activeHighlightSet &&
          activeHighlightSet.has(e.source) &&
          activeHighlightSet.has(e.target)
        ) {
          return "url(#arrow-active)";
        }
        return "url(#arrow-default)";
      });

    const nodeLayer = svg.append("g").attr("class", "nodes");
    const nodeGroups = nodeLayer
      .selectAll("g")
      .data(Array.from(positions.values()))
      .enter()
      .append("g")
      .attr("transform", (d) => `translate(${d.x},${d.y})`)
      .style("cursor", "pointer")
      .attr("opacity", (d) => {
        if (!activeHighlightSet) return 1;
        return activeHighlightSet.has(d.node.id) ? 1 : 0.28;
      });

    nodeGroups
      .append("circle")
      .attr("r", (d) => {
        const tier = getNodeTier(d.node);
        return tier === "supplier" ? 21 : tier === "product" ? 20 : 17;
      })
      .attr("fill", (d) => {
        if (selectedNode?.id === d.node.id) return "#111111";
        if (
          simulationOverlay.active &&
          (simulationOverlay.breachedOrders.has(d.node.id) ||
            d.node.id === simulationOverlay.criticalPart)
        ) {
          return "#FEF2F2";
        }
        const tier = getNodeTier(d.node);
        if (tier === "supplier") return "#181818";
        if (tier === "part") return "#F5F5F5";
        if (tier === "product") return "#222222";
        return "#FFFFFF";
      })
      .attr("stroke", (d) => {
        if (
          simulationOverlay.active &&
          (simulationOverlay.breachedOrders.has(d.node.id) ||
            d.node.id === simulationOverlay.criticalPart)
        ) {
          return "#991B1B";
        }
        return "#111111";
      })
      .attr("stroke-width", (d) => (selectedNode?.id === d.node.id ? 2.8 : 1.5));

    nodeGroups
      .append("text")
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .attr("font-family", "var(--font-geist-mono)")
      .attr("font-size", "9px")
      .attr("font-weight", "600")
      .attr("fill", (d) => {
        if (selectedNode?.id === d.node.id) return "#FFFFFF";
        if (
          simulationOverlay.active &&
          (simulationOverlay.breachedOrders.has(d.node.id) ||
            d.node.id === simulationOverlay.criticalPart)
        ) {
          return "#991B1B";
        }
        const tier = getNodeTier(d.node);
        return tier === "supplier" || tier === "product" ? "#FFFFFF" : "#111111";
      })
      .text((d) =>
        d.node.id.replace("PART-", "P").replace("PROD-", "PR").replace("ORD-", "O")
      );

    nodeGroups
      .append("text")
      .attr("y", (d) => {
        const tier = getNodeTier(d.node);
        return tier === "order" ? 4 : 29;
      })
      .attr("x", (d) => (getNodeTier(d.node) === "order" ? 24 : 0))
      .attr("text-anchor", (d) => (getNodeTier(d.node) === "order" ? "start" : "middle"))
      .attr("font-family", "var(--font-geist-mono)")
      .attr("font-size", "9px")
      .attr("fill", "#525252")
      .text((d) => d.node.id);

    nodeGroups
      .on("mouseenter", (event: MouseEvent, d) => {
        const rect = containerRef.current?.getBoundingClientRect();
        if (!rect) return;
        setTooltip({
          visible: true,
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
          node: d.node,
        });
      })
      .on("mousemove", (event: MouseEvent) => {
        const rect = containerRef.current?.getBoundingClientRect();
        if (!rect) return;
        setTooltip((prev) => ({
          ...prev,
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        }));
      })
      .on("mouseleave", () => {
        setTooltip((prev) => ({ ...prev, visible: false }));
      })
      .on("click", (event: MouseEvent, d) => {
        event.stopPropagation();
        void handleSelectNode(d.node);
      });

    svg.on("click", () => {
      setSelectedNode(null);
      setDownstreamIds([]);
    });

    return () => {
      svg.selectAll("*").remove();
    };
  }, [dimensions, downstreamIds, edges, nodes.length, positions, selectedNode, simulationOverlay]);

  const handleSelectNode = async (node: GraphNode) => {
    setSelectedNode(node);
    setLoadingDownstream(true);
    try {
      const res = await dashboardApi.getDownstream(node.id);
      setDownstreamIds(res.downstream ?? []);
    } catch {
      setDownstreamIds([]);
    } finally {
      setLoadingDownstream(false);
    }
  };

  const handleDeleteSelected = async () => {
    if (!selectedNode) return;
    await dispatch(deleteGraphNodeThunk(selectedNode.id));
    setSelectedNode(null);
    setDownstreamIds([]);
  };

  const handleUndo = async () => {
    await dispatch(undoGraphThunk());
    setSelectedNode(null);
    setDownstreamIds([]);
  };

  const handleReset = async () => {
    await dispatch(resetGraphThunk());
    setSelectedNode(null);
    setDownstreamIds([]);
  };

  return (
    <Card>
      <CardHeader
        title="Supply-Chain Dependency Graph (4-Tier DAG)"
        subtitle="Dynamic NetworkX graph from FastAPI — click any node to trace downstream blast radius or delete"
        action={
          <div className="flex flex-wrap items-center gap-2">
            {simulationOverlay.active ? (
              <Badge tone="breached">
                Impact Overlay: {simulationOverlay.breachedOrders.size} Breached
              </Badge>
            ) : null}
            <Badge tone="neutral">
              {nodes.length} Nodes · {edges.length} Edges
            </Badge>
            <button
              type="button"
              disabled={!canUndo || graphLoading}
              onClick={() => void handleUndo()}
              className="inline-flex items-center gap-1 rounded-sm border border-hairline bg-surface px-2.5 py-1 text-[11px] font-medium text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Undo2 className="h-3 w-3" aria-hidden="true" />
              Undo
            </button>
            <button
              type="button"
              disabled={graphLoading}
              onClick={() => void handleReset()}
              className="inline-flex items-center gap-1 rounded-sm border border-hairline bg-surface px-2.5 py-1 text-[11px] font-medium text-ink hover:bg-canvas disabled:opacity-40"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              Reset
            </button>
          </div>
        }
      />
      <CardBody>
        {nodes.length === 0 ? (
          <EmptyState
            icon={<Network className="h-8 w-8" />}
            title={
              connectionStatus === "connected"
                ? "All Graph Nodes Removed (0 Nodes)"
                : "Supply-Chain Graph Unavailable"
            }
            description={
              connectionStatus === "connected"
                ? "All nodes have been deleted from the active graph. Click Reset above to restore the 19-node network."
                : "Connect to the FastAPI backend to render the 4-tier NetworkX DAG."
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
            <div
              ref={containerRef}
              className={`relative overflow-x-auto rounded-sm border border-hairline bg-surface ${
                selectedNode ? "xl:col-span-8" : "xl:col-span-12"
              }`}
            >
              <svg
                ref={svgRef}
                role="img"
                aria-label="4-tier supply chain dependency graph showing suppliers, BOM parts, finished products, and customer orders"
                className="block h-auto min-w-[540px] w-full select-none"
              />

              {tooltip.visible && tooltip.node ? (
                <div
                  className="pointer-events-none absolute z-20 max-w-[230px] rounded-sm border border-carbon-800 bg-carbon-950 px-3 py-2 text-[11px] text-white shadow-md"
                  style={{
                    left: Math.min(dimensions.width - 240, Math.max(8, tooltip.x + 14)),
                    top: Math.max(8, tooltip.y - 12),
                  }}
                >
                  <p className="font-mono font-semibold">{tooltip.node.id}</p>
                  <p className="mt-0.5 text-[#D4D4D8]">
                    {tooltip.node.name ?? tooltip.node.label}
                  </p>
                  <p className="mt-0.5 font-mono text-[10px] uppercase text-[#A3A3A3]">
                    Tier: {getNodeTier(tooltip.node)}
                  </p>
                </div>
              ) : null}
            </div>

            {selectedNode ? (
              <div className="flex flex-col justify-between rounded-sm border border-hairline bg-canvas p-4 xl:col-span-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <Badge tone="dark">{getNodeTier(selectedNode)}</Badge>
                      <h3 className="mt-1.5 font-mono text-sm font-bold text-ink">
                        {selectedNode.id}
                      </h3>
                      <p className="text-xs text-ink-muted">
                        {selectedNode.name ?? selectedNode.label}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedNode(null);
                        setDownstreamIds([]);
                      }}
                      aria-label="Close node inspector"
                      className="rounded-sm p-1 text-ink-muted hover:bg-surface hover:text-ink"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="rounded-sm border border-hairline bg-surface p-3 text-xs">
                    <span className="text-[11px] font-medium text-ink-muted">
                      Downstream Reachable Nodes ({loadingDownstream ? "…" : downstreamIds.length})
                    </span>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {loadingDownstream ? (
                        <span className="text-[11px] text-ink-muted">
                          Computing BFS cascade…
                        </span>
                      ) : downstreamIds.length === 0 ? (
                        <span className="text-[11px] text-ink-muted">
                          Leaf node (0 downstream dependencies)
                        </span>
                      ) : (
                        downstreamIds.map((id) => (
                          <Badge
                            key={id}
                            tone={
                              simulationOverlay.breachedOrders.has(id) ||
                              id === simulationOverlay.criticalPart
                                ? "breached"
                                : "neutral"
                            }
                          >
                            {id}
                          </Badge>
                        ))
                      )}
                    </div>
                  </div>

                  <dl className="space-y-1.5 rounded-sm border border-hairline bg-surface p-3 text-xs">
                    {typeof selectedNode.recovery_lead_time_hours === "number" ? (
                      <div className="flex justify-between">
                        <dt className="text-ink-muted">Recovery Lead Time</dt>
                        <dd className="font-mono font-medium">
                          {selectedNode.recovery_lead_time_hours}h
                        </dd>
                      </div>
                    ) : null}
                    {typeof selectedNode.initial_stock_units === "number" ? (
                      <div className="flex justify-between">
                        <dt className="text-ink-muted">Initial Stock</dt>
                        <dd className="font-mono font-medium">
                          {selectedNode.initial_stock_units} units
                        </dd>
                      </div>
                    ) : null}
                    {typeof selectedNode.hourly_consumption_units === "number" ? (
                      <div className="flex justify-between">
                        <dt className="text-ink-muted">Hourly Burn</dt>
                        <dd className="font-mono font-medium">
                          {selectedNode.hourly_consumption_units}/hr
                        </dd>
                      </div>
                    ) : null}
                    {typeof selectedNode.delivery_deadline_hours === "number" ? (
                      <div className="flex justify-between">
                        <dt className="text-ink-muted">Delivery Deadline</dt>
                        <dd className="font-mono font-medium">
                          Hour {selectedNode.delivery_deadline_hours}
                        </dd>
                      </div>
                    ) : null}
                    {selectedNode.location ? (
                      <div className="flex justify-between">
                        <dt className="text-ink-muted">Location</dt>
                        <dd className="font-medium">{selectedNode.location}</dd>
                      </div>
                    ) : null}
                  </dl>
                </div>

                <div className="mt-4 border-t border-hairline pt-3">
                  <button
                    type="button"
                    disabled={graphLoading}
                    onClick={() => void handleDeleteSelected()}
                    className="inline-flex w-full items-center justify-center gap-1.5 rounded-sm border border-status-breached-border bg-status-breached-bg px-3 py-2 text-xs font-semibold text-status-breached hover:opacity-90 disabled:opacity-50"
                  >
                    <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                    Cascade Delete {selectedNode.id}
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        )}

        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[11px] text-ink-muted">
          <div className="flex flex-wrap items-center gap-4">
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-carbon-900" />
              Supplier / Product
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full border border-carbon-950 bg-canvas" />
              BOM Part
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full border border-carbon-950 bg-surface" />
              Customer Order
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full border border-status-breached bg-status-breached-bg" />
              Critical Part / Breached Order
            </span>
          </div>
          <span>Click any node to inspect downstream dependencies or cascade delete</span>
        </div>
      </CardBody>
    </Card>
  );
}
