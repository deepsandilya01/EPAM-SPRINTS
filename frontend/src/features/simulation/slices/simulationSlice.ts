import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { ApiClientError } from "@/features/shared/services/axiosInstance";
import type {
  DisruptionRequest,
  DisruptionType,
  SimulationResponse,
} from "@/features/shared/types/simulation";
import { TIMELINE_MAX_HOUR, TIMELINE_MIN_HOUR } from "@/features/shared/utils/constants";
import { simulationApi } from "@/features/simulation/services/simulationApi";

export type SimulationExecutionState =
  | "idle"
  | "validating"
  | "running"
  | "success"
  | "failed";

export interface SimulationErrorState {
  code: string;
  message: string;
  statusCode: number | null;
}

export interface SimulationState {
  executionState: SimulationExecutionState;
  currentRequest: DisruptionRequest | null;
  latestResponse: SimulationResponse | null;
  error: SimulationErrorState | null;
  selectedSupplier: string;
  selectedDisruptionType: DisruptionType;
  selectedTimelineHour: number;
  sessionRuns: SimulationResponse[];
}

const initialState: SimulationState = {
  executionState: "idle",
  currentRequest: null,
  latestResponse: null,
  error: null,
  selectedSupplier: "SUP-01",
  selectedDisruptionType: "SUPPLIER_DELAY",
  selectedTimelineHour: 0,
  sessionRuns: [],
};

export const runDisruptionSimulationThunk = createAsyncThunk<
  SimulationResponse,
  DisruptionRequest,
  { rejectValue: { code: string; message: string; statusCode: number | null } }
>("simulation/runDisruption", async (request, { rejectWithValue }) => {
  try {
    return await simulationApi.runDisruptionSimulation(request);
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue({
        code: err.code,
        message: err.message,
        statusCode: err.statusCode,
      });
    }
    return rejectWithValue({
      code: "UNKNOWN_ERROR",
      message: err instanceof Error ? err.message : "Simulation execution failed.",
      statusCode: null,
    });
  }
});

export const runBenchmarkSimulationThunk = createAsyncThunk<
  SimulationResponse,
  void,
  { rejectValue: { code: string; message: string; statusCode: number | null } }
>("simulation/runBenchmark", async (_, { rejectWithValue }) => {
  try {
    return await simulationApi.runBenchmarkSimulation();
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue({
        code: err.code,
        message: err.message,
        statusCode: err.statusCode,
      });
    }
    return rejectWithValue({
      code: "UNKNOWN_ERROR",
      message: err instanceof Error ? err.message : "Benchmark execution failed.",
      statusCode: null,
    });
  }
});

const simulationSlice = createSlice({
  name: "simulation",
  initialState,
  reducers: {
    setValidating(state, action: PayloadAction<DisruptionRequest>) {
      state.executionState = "validating";
      state.currentRequest = action.payload;
      state.error = null;
    },
    setValidationFailed(state, action: PayloadAction<string>) {
      state.executionState = "failed";
      state.error = {
        code: "VALIDATION_ERROR",
        message: action.payload,
        statusCode: null,
      };
    },
    setSelectedSupplier(state, action: PayloadAction<string>) {
      state.selectedSupplier = action.payload;
    },
    setSelectedDisruptionType(state, action: PayloadAction<DisruptionType>) {
      state.selectedDisruptionType = action.payload;
    },
    setSelectedTimelineHour(state, action: PayloadAction<number>) {
      const clamped = Math.max(
        TIMELINE_MIN_HOUR,
        Math.min(TIMELINE_MAX_HOUR, Math.round(action.payload))
      );
      state.selectedTimelineHour = clamped;
    },
    clearSimulationError(state) {
      state.error = null;
      if (state.executionState === "failed") {
        state.executionState = state.latestResponse ? "success" : "idle";
      }
    },
    resetSimulationState() {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(runDisruptionSimulationThunk.pending, (state, action) => {
        state.executionState = "running";
        state.currentRequest = action.meta.arg;
        state.selectedSupplier = action.meta.arg.supplier_id;
        state.selectedDisruptionType = action.meta.arg.disruption_type;
        state.error = null;
      })
      .addCase(runDisruptionSimulationThunk.fulfilled, (state, action) => {
        state.executionState = "success";
        state.latestResponse = action.payload;
        state.error = null;
        state.selectedTimelineHour = 0;
        state.sessionRuns = [action.payload, ...state.sessionRuns].slice(0, 10);
      })
      .addCase(runDisruptionSimulationThunk.rejected, (state, action) => {
        state.executionState = "failed";
        state.error = action.payload ?? {
          code: "UNKNOWN_ERROR",
          message: "Failed to execute simulation.",
          statusCode: null,
        };
      })
      .addCase(runBenchmarkSimulationThunk.pending, (state) => {
        state.executionState = "running";
        state.currentRequest = {
          supplier_id: "SUP-01",
          disruption_type: "SUPPLIER_DELAY",
          delay_duration_hours: 8.0,
          description: "Canonical 8-hour benchmark scenario",
        };
        state.selectedSupplier = "SUP-01";
        state.selectedDisruptionType = "SUPPLIER_DELAY";
        state.error = null;
      })
      .addCase(runBenchmarkSimulationThunk.fulfilled, (state, action) => {
        state.executionState = "success";
        state.latestResponse = action.payload;
        state.error = null;
        state.selectedTimelineHour = 0;
        state.sessionRuns = [action.payload, ...state.sessionRuns].slice(0, 10);
      })
      .addCase(runBenchmarkSimulationThunk.rejected, (state, action) => {
        state.executionState = "failed";
        state.error = action.payload ?? {
          code: "UNKNOWN_ERROR",
          message: "Failed to run canonical benchmark.",
          statusCode: null,
        };
      });
  },
});

export const {
  setValidating,
  setValidationFailed,
  setSelectedSupplier,
  setSelectedDisruptionType,
  setSelectedTimelineHour,
  clearSimulationError,
  resetSimulationState,
} = simulationSlice.actions;

export default simulationSlice.reducer;

