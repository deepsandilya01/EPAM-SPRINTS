import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppShell } from "@/features/shared/components/AppShell";

import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "RE:Flow — Temporal Disruption Simulation & Intervention Engine",
  description:
    "Team PHOTON Sprint 2 decision-intelligence console for supply-chain disruption simulation, inventory depletion modeling, and intervention window analysis.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-canvas text-ink antialiased">
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
