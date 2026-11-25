import type { ReactNode } from "react";

import { cn } from "@/features/shared/utils/format";

export type BadgeTone = "neutral" | "feasible" | "breached" | "critical" | "dark";

interface BadgeProps {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
}

const TONE_CLASSES: Record<BadgeTone, string> = {
  neutral: "border-hairline bg-canvas text-ink-muted",
  feasible: "border-status-feasible-border bg-status-feasible-bg text-status-feasible",
  breached: "border-status-breached-border bg-status-breached-bg text-status-breached",
  critical: "border-status-critical-border bg-status-critical-bg text-status-critical",
  dark: "border-carbon-950 bg-carbon-950 text-white",
};

export function Badge({ children, tone = "neutral", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 font-mono text-[11px] font-medium uppercase tracking-wider",
        TONE_CLASSES[tone],
        className
      )}
    >
      {children}
    </span>
  );
}

