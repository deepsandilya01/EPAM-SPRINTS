import {
  ApiClientError,
  axiosInstance,
  extractErrorMessage,
} from "@/features/shared/services/axiosInstance";
import type {
  DownstreamResponse,
  GraphMutationResponse,
  GraphResponse,
  HealthResponse,
} from "@/features/shared/types/graph";

export const dashboardApi = {
  async getHealth(): Promise<HealthResponse> {
    try {
      const response = await axiosInstance.get<HealthResponse>("/api/health");
      if (!response.data || typeof response.data.status !== "string") {
        throw new ApiClientError("Invalid health response.", "INVALID_RESPONSE");
      }
      return response.data;
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  async getGraph(): Promise<GraphResponse> {
    try {
      const response = await axiosInstance.get<GraphResponse>("/api/graph");
      if (
        !response.data ||
        !Array.isArray(response.data.nodes) ||
        !Array.isArray(response.data.edges)
      ) {
        throw new ApiClientError("Invalid graph payload.", "INVALID_RESPONSE");
      }
      return response.data;
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  async getDownstream(nodeId: string): Promise<DownstreamResponse> {
    try {
      const response = await axiosInstance.get<DownstreamResponse>(
        `/api/downstream/${encodeURIComponent(nodeId)}`
      );
      return response.data;
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  async deleteNode(nodeId: string): Promise<GraphMutationResponse> {
    try {
      const response = await axiosInstance.delete<GraphMutationResponse>(
        `/api/node/${encodeURIComponent(nodeId)}`
      );
      return response.data;
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  async undoGraph(): Promise<GraphMutationResponse> {
    try {
      const response = await axiosInstance.post<GraphMutationResponse>("/api/undo");
      return response.data;
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  async resetGraph(): Promise<GraphMutationResponse> {
    try {
      const response = await axiosInstance.post<GraphMutationResponse>("/api/reset");
      return response.data;
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },
};

