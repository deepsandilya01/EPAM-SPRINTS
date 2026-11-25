"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, RefreshCw, ShieldCheck, User } from "lucide-react";

import { Badge } from "@/features/shared/components/Badge";
import { useAppSelector } from "@/store";

interface TopNavProps {
  onOpenMobileMenu: () => void;
  onRefreshBackend: () => void;
}

const ROUTE_META: Record<string, { title: string; breadcrumb: string }> = {
  "/": { title: "Operational Dashboard", breadcrumb: "Dashboard" },
  "/dashboard": { title: "Operational Dashboard", breadcrumb: "Dashboard" },
  "/simulation": {
    title: "Disruption Simulation",
    breadcrumb: "Disruption Simulation",
  },
  "/overview": {
    title: "Supply Chain Overview",
    breadcrumb: "Supply Chain Overview",
  },
  "/settings": {
    title: "System Settings",
    breadcrumb: "Settings",
  },
};

export function TopNav({ onOpenMobileMenu, onRefreshBackend }: TopNavProps) {
  const pathname = usePathname();
  const { connectionStatus, health, graphLoading } = useAppSelector(
    (state) => state.dashboard
  );
  const executionState = useAppSelector((state) => state.simulation.executionState);

  const meta = ROUTE_META[pathname] ?? {
    title: "RE:Flow",
    breadcrumb: "Workspace",
  };

  const connectionTone =
    connectionStatus === "connected"
      ? "feasible"
      : connectionStatus === "disconnected"
        ? "breached"
        : "neutral";

  const connectionLabel =
    connectionStatus === "connected"
      ? "Backend Connected"
      : connectionStatus === "disconnected"
        ? "Backend Offline"
        : "Checking Backend";

  return (
    <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center justify-between gap-4 border-b border-hairline bg-surface px-4 sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          aria-label="Open navigation menu"
          className="rounded-sm border border-hairline p-1.5 text-ink hover:bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-carbon-950 lg:hidden"
        >
          <Menu className="h-4 w-4" />
        </button>

        <div className="min-w-0">
          <nav
            aria-label="Breadcrumb"
            className="flex items-center gap-1.5 text-[11px] text-ink-muted"
          >
            <Link href="/dashboard" className="hover:text-ink">
              RE:Flow
            </Link>
            <span aria-hidden="true">/</span>
            <span className="truncate font-medium text-ink">{meta.breadcrumb}</span>
          </nav>
          <h1 className="truncate text-sm font-semibold tracking-tight text-ink">
            {meta.title}
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        <Badge tone={connectionTone} className="hidden sm:inline-flex">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              connectionStatus === "connected"
                ? "bg-status-feasible"
                : connectionStatus === "disconnected"
                  ? "bg-status-breached"
                  : "bg-ink-muted"
            }`}
          />
          {connectionLabel}
        </Badge>

        <div className="hidden items-center gap-1.5 rounded-sm border border-hairline bg-canvas px-2.5 py-1 text-[11px] text-ink-muted md:flex">
          <ShieldCheck className="h-3.5 w-3.5 text-ink" aria-hidden="true" />
          <span className="font-mono uppercase">
            {health
              ? `${health.node_count}N · ${health.edge_count}E · ${executionState}`
              : `System: ${executionState}`}
          </span>
        </div>

        <button
          type="button"
          onClick={onRefreshBackend}
          disabled={graphLoading}
          title="Sync backend health and graph"
          aria-label="Sync backend status"
          className="inline-flex items-center gap-1.5 rounded-sm border border-hairline bg-surface px-2.5 py-1.5 text-xs font-medium text-ink hover:bg-canvas disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-carbon-950"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${graphLoading ? "animate-spin" : ""}`}
            aria-hidden="true"
          />
          <span className="hidden sm:inline">Sync</span>
        </button>

        <div
          className="flex h-8 w-8 items-center justify-center rounded-sm border border-hairline bg-canvas text-ink-muted"
          title="Workspace Operator"
          aria-label="Workspace placeholder"
        >
          <User className="h-4 w-4" aria-hidden="true" />
        </div>
      </div>
    </header>
  );
}

