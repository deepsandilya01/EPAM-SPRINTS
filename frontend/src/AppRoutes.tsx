"use client";

import { usePathname } from "next/navigation";

import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { OverviewPage } from "@/features/dashboard/pages/OverviewPage";
import { SettingsPage } from "@/features/settings/pages/SettingsPage";
import { SimulationPage } from "@/features/simulation/pages/SimulationPage";

export function AppRoutes() {
  const pathname = usePathname();

  if (pathname === "/simulation") {
    return <SimulationPage />;
  }
  if (pathname === "/overview") {
    return <OverviewPage />;
  }
  if (pathname === "/settings") {
    return <SettingsPage />;
  }

  return <DashboardPage />;
}
