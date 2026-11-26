import axios, { AxiosError, AxiosInstance } from "axios";

import { resolveApiBaseUrl } from "@/features/shared/utils/constants";

export type ApiErrorCode =
  | "BACKEND_UNAVAILABLE"
  | "CONNECTION_REFUSED"
  | "TIMEOUT"
  | "VALIDATION_ERROR"
  | "SERVER_ERROR"
  | "INVALID_RESPONSE"
  | "UNKNOWN_ERROR";

export class ApiClientError extends Error {
  public readonly code: ApiErrorCode;
  public readonly statusCode: number | null;
  public readonly details?: string;

  constructor(
    message: string,
    code: ApiErrorCode,
    statusCode: number | null = null,
    details?: string
  ) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

interface FastApiErrorPayload {
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }>;
  error?: string;
}

export function extractErrorMessage(error: unknown): ApiClientError {
  if (error instanceof ApiClientError) {
    return error;
  }

  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<FastApiErrorPayload>;

    if (axiosErr.code === "ECONNABORTED" || axiosErr.message.toLowerCase().includes("timeout")) {
      return new ApiClientError(
        "Request timed out while waiting for the FastAPI backend.",
        "TIMEOUT",
        null,
        axiosErr.message
      );
    }

    if (!axiosErr.response) {
      const isRefused =
        axiosErr.code === "ECONNREFUSED" ||
        axiosErr.message.includes("Network Error");
      return new ApiClientError(
        `Backend unreachable at ${customBaseUrl ?? (resolveApiBaseUrl() || "same-origin /api proxy")}. Verify that the FastAPI server is running.`,
        isRefused ? "CONNECTION_REFUSED" : "BACKEND_UNAVAILABLE",
        null,
        axiosErr.message
      );
    }

    const { status, data } = axiosErr.response;
    let detailMessage = "";

    if (data && typeof data === "object") {
      if (typeof data.detail === "string") {
        detailMessage = data.detail;
      } else if (Array.isArray(data.detail)) {
        detailMessage = data.detail
          .map((item) => {
            const loc = item.loc ? item.loc.join(".") : "field";
            return `${loc}: ${item.msg ?? "invalid"}`;
          })
          .join("; ");
      } else if (typeof data.error === "string") {
        detailMessage = data.error;
      }
    }

    if (status === 422 || status === 400) {
      return new ApiClientError(
        detailMessage || "Validation rejected by backend.",
        "VALIDATION_ERROR",
        status,
        detailMessage
      );
    }

    if (status >= 500) {
      return new ApiClientError(
        detailMessage || "Internal server error in simulation engine.",
        "SERVER_ERROR",
        status,
        detailMessage
      );
    }

    return new ApiClientError(
      detailMessage || `Request failed with HTTP ${status}.`,
      "UNKNOWN_ERROR",
      status,
      detailMessage
    );
  }

  if (error instanceof SyntaxError) {
    return new ApiClientError(
      "Received invalid JSON from backend.",
      "INVALID_RESPONSE",
      null,
      error.message
    );
  }

  if (error instanceof Error) {
    return new ApiClientError(error.message, "UNKNOWN_ERROR", null);
  }

  return new ApiClientError("Unexpected communication failure.", "UNKNOWN_ERROR", null);
}

let customBaseUrl: string | null = null;

export const axiosInstance: AxiosInstance = axios.create({
  baseURL: resolveApiBaseUrl(),
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

axiosInstance.interceptors.request.use((config) => {
  config.baseURL = customBaseUrl ?? resolveApiBaseUrl();
  return config;
});

export function setApiBaseUrl(url: string): void {
  const sanitized = url.trim().replace(/\/+$/, "");
  if (!sanitized) return;
  customBaseUrl = sanitized;
  axiosInstance.defaults.baseURL = sanitized;
}

export function getApiBaseUrl(): string {
  return customBaseUrl ?? resolveApiBaseUrl();
}

