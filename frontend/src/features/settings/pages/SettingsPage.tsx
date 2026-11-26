"use client";

import { useState, type FormEvent } from "react";
import { Check, RotateCcw, Server } from "lucide-react";

import { useBackendSync } from "@/features/dashboard/hooks/useBackendSync";
import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import {
  getApiBaseUrl,
  setApiBaseUrl,
} from "@/features/shared/services/axiosInstance";
import { API_BASE_URL } from "@/features/shared/utils/constants";
import { resetSimulationState } from "@/features/simulation/slices/simulationSlice";
import { useAppDispatch } from "@/store";

export function SettingsPage() {
  const dispatch = useAppDispatch();
  const { connectionStatus, health, refreshBackendData } = useBackendSync();
  const [urlInput, setUrlInput] = useState(getApiBaseUrl());
  const [savedNotice, setSavedNotice] = useState(false);

  const handleSaveEndpoint = (e: FormEvent) => {
    e.preventDefault();
    setApiBaseUrl(urlInput);
    setSavedNotice(true);
    refreshBackendData();
    setTimeout(() => setSavedNotice(false), 2500);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          title="FastAPI Backend Integration"
          subtitle="Configure the Axios base URL for RE:Flow REST API communication"
          action={
            <Badge
              tone={
                connectionStatus === "connected"
                  ? "feasible"
                  : connectionStatus === "disconnected"
                    ? "breached"
                    : "neutral"
              }
            >
              {connectionStatus}
            </Badge>
          }
        />
        <CardBody className="space-y-4">
          <form onSubmit={handleSaveEndpoint} className="flex flex-wrap items-end gap-3">
            <div className="min-w-[260px] flex-1">
              <label
                htmlFor="api-base-url"
                className="mb-1.5 block text-xs font-medium text-ink"
              >
                API Base URL (Default from NEXT_PUBLIC_API_BASE_URL: {API_BASE_URL})
              </label>
              <input
                id="api-base-url"
                type="url"
                required
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="w-full rounded-sm border border-hairline bg-surface px-3 py-2 font-mono text-xs text-ink focus:border-carbon-950 focus:outline-none focus:ring-1 focus:ring-carbon-950"
              />
            </div>

            <button
              type="submit"
              className="inline-flex items-center gap-1.5 rounded-sm border border-carbon-950 bg-carbon-950 px-4 py-2 text-xs font-semibold text-white hover:bg-carbon-800"
            >
              {savedNotice ? (
                <>
                  <Check className="h-3.5 w-3.5" aria-hidden="true" />
                  Applied &amp; Synced
                </>
              ) : (
                <>
                  <Server className="h-3.5 w-3.5" aria-hidden="true" />
                  Apply &amp; Test Connection
                </>
              )}
            </button>
          </form>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-sm border border-hairline bg-canvas p-3">
              <span className="text-[11px] text-ink-muted">Simulation Endpoint</span>
              <p className="mt-1 font-mono text-xs font-semibold text-ink">
                POST /api/v1/simulation/disrupt
              </p>
            </div>
            <div className="rounded-sm border border-hairline bg-canvas p-3">
              <span className="text-[11px] text-ink-muted">Graph Endpoint</span>
              <p className="mt-1 font-mono text-xs font-semibold text-ink">
                GET /api/graph
              </p>
            </div>
            <div className="rounded-sm border border-hairline bg-canvas p-3">
              <span className="text-[11px] text-ink-muted">Backend Service</span>
              <p className="mt-1 font-mono text-xs font-semibold text-ink">
                {health ? `${health.service} (v${health.version})` : "Not connected"}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader
          title="Client State Controls"
          subtitle="Clear Redux simulation state and session activity log"
        />
        <CardBody>
          <button
            type="button"
            onClick={() => dispatch(resetSimulationState())}
            className="inline-flex items-center gap-1.5 rounded-sm border border-hairline bg-surface px-3.5 py-2 text-xs font-medium text-ink hover:bg-canvas"
          >
            <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
            Reset Simulation Redux State
          </button>
        </CardBody>
      </Card>
    </div>
  );
}

