"use client";

import { Clock, Minus, Plus, RotateCcw } from "lucide-react";

import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { TIMELINE_MAX_HOUR, TIMELINE_MIN_HOUR } from "@/features/shared/utils/constants";
import {
  selectDepletionTimeline,
  selectSelectedTimelineHour,
  selectSelectedTimelinePoint,
  selectStockoutHour,
} from "@/features/simulation/slices/simulationSelectors";
import { setSelectedTimelineHour } from "@/features/simulation/slices/simulationSlice";
import { useAppDispatch, useAppSelector } from "@/store";

export function TimelineScrubber() {
  const dispatch = useAppDispatch();
  const timeline = useAppSelector(selectDepletionTimeline);
  const selectedHour = useAppSelector(selectSelectedTimelineHour);
  const selectedPoint = useAppSelector(selectSelectedTimelinePoint);
  const stockoutHour = useAppSelector(selectStockoutHour);

  const hasTimeline = timeline.length > 0;

  const updateHour = (hour: number) => {
    dispatch(setSelectedTimelineHour(hour));
  };

  return (
    <Card>
      <CardHeader
        title="Hour 0–72 Timeline Scrubber"
        subtitle="Inspect warehouse inventory state hour-by-hour (client-side sync, zero extra API calls)"
        action={
          <div className="flex items-center gap-2">
            {stockoutHour !== null ? (
              <button
                type="button"
                disabled={!hasTimeline}
                onClick={() => updateHour(Math.round(stockoutHour))}
                className="rounded-sm border border-status-breached-border bg-status-breached-bg px-2.5 py-1 font-mono text-[11px] font-medium text-status-breached hover:opacity-90 disabled:opacity-40"
              >
                Jump to T_stockout ({stockoutHour.toFixed(0)}h)
              </button>
            ) : null}
            <button
              type="button"
              disabled={!hasTimeline || selectedHour === 0}
              onClick={() => updateHour(0)}
              className="inline-flex items-center gap-1 rounded-sm border border-hairline bg-surface px-2.5 py-1 text-[11px] font-medium text-ink hover:bg-canvas disabled:opacity-40"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              0h
            </button>
          </div>
        }
      />
      <CardBody className="space-y-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            disabled={!hasTimeline || selectedHour <= TIMELINE_MIN_HOUR}
            onClick={() => updateHour(selectedHour - 1)}
            aria-label="Previous hour"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-hairline bg-surface text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Minus className="h-3.5 w-3.5" />
          </button>

          <div className="flex-1">
            <input
              id="hour-timeline-slider"
              type="range"
              min={TIMELINE_MIN_HOUR}
              max={TIMELINE_MAX_HOUR}
              step={1}
              disabled={!hasTimeline}
              value={selectedHour}
              onChange={(e) => updateHour(Number(e.target.value))}
              aria-label="Simulation timeline hour scrubber (0 to 72)"
              className="reflow-slider disabled:cursor-not-allowed disabled:opacity-40"
            />
            <div className="mt-1.5 flex justify-between font-mono text-[10px] text-ink-muted">
              <span>0h</span>
              <span>12h</span>
              <span>24h</span>
              <span>36h</span>
              <span>48h</span>
              <span>60h</span>
              <span>72h</span>
            </div>
          </div>

          <button
            type="button"
            disabled={!hasTimeline || selectedHour >= TIMELINE_MAX_HOUR}
            onClick={() => updateHour(selectedHour + 1)}
            aria-label="Next hour"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-hairline bg-surface text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-sm border border-hairline bg-canvas px-3.5 py-2.5">
            <p className="flex items-center gap-1.5 text-[11px] text-ink-muted">
              <Clock className="h-3.5 w-3.5" aria-hidden="true" />
              Selected Hour
            </p>
            <p className="mt-1 font-mono text-lg font-semibold text-ink">
              Hour {selectedHour}
            </p>
          </div>

          <div className="rounded-sm border border-hairline bg-canvas px-3.5 py-2.5">
            <p className="text-[11px] text-ink-muted">Remaining Stock</p>
            <p className="mt-1 font-mono text-lg font-semibold text-ink">
              {selectedPoint ? `${selectedPoint.stock_units.toFixed(2)} units` : "—"}
            </p>
          </div>

          <div className="rounded-sm border border-hairline bg-canvas px-3.5 py-2.5">
            <p className="text-[11px] text-ink-muted">Inbound Supply Status</p>
            <div className="mt-1.5">
              {selectedPoint ? (
                selectedPoint.supply_blocked ? (
                  <Badge tone="breached">Supply Blocked</Badge>
                ) : (
                  <Badge tone="feasible">Supply Window Cleared</Badge>
                )
              ) : (
                <Badge tone="neutral">Awaiting Simulation</Badge>
              )}
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}

