export function resolveApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim().replace(/\/+$/, "");
  if (configured) {
    return configured;
  }
  // In production on Render without NEXT_PUBLIC_API_BASE_URL baked in at build time,
  // route calls through Next.js same-origin /api/* proxy to BACKEND_HOST / BACKEND_URL.
  if (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    return "";
  }
  return "http://localhost:5001";
}

export const API_BASE_URL = resolveApiBaseUrl();

export const DEFAULT_BENCHMARK_REQUEST = {
  supplier_id: "SUP-01" as const,
  disruption_type: "SUPPLIER_DELAY" as const,
  delay_duration_hours: 8.0,
  description: "Benchmark test disruption",
};

export const TIMELINE_MIN_HOUR = 0;
export const TIMELINE_MAX_HOUR = 72;

export const SUPPORTED_SUPPLIERS = [
  { id: "SUP-01", label: "SUP-01 — Apex Components (Pune)" },
  { id: "SUP-02", label: "SUP-02 — Bharat Precision Parts (Indore)" },
] as const;

export const SUPPORTED_DISRUPTION_TYPES = [
  { value: "SUPPLIER_DELAY", label: "SUPPLIER_DELAY — Inbound Shipment Delay" },
  { value: "CAPACITY_DROP", label: "CAPACITY_DROP — Tier-1 Capacity Reduction" },
  { value: "FORCE_MAJEURE", label: "FORCE_MAJEURE — Force Majeure Halting" },
] as const;
