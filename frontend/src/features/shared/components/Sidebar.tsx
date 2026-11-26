"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Network,
  Settings,
  X,
} from "lucide-react";

import { cn } from "@/features/shared/utils/format";

const NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "/dashboard",
    matchPaths: ["/", "/dashboard"],
    icon: LayoutDashboard,
  },
  {
    label: "Disruption Simulation",
    href: "/simulation",
    matchPaths: ["/simulation"],
    icon: Activity,
  },
  {
    label: "Supply Chain Overview",
    href: "/overview",
    matchPaths: ["/overview"],
    icon: Network,
  },
  {
    label: "Settings",
    href: "/settings",
    matchPaths: ["/settings"],
    icon: Settings,
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export function Sidebar({
  collapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
}: SidebarProps) {
  const pathname = usePathname();

  const renderLinks = (isCollapsed: boolean) => (
    <nav aria-label="Primary Navigation" className="flex-1 space-y-1 px-2.5 py-4">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        const isActive = item.matchPaths.includes(pathname);

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onCloseMobile}
            title={isCollapsed ? item.label : undefined}
            className={cn(
              "flex items-center gap-3 rounded-sm px-3 py-2.5 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white",
              isActive
                ? "bg-carbon-800 text-white"
                : "text-[#A3A3A3] hover:bg-carbon-900 hover:text-white",
              isCollapsed && "justify-center px-2"
            )}
          >
            <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
            {!isCollapsed ? <span className="truncate">{item.label}</span> : null}
          </Link>
        );
      })}
    </nav>
  );

  return (
    <>
      <aside
        className={cn(
          "hidden shrink-0 flex-col border-r border-carbon-800 bg-carbon-950 text-white transition-[width] duration-200 lg:flex",
          collapsed ? "w-16" : "w-64"
        )}
      >
        <div
          className={cn(
            "flex h-14 items-center border-b border-carbon-800 px-4",
            collapsed ? "justify-center" : "justify-between"
          )}
        >
          {!collapsed ? (
            <Link href="/dashboard" className="flex items-center gap-2.5">
              <span className="flex h-7 w-7 items-center justify-center rounded-sm border border-[#333333] bg-carbon-800 font-mono text-xs font-bold tracking-tight text-white">
                RF
              </span>
              <div className="leading-tight">
                <span className="block text-sm font-semibold tracking-tight text-white">
                  RE:Flow
                </span>
                <span className="block font-mono text-[10px] uppercase tracking-widest text-[#777777]">
                  Photon · Sprint 2
                </span>
              </div>
            </Link>
          ) : (
            <Link
              href="/dashboard"
              title="RE:Flow"
              className="flex h-7 w-7 items-center justify-center rounded-sm border border-[#333333] bg-carbon-800 font-mono text-xs font-bold text-white"
            >
              RF
            </Link>
          )}

          {!collapsed ? (
            <button
              type="button"
              onClick={onToggleCollapse}
              aria-label="Collapse sidebar"
              className="rounded-sm p-1 text-[#A3A3A3] hover:bg-carbon-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
          ) : null}
        </div>

        {renderLinks(collapsed)}

        <div className="border-t border-carbon-800 p-2.5">
          {collapsed ? (
            <button
              type="button"
              onClick={onToggleCollapse}
              aria-label="Expand sidebar"
              className="flex w-full items-center justify-center rounded-sm p-2 text-[#A3A3A3] hover:bg-carbon-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          ) : (
            <div className="rounded-sm border border-carbon-800 bg-carbon-900 px-3 py-2.5">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[#777777]">
                Engine Target
              </p>
              <p className="mt-0.5 text-xs font-medium text-white">
                72h Temporal Pipeline
              </p>
            </div>
          )}
        </div>
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 flex lg:hidden" role="dialog" aria-modal="true">
          <div
            className="fixed inset-0 bg-black/50"
            onClick={onCloseMobile}
            aria-hidden="true"
          />
          <aside className="relative z-10 flex w-64 flex-col bg-carbon-950 text-white shadow-xl">
            <div className="flex h-14 items-center justify-between border-b border-carbon-800 px-4">
              <Link
                href="/dashboard"
                onClick={onCloseMobile}
                className="flex items-center gap-2.5"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-sm border border-[#333333] bg-carbon-800 font-mono text-xs font-bold text-white">
                  RF
                </span>
                <div>
                  <span className="block text-sm font-semibold text-white">RE:Flow</span>
                  <span className="block font-mono text-[10px] uppercase tracking-widest text-[#777777]">
                    Photon · Sprint 2
                  </span>
                </div>
              </Link>
              <button
                type="button"
                onClick={onCloseMobile}
                aria-label="Close navigation menu"
                className="rounded-sm p-1 text-[#A3A3A3] hover:bg-carbon-800 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            {renderLinks(false)}
          </aside>
        </div>
      ) : null}
    </>
  );
}

