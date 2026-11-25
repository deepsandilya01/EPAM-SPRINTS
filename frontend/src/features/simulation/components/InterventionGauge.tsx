"use client";

import { AlertTriangle, CheckCircle2, Gauge, XCircle } from "lucide-react";

import { Badge, type BadgeTone } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { EmptyState } from "@/features/shared/components/EmptyState";
import type { InterventionWindowResult } from "@/features/shared/types/simulation";
import { formatDeltaT, formatNumber } from "@/features/shared/utils/format";

interface InterventionGaugeProps {
  intervention: InterventionWindowResult | null;
}

function getStatusConfig(status: string): {
  tone: BadgeTone;
  panelClass: string;
  barClass: string;
  Icon: typeof CheckCircle2;
} {
  const normalized = status.toUpperCase();
  if (normalized === "FEASIBLE") {
    return {
      tone: "feasible",
      panelClass: "border-status-feasible-border bg-status-feasible-bg text-status-feasible",
      barClass: "bg-status-feasible",
      Icon: CheckCircle2,
    };
  }
  if (normalized === "CRITICAL") {
    return {
      tone: "critical",
      panelClass: "border-status-critical-border bg-status-critical-bg text-status-critical",
      barClass: "bg-carbon-800",
      Icon: AlertTriangle,
    };
  }
  return {
    tone: "breached",
    panelClass: "border-status-breached-border bg-status-breached-bg text-status-breached",
    barClass: "bg-status-breached",
    Icon: XCircle,
  };
}

export function InterventionGauge({ intervention }: InterventionGaugeProps) {
  if (!intervention) {
    return (
      <Card>
        <CardHeader
          title="Intervention Window (ΔT)"
          subtitle="Formula: ΔT = T_stockout − T_current − t_recovery"
        />
        <CardBody>
          <EmptyState
            icon={<Gauge className="h-8 w-8" />}
            title="No Intervention Window Calculated"
            description="Execute a simulation to compute ΔT feasibility, recovery lead time, and impacted order IDs from the backend."
          />
        </CardBody>
      </Card>
    );
  }

  const config = getStatusConfig(intervention.status);
  const StatusIcon = config.Icon;

  const stockoutVal = intervention.stockout_hour ?? 0;
  const recoveryVal = intervention.recovery_lead_time_hours;
  const maxAxis = Math.max(stockoutVal, recoveryVal, 1);
  const recoveryPct = Math.min(100, Math.max(0, (recoveryVal / maxAxis) * 100));
  const deltaPct =
    intervention.delta_t_hours !== null && intervention.delta_t_hours > 0
      ? Math.min(100 - recoveryPct, (intervention.delta_t_hours / maxAxis) * 100)
      : 0;

  return (
    <Card>
      <CardHeader
        title="Intervention Window (ΔT)"
        subtitle="Authoritative decision status calculated by FastAPI"
        action={<Badge tone={config.tone}>{intervention.status}</Badge>}
      />
      <CardBody className="space-y-4">
        <div className={`rounded-sm border p-4 ${config.panelClass}`}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <StatusIcon className="h-5 w-5 shrink-0" aria-hidden="true" />
              <div>
                <p className="font-mono text-xs font-semibold uppercase tracking-wider">
                  {intervention.status} ·{" "}
                  {intervention.is_feasible ? "Action Window Open" : "Window Breached"}
                </p>
                <p className="mt-0.5 text-xs opacity-90">{intervention.message}</p>
              </div>
            </div>
            <div className="text-right">
              <span className="block font-mono text-[10px] uppercase tracking-wider opacity-80">
                Delta T (ΔT)
              </span>
              <span className="font-mono text-2xl font-bold tracking-tight">
                {formatDeltaT(intervention.delta_t_hours)}
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-sm border border-hairline bg-canvas p-3.5">
          <div className="mb-2 flex items-center justify-between font-mono text-[11px] text-ink-muted">
            <span>T_current: {formatNumber(intervention.current_hour)}h</span>
            <span>T_stockout: {formatNumber(intervention.stockout_hour)}h</span>
          </div>

          <div
            className="flex h-3 w-full overflow-hidden rounded-sm border border-hairline bg-surface"
            aria-label="Intervention window proportion gauge"
          >
            <div
              className="h-full bg-carbon-950"
              style={{ width: `${recoveryPct}%` }}
              title={`Recovery lead time: ${recoveryVal}h`}
            />
            {deltaPct > 0 ? (
              <div
                className={`h-full ${config.barClass}`}
                style={{ width: `${deltaPct}%` }}
                title={`Intervention window ΔT: ${formatDeltaT(intervention.delta_t_hours)}`}
              />
            ) : null}
          </div>

          <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[11px] text-ink-muted">
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-xs bg-carbon-950" />
              Recovery Lead Time ({formatNumber(recoveryVal)}h)
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-xs ${config.barClass}`} />
              Remaining Window ({formatDeltaT(intervention.delta_t_hours)})
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-sm border border-hairline bg-surface p-3">
            <span className="text-[11px] text-ink-muted">T_stockout</span>
            <p className="mt-1 font-mono text-sm font-semibold text-ink">
              {formatNumber(intervention.stockout_hour)}h
            </p>
          </div>
          <div className="rounded-sm border border-hairline bg-surface p-3">
            <span className="text-[11px] text-ink-muted">T_current</span>
            <p className="mt-1 font-mono text-sm font-semibold text-ink">
              {formatNumber(intervention.current_hour)}h
            </p>
          </div>
          <div className="rounded-sm border border-hairline bg-surface p-3">
            <span className="text-[11px] text-ink-muted">t_recovery</span>
            <p className="mt-1 font-mono text-sm font-semibold text-ink">
              {formatNumber(intervention.recovery_lead_time_hours)}h
            </p>
          </div>
          <div className="rounded-sm border border-hairline bg-surface p-3">
            <span className="text-[11px] text-ink-muted">Breached Orders</span>
            <p className="mt-1 font-mono text-sm font-semibold text-ink">
              {intervention.affected_order_ids.length > 0
                ? intervention.affected_order_ids.join(", ")
                : "None"}
            </p>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}

