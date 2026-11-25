"use client";

import { useState, type ReactNode } from "react";

import { useBackendSync } from "@/features/dashboard/hooks/useBackendSync";

import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { refreshBackendData } = useBackendSync();

  return (
    <div className="flex min-h-screen w-full bg-canvas text-ink">
      <Sidebar
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed((prev) => !prev)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <TopNav
          onOpenMobileMenu={() => setMobileOpen(true)}
          onRefreshBackend={refreshBackendData}
        />
        <main className="mx-auto w-full max-w-[1440px] flex-1 p-4 sm:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

