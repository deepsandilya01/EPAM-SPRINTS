"use client";

import { useCallback } from "react";
import { GitBranch, Layers } from "lucide-react";

import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody } from "@/features/shared/components/Card";
import { AffectedOrdersTable } from "@/features/simulation/components/AffectedOrdersTable";
import { DisruptionForm } from "@/features/simulation/components/DisruptionForm";
import { InterventionGauge } from "@/features/simulation/components/InterventionGauge";
import { InventoryDepletionChart } from "@/features/simulation/components/InventoryDepletionChart";
import { TimelineScrubber } from "@/features/simulation/components/TimelineScrubber";
import {
  selectDepletionTimeline,
  selectLatestResponse,
  selectSelectedTimelineHour,
  selectStockoutHour,
} from "@/features/simulation/slices/simulationSelectors";
import { setSelectedTimelineHour } from "@/features/simulation/slices/simulationSlice";
import { useAppDispatch, useAppSelector } from "@/store";

export function SimulationPage() {
  const dispatch = useAppDispatch();
  const latestResponse = useAppSelector(selectLatestResponse);
  const timeline = useAppSelector(selectDepletionTimeline);
  const selectedHour = useAppSelector(selectSelectedTimelineHour);
  const stockoutHour = useAppSelector(selectStockoutHour);
  const graphNodes = useAppSelector((state) => state.dashboard.nodes);

  const handleSelectHour = useCallback(
    (hour: number) => {
      dispatch(setSelectedTimelineHour(hour));
    },
    [dispatch]
  );

  return (
    <div className="space-y-6">
      <DisruptionForm />

      {latestResponse ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-ink-muted">
                  Downstream Ripple Impact
                </span>
                <GitBranch className="h-3.5 w-3.5 text-ink-muted" aria-hidden="true" />
              </div>
              <p className="mt-1.5 font-mono text-base font-semibold text-ink">
                {latestResponse.impact.disrupted_supplier} →{" "}
                {latestResponse.impact.total_affected_nodes} Nodes
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {latestResponse.impact.affected_parts.map((part) => (
                  <Badge key={part} tone="neutral">
                    {part}
                  </Badge>
                ))}
                {latestResponse.impact.affected_products.map((prod) => (
                  <Badge key={prod} tone="dark">
                    {prod}
                  </Badge>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-ink-muted">
                  Critical BOM Component
                </span>
                <Layers className="h-3.5 w-3.5 text-ink-muted" aria-hidden="true" />
              </div>
              <p className="mt-1.5 font-mono text-base font-semibold text-ink">
                {latestResponse.critical_part?.part_id ??
                  latestResponse.stockout.part_id}
              </p>
              <p className="mt-1 text-xs text-ink-muted">
                {latestResponse.critical_part
                  ? `Initial: ${latestResponse.critical_part.initial_stock} units · Burn: ${latestResponse.critical_part.hourly_consumption} units/hr`
                  : "Critical stockout component"}
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-ink-muted">
                  Pipeline Performance SLA
                </span>
                <Badge tone={latestResponse.execution_time_ms < 25 ? "feasible" : "breached"}>
                  {latestResponse.execution_time_ms < 25 ? "SLA Met" : "SLA Exceeded"}
                </Badge>
              </div>
              <p className="mt-1.5 font-mono text-base font-semibold text-ink">
                {latestResponse.execution_time_ms.toFixed(4)} ms
              </p>
              <p className="mt-1 text-xs text-ink-muted">
                Event ID:{" "}
                <span className="font-mono">
                  {latestResponse.event.event_id.slice(0, 12)}…
                </span>
              </p>
            </CardBody>
          </Card>
        </div>
      ) : null}

      <InventoryDepletionChart
        timeline={timeline}
        selectedHour={selectedHour}
        stockoutHour={stockoutHour}
        partId={
          latestResponse?.critical_part?.part_id ?? latestResponse?.stockout.part_id
        }
        delayHours={latestResponse?.event.delay_duration_hours}
        onSelectHour={handleSelectHour}
      />

      <TimelineScrubber />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="xl:col-span-5">
          <InterventionGauge intervention={latestResponse?.intervention ?? null} />
        </div>
        <div className="xl:col-span-7">
          <AffectedOrdersTable
            simulation={latestResponse}
            graphNodes={graphNodes}
          />
        </div>
      </div>
    </div>
  );
}

