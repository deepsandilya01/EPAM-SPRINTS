"use client";

import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Boxes,
  Clock,
  Cpu,
  Factory,
  Gauge,
  Package,
  Play,
  ShoppingCart,
} from "lucide-react";

import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { EmptyState } from "@/features/shared/components/EmptyState";
import { formatDeltaT, formatNumber } from "@/features/shared/utils/format";
import { InterventionGauge } from "@/features/simulation/components/InterventionGauge";
import {
  selectDeltaT,
  selectExecutionState,
  selectExecutionTime,
  selectInterventionStatus,
  selectLatestResponse,
  selectSessionRuns,
  selectStockoutHour,
} from "@/features/simulation/slices/simulationSelectors";
import { runBenchmarkSimulationThunk } from "@/features/simulation/slices/simulationSlice";
import { useAppDispatch, useAppSelector } from "@/store";

export function DashboardPage() {
  const dispatch = useAppDispatch();
  const { nodes, edges, connectionStatus, health, graphError } = useAppSelector(
    (state) => state.dashboard
  );
  const latestResponse = useAppSelector(selectLatestResponse);
  const executionState = useAppSelector(selectExecutionState);
  const stockoutHour = useAppSelector(selectStockoutHour);
  const interventionStatus = useAppSelector(selectInterventionStatus);
  const deltaT = useAppSelector(selectDeltaT);
  const executionTimeMs = useAppSelector(selectExecutionTime);
  const sessionRuns = useAppSelector(selectSessionRuns);

  const supplierCount = nodes.filter(
    (n) => n.kind === "supplier" || n.tier === "supplier"
  ).length;

  const isRunning = executionState === "running" || executionState === "validating";

  const statusTone =
    interventionStatus === "FEASIBLE"
      ? "feasible"
      : interventionStatus === "CRITICAL"
        ? "critical"
        : interventionStatus === "BREACHED"
          ? "breached"
          : "neutral";

  const metrics = [
    {
      label: "Total Suppliers",
      value: nodes.length > 0 ? String(supplierCount) : "—",
      sub:
        nodes.length > 0
          ? `${nodes.length} nodes · ${edges.length} edges loaded`
          : "Awaiting backend graph",
      icon: Factory,
    },
    {
      label: "Affected Parts",
      value: latestResponse
        ? String(latestResponse.impact.affected_parts.length)
        : "—",
      sub: latestResponse
        ? latestResponse.impact.affected_parts.join(", ") || "None"
        : "Run simulation to compute",
      icon: Boxes,
    },
    {
      label: "Affected Products",
      value: latestResponse
        ? String(latestResponse.impact.affected_products.length)
        : "—",
      sub: latestResponse
        ? latestResponse.impact.affected_products.join(", ") || "None"
        : "Run simulation to compute",
      icon: Package,
    },
    {
      label: "Affected Orders",
      value: latestResponse
        ? String(latestResponse.impact.affected_orders.length)
        : "—",
      sub: latestResponse
        ? `${latestResponse.stockout.total_breached} breached / ${latestResponse.impact.affected_orders.length} downstream`
        : "Run simulation to compute",
      icon: ShoppingCart,
    },
    {
      label: "Stockout Prediction",
      value: latestResponse
        ? stockoutHour !== null
          ? `Hour ${formatNumber(stockoutHour)}`
          : "No Stockout"
        : "—",
      sub: latestResponse?.critical_part
        ? `Critical part: ${latestResponse.critical_part.part_id}`
        : "72-hour horizon",
      icon: Clock,
    },
    {
      label: "Intervention Status",
      value: interventionStatus ?? "—",
      sub:
        deltaT !== null
          ? `ΔT = ${formatDeltaT(deltaT)}`
          : "ΔT = T_stockout − T_curr − t_rec",
      icon: Gauge,
    },
    {
      label: "Execution Time",
      value: executionTimeMs !== null ? `${executionTimeMs.toFixed(3)} ms` : "—",
      sub:
        executionTimeMs !== null
          ? executionTimeMs < 25
            ? "Within <25ms Sprint 2 SLA"
            : "Exceeds 25ms SLA"
          : "Pipeline SLA target < 25ms",
      icon: Cpu,
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardBody className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="dark">RE:Flow Sprint 2</Badge>
              <Badge
                tone={
                  connectionStatus === "connected"
                    ? "feasible"
                    : connectionStatus === "disconnected"
                      ? "breached"
                      : "neutral"
                }
              >
                {connectionStatus === "connected"
                  ? `FastAPI v${health?.version ?? "2.0.0"} Online`
                  : connectionStatus === "disconnected"
                    ? "FastAPI Offline"
                    : "Connecting..."}
              </Badge>
            </div>
            <h2 className="text-base font-semibold tracking-tight text-ink">
              Temporal Disruption Simulation &amp; Intervention Window Console
            </h2>
            <p className="text-xs text-ink-muted">
              Real-time supply-chain blast radius, 72-hour warehouse depletion modeling, and
              actionable intervention window analytics.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              disabled={isRunning || connectionStatus === "disconnected"}
              onClick={() => void dispatch(runBenchmarkSimulationThunk())}
              className="inline-flex items-center gap-2 rounded-sm border border-carbon-950 bg-carbon-950 px-3.5 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-carbon-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Play className="h-3.5 w-3.5" aria-hidden="true" />
              Run Benchmark (SUP-01 · 8h)
            </button>

            <Link
              href="/simulation"
              className="inline-flex items-center gap-1.5 rounded-sm border border-hairline bg-surface px-3.5 py-2 text-xs font-medium text-ink hover:bg-canvas"
            >
              Open Simulation Lab
              <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            </Link>
          </div>
        </CardBody>
      </Card>

      {graphError ? (
        <div
          role="alert"
          className="rounded-sm border border-status-breached-border bg-status-breached-bg px-4 py-3 text-xs text-status-breached"
        >
          <span className="font-semibold">Backend Connection Error:</span> {graphError}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.label} className="flex flex-col justify-between">
              <CardBody className="p-4">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[11px] font-medium text-ink-muted">
                    {metric.label}
                  </span>
                  <Icon className="h-3.5 w-3.5 text-ink-muted" aria-hidden="true" />
                </div>
                <div className="mt-2 font-mono text-lg font-bold tracking-tight text-ink">
                  {metric.label === "Intervention Status" && interventionStatus ? (
                    <Badge tone={statusTone}>{metric.value}</Badge>
                  ) : (
                    metric.value
                  )}
                </div>
                <p className="mt-1.5 truncate text-[11px] text-ink-muted" title={metric.sub}>
                  {metric.sub}
                </p>
              </CardBody>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="lg:col-span-6">
          <Card className="h-full">
            <CardHeader
              title="Simulation Overview"
              subtitle="Latest supplier disruption event & downstream ripple cascade"
              action={
                latestResponse ? (
                  <Badge tone="dark">{latestResponse.event.supplier_id}</Badge>
                ) : null
              }
            />
            <CardBody>
              {!latestResponse ? (
                <EmptyState
                  icon={<Activity className="h-8 w-8" />}
                  title="No Simulation Executed Yet"
                  description="Trigger the canonical 8-hour benchmark above or open Disruption Simulation to inspect ripple impact, depletion curve, and order breaches."
                  action={
                    <Link
                      href="/simulation"
                      className="inline-flex items-center gap-1.5 rounded-sm border border-carbon-950 bg-carbon-950 px-3.5 py-2 text-xs font-medium text-white hover:bg-carbon-800"
                    >
                      Go to Simulation
                      <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                    </Link>
                  }
                />
              ) : (
                <dl className="grid grid-cols-1 gap-3 text-xs sm:grid-cols-2">
                  <div className="rounded-sm border border-hairline bg-canvas p-3">
                    <dt className="text-[11px] text-ink-muted">Supplier &amp; Event</dt>
                    <dd className="mt-1 font-mono font-semibold text-ink">
                      {latestResponse.event.supplier_id} ·{" "}
                      {latestResponse.event.disruption_type}
                    </dd>
                    <dd className="mt-0.5 text-[11px] text-ink-muted">
                      Delay: {latestResponse.event.delay_duration_hours}h
                    </dd>
                  </div>

                  <div className="rounded-sm border border-hairline bg-canvas p-3">
                    <dt className="text-[11px] text-ink-muted">Ripple Impact</dt>
                    <dd className="mt-1 font-mono font-semibold text-ink">
                      {latestResponse.impact.total_affected_nodes} downstream nodes
                    </dd>
                    <dd className="mt-0.5 text-[11px] text-ink-muted">
                      {latestResponse.impact.affected_parts.length} parts ·{" "}
                      {latestResponse.impact.affected_products.length} products ·{" "}
                      {latestResponse.impact.affected_orders.length} orders
                    </dd>
                  </div>

                  <div className="rounded-sm border border-hairline bg-canvas p-3">
                    <dt className="text-[11px] text-ink-muted">Critical Inventory Part</dt>
                    <dd className="mt-1 font-mono font-semibold text-ink">
                      {latestResponse.critical_part?.part_id ??
                        latestResponse.stockout.part_id}
                    </dd>
                    <dd className="mt-0.5 text-[11px] text-ink-muted">
                      {latestResponse.critical_part
                        ? `${latestResponse.critical_part.initial_stock} initial · ${latestResponse.critical_part.hourly_consumption}/hr burn`
                        : "Inventory timeline loaded"}
                    </dd>
                  </div>

                  <div className="rounded-sm border border-hairline bg-canvas p-3">
                    <dt className="text-[11px] text-ink-muted">Breached Orders</dt>
                    <dd className="mt-1 font-mono font-semibold text-ink">
                      {latestResponse.stockout.total_breached} failing orders
                    </dd>
                    <dd className="mt-0.5 font-mono text-[11px] text-status-breached">
                      {latestResponse.stockout.breached_orders
                        .map((o) => o.order_id)
                        .join(", ") || "None"}
                    </dd>
                  </div>
                </dl>
              )}
            </CardBody>
          </Card>
        </div>

        <div className="lg:col-span-6">
          <InterventionGauge intervention={latestResponse?.intervention ?? null} />
        </div>
      </div>

      <Card>
        <CardHeader
          title="Session Simulation Activity"
          subtitle="Live execution log recorded during this browser session (sourced strictly from FastAPI responses)"
        />
        <CardBody>
          {sessionRuns.length === 0 ? (
            <EmptyState
              title="No Session Runs Recorded"
              description="The FastAPI backend is stateless for simulation history. Executed runs in this session will appear here automatically."
            />
          ) : (
            <div className="overflow-x-auto rounded-sm border border-hairline">
              <table className="w-full border-collapse text-left text-xs">
                <thead>
                  <tr className="border-b border-hairline bg-canvas text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
                    <th className="px-3.5 py-2.5">Supplier</th>
                    <th className="px-3.5 py-2.5">Type</th>
                    <th className="px-3.5 py-2.5">Delay</th>
                    <th className="px-3.5 py-2.5">T_stockout</th>
                    <th className="px-3.5 py-2.5">ΔT</th>
                    <th className="px-3.5 py-2.5">Status</th>
                    <th className="px-3.5 py-2.5">Breached</th>
                    <th className="px-3.5 py-2.5">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hairline bg-surface">
                  {sessionRuns.map((run) => (
                    <tr key={run.event.event_id} className="hover:bg-canvas/60">
                      <td className="px-3.5 py-2.5 font-mono font-semibold">
                        {run.event.supplier_id}
                      </td>
                      <td className="px-3.5 py-2.5 font-mono text-ink-muted">
                        {run.event.disruption_type}
                      </td>
                      <td className="px-3.5 py-2.5 font-mono">
                        {run.event.delay_duration_hours}h
                      </td>
                      <td className="px-3.5 py-2.5 font-mono">
                        {run.stockout.stockout_hour !== null
                          ? `${run.stockout.stockout_hour}h`
                          : "None"}
                      </td>
                      <td className="px-3.5 py-2.5 font-mono">
                        {formatDeltaT(run.intervention.delta_t_hours)}
                      </td>
                      <td className="px-3.5 py-2.5">
                        <Badge
                          tone={
                            run.intervention.status === "FEASIBLE"
                              ? "feasible"
                              : run.intervention.status === "CRITICAL"
                                ? "critical"
                                : "breached"
                          }
                        >
                          {run.intervention.status}
                        </Badge>
                      </td>
                      <td className="px-3.5 py-2.5 font-mono">
                        {run.stockout.total_breached}
                      </td>
                      <td className="px-3.5 py-2.5 font-mono text-ink-muted">
                        {run.execution_time_ms.toFixed(3)} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}

