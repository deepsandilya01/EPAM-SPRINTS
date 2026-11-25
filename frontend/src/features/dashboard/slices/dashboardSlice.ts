import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { dashboardApi } from "@/features/dashboard/services/dashboardApi";
import { ApiClientError } from "@/features/shared/services/axiosInstance";
import type { GraphEdge, GraphNode, HealthResponse } from "@/features/shared/types/graph";

export type BackendConnectionStatus = "checking" | "connected" | "disconnected";

export interface DashboardState {
  connectionStatus: BackendConnectionStatus;
  health: HealthResponse | null;
  nodes: GraphNode[];
  edges: GraphEdge[];
  graphLoading: boolean;
  graphError: string | null;
  undoDepth: number;
  canUndo: boolean;
  lastSyncedAt: string | null;
}

const initialState: DashboardState = {
  connectionStatus: "checking",
  health: null,
  nodes: [],
  edges: [],
  graphLoading: false,
  graphError: null,
  undoDepth: 0,
  canUndo: false,
  lastSyncedAt: null,
};

export const fetchBackendHealthThunk = createAsyncThunk<
  HealthResponse,
  void,
  { rejectValue: string }
>("dashboard/fetchHealth", async (_, { rejectWithValue }) => {
  try {
    return await dashboardApi.getHealth();
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue(err.message);
    }
    return rejectWithValue("Unable to reach FastAPI health endpoint.");
  }
});

export const fetchSupplyChainGraphThunk = createAsyncThunk<
  { nodes: GraphNode[]; edges: GraphEdge[] },
  void,
  { rejectValue: string }
>("dashboard/fetchGraph", async (_, { rejectWithValue }) => {
  try {
    const graph = await dashboardApi.getGraph();
    return {
      nodes: graph.nodes,
      edges: graph.edges,
    };
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue(err.message);
    }
    return rejectWithValue("Unable to load supply-chain graph from FastAPI.");
  }
});

export const deleteGraphNodeThunk = createAsyncThunk<
  { nodes: GraphNode[]; edges: GraphEdge[] },
  string,
  { rejectValue: string }
>("dashboard/deleteNode", async (nodeId, { rejectWithValue }) => {
  try {
    const res = await dashboardApi.deleteNode(nodeId);
    const graph = res.graph ?? (await dashboardApi.getGraph());
    return {
      nodes: graph.nodes,
      edges: graph.edges,
    };
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue(err.message);
    }
    return rejectWithValue("Unable to delete node from supply-chain graph.");
  }
});

export const undoGraphThunk = createAsyncThunk<
  { nodes: GraphNode[]; edges: GraphEdge[] },
  void,
  { rejectValue: string }
>("dashboard/undoGraph", async (_, { rejectWithValue }) => {
  try {
    const res = await dashboardApi.undoGraph();
    const graph = res.graph ?? (await dashboardApi.getGraph());
    return {
      nodes: graph.nodes,
      edges: graph.edges,
    };
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue(err.message);
    }
    return rejectWithValue("Unable to undo last graph operation.");
  }
});

export const resetGraphThunk = createAsyncThunk<
  { nodes: GraphNode[]; edges: GraphEdge[] },
  void,
  { rejectValue: string }
>("dashboard/resetGraph", async (_, { rejectWithValue }) => {
  try {
    const res = await dashboardApi.resetGraph();
    const graph = res.graph ?? (await dashboardApi.getGraph());
    return {
      nodes: graph.nodes,
      edges: graph.edges,
    };
  } catch (err) {
    if (err instanceof ApiClientError) {
      return rejectWithValue(err.message);
    }
    return rejectWithValue("Unable to reset supply-chain graph.");
  }
});

const dashboardSlice = createSlice({
  name: "dashboard",
  initialState,
  reducers: {
    setConnectionChecking(state) {
      state.connectionStatus = "checking";
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBackendHealthThunk.pending, (state) => {
        state.connectionStatus = "checking";
      })
      .addCase(fetchBackendHealthThunk.fulfilled, (state, action) => {
        state.connectionStatus = "connected";
        state.health = action.payload;
        state.lastSyncedAt = new Date().toISOString();
      })
      .addCase(fetchBackendHealthThunk.rejected, (state) => {
        state.connectionStatus = "disconnected";
        state.health = null;
      })
      .addCase(fetchSupplyChainGraphThunk.pending, (state) => {
        state.graphLoading = true;
        state.graphError = null;
      })
      .addCase(fetchSupplyChainGraphThunk.fulfilled, (state, action) => {
        state.graphLoading = false;
        state.nodes = action.payload.nodes;
        state.edges = action.payload.edges;
        state.graphError = null;
        state.lastSyncedAt = new Date().toISOString();
      })
      .addCase(fetchSupplyChainGraphThunk.rejected, (state, action) => {
        state.graphLoading = false;
        state.graphError = action.payload ?? "Failed to load graph topology.";
      })
      .addCase(deleteGraphNodeThunk.pending, (state) => {
        state.graphLoading = true;
        state.graphError = null;
      })
      .addCase(deleteGraphNodeThunk.fulfilled, (state, action) => {
        state.graphLoading = false;
        state.nodes = action.payload.nodes;
        state.edges = action.payload.edges;
        state.undoDepth += 1;
        state.canUndo = state.undoDepth > 0;
        if (state.health) {
          state.health.node_count = action.payload.nodes.length;
          state.health.edge_count = action.payload.edges.length;
        }
      })
      .addCase(deleteGraphNodeThunk.rejected, (state, action) => {
        state.graphLoading = false;
        state.graphError = action.payload ?? "Failed to delete node.";
      })
      .addCase(undoGraphThunk.fulfilled, (state, action) => {
        state.nodes = action.payload.nodes;
        state.edges = action.payload.edges;
        state.undoDepth = Math.max(0, state.undoDepth - 1);
        state.canUndo = state.undoDepth > 0;
        if (state.health) {
          state.health.node_count = action.payload.nodes.length;
          state.health.edge_count = action.payload.edges.length;
        }
      })
      .addCase(resetGraphThunk.fulfilled, (state, action) => {
        state.nodes = action.payload.nodes;
        state.edges = action.payload.edges;
        state.undoDepth = 0;
        state.canUndo = false;
        if (state.health) {
          state.health.node_count = action.payload.nodes.length;
          state.health.edge_count = action.payload.edges.length;
        }
      });
  },
});

export const { setConnectionChecking } = dashboardSlice.actions;
export default dashboardSlice.reducer;
