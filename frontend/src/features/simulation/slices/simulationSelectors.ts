import { createSelector } from "@reduxjs/toolkit";

import type { RootState } from "@/store";

export const selectSimulationState = (state: RootState) => state.simulation;
export const selectLatestResponse = (state: RootState) => state.simulation.latestResponse;
export const selectExecutionState = (state: RootState) => state.simulation.executionState;
export const selectSimulationError = (state: RootState) => state.simulation.error;
export const selectSelectedTimelineHour = (state: RootState) =>
  state.simulation.selectedTimelineHour;
export const selectSessionRuns = (state: RootState) => state.simulation.sessionRuns;

export const selectDepletionTimeline = createSelector(
  [selectLatestResponse],
  (response) => response?.depletion_timeline ?? []
);

export const selectSelectedTimelinePoint = createSelector(
  [selectDepletionTimeline, selectSelectedTimelineHour],
  (timeline, selectedHour) => {
    if (timeline.length === 0) {
      return null;
    }
    return (
      timeline.find((point) => point.hour === selectedHour) ??
      timeline[Math.min(selectedHour, timeline.length - 1)] ??
      null
    );
  }
);

export const selectSelectedStock = createSelector(
  [selectSelectedTimelinePoint],
  (point) => (point ? point.stock_units : null)
);

export const selectStockoutHour = createSelector(
  [selectLatestResponse],
  (response) => response?.stockout.stockout_hour ?? null
);

export const selectInterventionStatus = createSelector(
  [selectLatestResponse],
  (response) => response?.intervention.status ?? null
);

export const selectDeltaT = createSelector(
  [selectLatestResponse],
  (response) => response?.intervention.delta_t_hours ?? null
);

export const selectAffectedOrders = createSelector(
  [selectLatestResponse],
  (response) => response?.impact.affected_orders ?? []
);

export const selectBreachedOrders = createSelector(
  [selectLatestResponse],
  (response) => response?.stockout.breached_orders ?? []
);

export const selectExecutionTime = createSelector(
  [selectLatestResponse],
  (response) => response?.execution_time_ms ?? null
);

