"use client";

import { useState } from "react";
import { Network } from "lucide-react";

import { SupplyChainGraph } from "@/features/dashboard/components/SupplyChainGraph";
import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { EmptyState } from "@/features/shared/components/EmptyState";
import { selectLatestResponse } from "@/features/simulation/slices/simulationSelectors";
import { useAppSelector } from "@/store";

type TierFilter = "all" | "supplier" | "part" | "product" | "order";

export function OverviewPage() {
  const { nodes, edges, graphLoading, graphError } = useAppSelector(
    (state) => state.dashboard
  );
  const latestResponse = useAppSelector(selectLatestResponse);
  const [tierFilter, setTierFilter] = useState<TierFilter>("all");

  const counts = {
    supplier: nodes.filter((n) => n.kind === "supplier" || n.tier === "supplier").length,
    part: nodes.filter((n) => n.kind === "part" || n.tier === "part").length,
    product: nodes.filter((n) => n.kind === "product" || n.tier === "product").length,
    order: nodes.filter((n) => n.kind === "order" || n.tier === "order").length,
  };

  const filteredNodes =
    tierFilter === "all"
      ? nodes
      : nodes.filter((n) => n.kind === tierFilter || n.tier === tierFilter);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Card>
          <CardBody className="p-4">
            <span className="text-[11px] text-ink-muted">Tier 1 · Suppliers</span>
            <p className="mt-1 font-mono text-2xl font-bold text-ink">{counts.supplier}</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="p-4">
            <span className="text-[11px] text-ink-muted">Tier 2 · BOM Parts</span>
            <p className="mt-1 font-mono text-2xl font-bold text-ink">{counts.part}</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="p-4">
            <span className="text-[11px] text-ink-muted">Tier 3 · Finished Products</span>
            <p className="mt-1 font-mono text-2xl font-bold text-ink">{counts.product}</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="p-4">
            <span className="text-[11px] text-ink-muted">Tier 4 · Customer Orders</span>
            <p className="mt-1 font-mono text-2xl font-bold text-ink">{counts.order}</p>
          </CardBody>
        </Card>
      </div>

      <SupplyChainGraph
        nodes={nodes}
        edges={edges}
        simulation={latestResponse}
      />

      <Card>
        <CardHeader
          title="Supply Chain Network Entities"
          subtitle="Live topology from GET /api/graph"
          action={<Badge tone="neutral">{edges.length} Directed Edges</Badge>}
        />
        <CardBody className="space-y-4">
          {graphError ? (
            <div
              role="alert"
              className="rounded-sm border border-status-breached-border bg-status-breached-bg px-4 py-3 text-xs text-status-breached"
            >
              {graphError}
            </div>
          ) : null}

          <div
            className="flex flex-wrap gap-1.5"
            role="group"
            aria-label="Filter graph nodes by tier"
          >
            {(["all", "supplier", "part", "product", "order"] as const).map((tier) => (
              <button
                key={tier}
                type="button"
                onClick={() => setTierFilter(tier)}
                className={`rounded-sm border px-3 py-1.5 font-mono text-[11px] font-medium uppercase transition-colors ${
                  tierFilter === tier
                    ? "border-carbon-950 bg-carbon-950 text-white"
                    : "border-hairline bg-surface text-ink-muted hover:bg-canvas hover:text-ink"
                }`}
              >
                {tier}
              </button>
            ))}
          </div>

          {graphLoading ? (
            <p className="py-6 text-center text-xs text-ink-muted">
              Loading graph topology from FastAPI…
            </p>
          ) : filteredNodes.length === 0 ? (
            <EmptyState
              icon={<Network className="h-8 w-8" />}
              title="No Network Entities Available"
              description="Connect to the FastAPI backend to load the 4-tier supply chain DAG."
            />
          ) : (
            <div className="overflow-x-auto rounded-sm border border-hairline">
              <table className="w-full border-collapse text-left text-xs">
                <thead>
                  <tr className="border-b border-hairline bg-canvas text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
                    <th className="px-3.5 py-2.5">ID</th>
                    <th className="px-3.5 py-2.5">Tier</th>
                    <th className="px-3.5 py-2.5">Label / Name</th>
                    <th className="px-3.5 py-2.5">Calibration / Parameters</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hairline bg-surface">
                  {filteredNodes.map((node) => {
                    const details: string[] = [];
                    if (typeof node.recovery_lead_time_hours === "number") {
                      details.push(`t_recovery=${node.recovery_lead_time_hours}h`);
                    }
                    if (node.location) {
                      details.push(`location=${node.location}`);
                    }
                    if (typeof node.initial_stock_units === "number") {
                      details.push(`stock=${node.initial_stock_units}`);
                    }
                    if (typeof node.hourly_consumption_units === "number") {
                      details.push(`burn=${node.hourly_consumption_units}/hr`);
                    }
                    if (node.parts_needed) {
                      details.push(`BOM: ${node.parts_needed}`);
                    }
                    if (typeof node.delivery_deadline_hours === "number") {
                      details.push(`deadline=${node.delivery_deadline_hours}h`);
                    }
                    if (typeof node.quantity === "number") {
                      details.push(`qty=${node.quantity}`);
                    }

                    return (
                      <tr key={node.id} className="hover:bg-canvas/60">
                        <td className="whitespace-nowrap px-3.5 py-2.5 font-mono font-semibold text-ink">
                          {node.id}
                        </td>
                        <td className="whitespace-nowrap px-3.5 py-2.5">
                          <Badge tone="neutral">{node.kind || node.tier}</Badge>
                        </td>
                        <td className="px-3.5 py-2.5 text-ink">
                          {node.name ?? node.label ?? node.id}
                        </td>
                        <td className="px-3.5 py-2.5 font-mono text-[11px] text-ink-muted">
                          {details.join(" · ") || "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}

