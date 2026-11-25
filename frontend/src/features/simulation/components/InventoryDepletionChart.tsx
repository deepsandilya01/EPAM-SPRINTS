"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { LineChart } from "lucide-react";

import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { EmptyState } from "@/features/shared/components/EmptyState";
import type { HourlyStockPoint } from "@/features/shared/types/simulation";

interface InventoryDepletionChartProps {
  timeline: HourlyStockPoint[];
  selectedHour: number;
  stockoutHour: number | null;
  partId?: string;
  delayHours?: number;
  onSelectHour?: (hour: number) => void;
}

interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  point: HourlyStockPoint | null;
}

export function InventoryDepletionChart({
  timeline,
  selectedHour,
  stockoutHour,
  partId,
  delayHours,
  onSelectHour,
}: InventoryDepletionChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [dimensions, setDimensions] = useState({ width: 760, height: 320 });
  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false,
    x: 0,
    y: 0,
    point: null,
  });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const updateSize = () => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0) {
        setDimensions({
          width: Math.max(320, Math.floor(rect.width)),
          height: rect.width < 520 ? 260 : 320,
        });
      }
    };

    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(el);

    return () => observer.disconnect();
  }, [timeline.length]);

  useEffect(() => {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    const svg = d3.select(svgEl);
    svg.selectAll("*").remove();

    if (timeline.length === 0) {
      return;
    }

    const margin = { top: 24, right: 24, bottom: 42, left: 56 };
    const innerWidth = Math.max(120, dimensions.width - margin.left - margin.right);
    const innerHeight = Math.max(120, dimensions.height - margin.top - margin.bottom);

    const maxStock = d3.max(timeline, (d) => d.stock_units) ?? 10;
    const yMax = maxStock > 0 ? maxStock * 1.15 : 10;

    const xScale = d3.scaleLinear().domain([0, 72]).range([0, innerWidth]);
    const yScale = d3.scaleLinear().domain([0, yMax]).nice().range([innerHeight, 0]);

    const root = svg
      .attr("viewBox", `0 0 ${dimensions.width} ${dimensions.height}`)
      .attr("width", dimensions.width)
      .attr("height", dimensions.height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    root
      .append("g")
      .attr("class", "grid-y")
      .call(
        d3
          .axisLeft(yScale)
          .ticks(5)
          .tickSize(-innerWidth)
          .tickFormat(() => "")
      )
      .call((g) => g.select(".domain").remove())
      .call((g) =>
        g
          .selectAll("line")
          .attr("stroke", "#E5E5E5")
          .attr("stroke-dasharray", "2,2")
      );

    if (typeof delayHours === "number" && delayHours > 0) {
      const clampedDelay = Math.min(72, delayHours);
      root
        .append("rect")
        .attr("x", xScale(0))
        .attr("y", 0)
        .attr("width", Math.max(0, xScale(clampedDelay) - xScale(0)))
        .attr("height", innerHeight)
        .attr("fill", "#111111")
        .attr("opacity", 0.04);

      root
        .append("text")
        .attr("x", Math.min(innerWidth - 4, xScale(clampedDelay / 2)))
        .attr("y", 12)
        .attr("text-anchor", "middle")
        .attr("fill", "#777777")
        .attr("font-size", "10px")
        .attr("font-family", "var(--font-geist-mono)")
        .text(`SUPPLY BLOCKED (0–${clampedDelay.toFixed(0)}h)`);
    }

    const areaGenerator = d3
      .area<HourlyStockPoint>()
      .x((d) => xScale(d.hour))
      .y0(innerHeight)
      .y1((d) => yScale(d.stock_units))
      .curve(d3.curveMonotoneX);

    root
      .append("path")
      .datum(timeline)
      .attr("fill", "#111111")
      .attr("fill-opacity", 0.08)
      .attr("d", areaGenerator);

    const lineGenerator = d3
      .line<HourlyStockPoint>()
      .x((d) => xScale(d.hour))
      .y((d) => yScale(d.stock_units))
      .curve(d3.curveMonotoneX);

    root
      .append("path")
      .datum(timeline)
      .attr("fill", "none")
      .attr("stroke", "#111111")
      .attr("stroke-width", 2)
      .attr("d", lineGenerator);

    root
      .append("line")
      .attr("x1", 0)
      .attr("x2", innerWidth)
      .attr("y1", yScale(0))
      .attr("y2", yScale(0))
      .attr("stroke", "#D4D4D8")
      .attr("stroke-width", 1);

    root
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(
        d3
          .axisBottom(xScale)
          .tickValues([0, 8, 16, 24, 32, 40, 48, 56, 64, 72])
          .tickFormat((d) => `${d}h`)
      )
      .call((g) => g.select(".domain").attr("stroke", "#D4D4D8"))
      .call((g) => g.selectAll("line").attr("stroke", "#D4D4D8"))
      .call((g) =>
        g
          .selectAll("text")
          .attr("fill", "#777777")
          .attr("font-size", "10px")
          .attr("font-family", "var(--font-geist-mono)")
      );

    root
      .append("g")
      .call(d3.axisLeft(yScale).ticks(5))
      .call((g) => g.select(".domain").attr("stroke", "#D4D4D8"))
      .call((g) => g.selectAll("line").attr("stroke", "#D4D4D8"))
      .call((g) =>
        g
          .selectAll("text")
          .attr("fill", "#777777")
          .attr("font-size", "10px")
          .attr("font-family", "var(--font-geist-mono)")
      );

    root
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", innerHeight + 34)
      .attr("text-anchor", "middle")
      .attr("fill", "#777777")
      .attr("font-size", "10px")
      .text("Simulation Horizon (Hours 0–72)");

    root
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -42)
      .attr("text-anchor", "middle")
      .attr("fill", "#777777")
      .attr("font-size", "10px")
      .text("Remaining Inventory (Units)");

    if (stockoutHour !== null && stockoutHour >= 0 && stockoutHour <= 72) {
      const sx = xScale(stockoutHour);
      root
        .append("line")
        .attr("x1", sx)
        .attr("x2", sx)
        .attr("y1", 0)
        .attr("y2", innerHeight)
        .attr("stroke", "#991B1B")
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", "4,3");

      root
        .append("circle")
        .attr("cx", sx)
        .attr("cy", yScale(0))
        .attr("r", 4.5)
        .attr("fill", "#991B1B")
        .attr("stroke", "#FFFFFF")
        .attr("stroke-width", 1.5);

      const labelAnchor = sx > innerWidth * 0.72 ? "end" : "start";
      const labelDx = sx > innerWidth * 0.72 ? -6 : 6;
      root
        .append("text")
        .attr("x", sx + labelDx)
        .attr("y", 26)
        .attr("text-anchor", labelAnchor)
        .attr("fill", "#991B1B")
        .attr("font-size", "10px")
        .attr("font-weight", "600")
        .attr("font-family", "var(--font-geist-mono)")
        .text(`T_stockout = ${stockoutHour.toFixed(1)}h`);
    }

    const selectedPoint =
      timeline.find((p) => p.hour === selectedHour) ??
      timeline[Math.min(selectedHour, timeline.length - 1)];

    if (selectedPoint) {
      const cx = xScale(selectedPoint.hour);
      const cy = yScale(selectedPoint.stock_units);

      root
        .append("line")
        .attr("x1", cx)
        .attr("x2", cx)
        .attr("y1", 0)
        .attr("y2", innerHeight)
        .attr("stroke", "#111111")
        .attr("stroke-width", 1.25);

      root
        .append("circle")
        .attr("cx", cx)
        .attr("cy", cy)
        .attr("r", 5)
        .attr("fill", "#111111")
        .attr("stroke", "#FFFFFF")
        .attr("stroke-width", 2);
    }

    root
      .append("rect")
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .attr("fill", "transparent")
      .style("cursor", "crosshair")
      .on("pointermove", (event: PointerEvent) => {
        const [mx] = d3.pointer(event);
        const hoveredHour = Math.max(0, Math.min(72, Math.round(xScale.invert(mx))));
        const point =
          timeline.find((p) => p.hour === hoveredHour) ??
          timeline[Math.min(hoveredHour, timeline.length - 1)] ??
          null;

        if (!point) return;

        const px = margin.left + xScale(point.hour);
        const py = margin.top + yScale(point.stock_units);

        setTooltip({
          visible: true,
          x: px,
          y: py,
          point,
        });
      })
      .on("pointerleave", () => {
        setTooltip((prev) => ({ ...prev, visible: false }));
      })
      .on("click", (event: MouseEvent) => {
        if (!onSelectHour) return;
        const [mx] = d3.pointer(event);
        const clickedHour = Math.max(0, Math.min(72, Math.round(xScale.invert(mx))));
        onSelectHour(clickedHour);
      });

    return () => {
      svg.selectAll("*").remove();
    };
  }, [delayHours, dimensions.height, dimensions.width, onSelectHour, selectedHour, stockoutHour, timeline]);

  return (
    <Card>
      <CardHeader
        title="Inventory Depletion Curve (0–72h)"
        subtitle={
          partId
            ? `Critical BOM Part: ${partId} — Discrete hourly consumption trajectory`
            : "Discrete hourly inventory trajectory returned by FastAPI"
        }
        action={
          <div className="flex flex-wrap items-center gap-2">
            {stockoutHour !== null ? (
              <Badge tone="breached">Stockout: Hour {stockoutHour.toFixed(1)}</Badge>
            ) : timeline.length > 0 ? (
              <Badge tone="feasible">No Stockout (0–72h)</Badge>
            ) : null}
            <Badge tone="dark">Selected: Hour {selectedHour}</Badge>
          </div>
        }
      />
      <CardBody>
        {timeline.length === 0 ? (
          <EmptyState
            icon={<LineChart className="h-8 w-8" />}
            title="No Simulation Timeline Loaded"
            description="Run a disruption simulation to visualize the 72-hour inventory depletion trajectory and stockout threshold."
          />
        ) : (
          <div ref={containerRef} className="relative w-full overflow-hidden">
            <svg
              ref={svgRef}
              role="img"
              aria-label={`Inventory depletion line chart for ${partId ?? "critical part"} across 72 hours`}
              className="block h-auto w-full select-none"
            />

            {tooltip.visible && tooltip.point ? (
              <div
                className="pointer-events-none absolute z-20 rounded-sm border border-carbon-800 bg-carbon-950 px-3 py-2 text-[11px] text-white shadow-md"
                style={{
                  left: Math.min(dimensions.width - 170, Math.max(8, tooltip.x + 12)),
                  top: Math.max(8, tooltip.y - 54),
                }}
              >
                <div className="font-mono font-semibold">Hour {tooltip.point.hour}</div>
                <div className="mt-0.5 text-[#D4D4D8]">
                  Remaining Stock:{" "}
                  <span className="font-mono font-medium text-white">
                    {tooltip.point.stock_units.toFixed(2)} units
                  </span>
                </div>
                <div className="mt-0.5 text-[#A3A3A3]">
                  Supply:{" "}
                  <span className="font-mono">
                    {tooltip.point.supply_blocked ? "BLOCKED" : "RESUMED"}
                  </span>
                </div>
              </div>
            ) : null}

            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-hairline pt-2.5 text-[11px] text-ink-muted">
              <div className="flex flex-wrap items-center gap-4">
                <span className="inline-flex items-center gap-1.5">
                  <span className="h-0.5 w-4 bg-carbon-950" />
                  Inventory Trajectory
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-carbon-950" />
                  Selected Hour Marker
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <span className="h-0.5 w-4 border-t-2 border-dashed border-status-breached" />
                  Stockout Inflection
                </span>
              </div>
              <span>Click or hover chart to inspect hourly stock levels</span>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}

