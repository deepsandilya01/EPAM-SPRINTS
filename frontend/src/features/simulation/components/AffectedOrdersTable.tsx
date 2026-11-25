"use client";

import { useState } from "react";
import { PackageCheck } from "lucide-react";

import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import { EmptyState } from "@/features/shared/components/EmptyState";
import type { GraphNode } from "@/features/shared/types/graph";
import type {
  OrderImpactCategory,
  SimulationResponse,
} from "@/features/shared/types/simulation";
import { simulationApi } from "@/features/simulation/services/simulationApi";

interface AffectedOrdersTableProps {
  simulation: SimulationResponse | null;
  graphNodes: GraphNode[];
}

export function AffectedOrdersTable({
  simulation,
  graphNodes,
}: AffectedOrdersTableProps) {
  const [filter, setFilter] = useState<"ALL" | OrderImpactCategory>("ALL");

  const orderImpacts = simulationApi.deriveOrderImpacts(simulation, graphNodes);
  const failedCount = orderImpacts.filter((o) => o.category === "FAILED").length;
  const safeCount = orderImpacts.filter((o) => o.category === "SAFE").length;
  const unknownCount = orderImpacts.filter((o) => o.category === "UNKNOWN").length;

  const visibleOrders =
    filter === "ALL"
      ? orderImpacts
      : orderImpacts.filter((o) => o.category === filter);

  return (
    <Card>
      <CardHeader
        title="Affected Customer Orders"
        subtitle="Distinguishes failing commitments from safe downstream orders"
        action={
          simulation ? (
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="breached">Failed: {failedCount}</Badge>
              <Badge tone="feasible">Safe: {safeCount}</Badge>
              {unknownCount > 0 ? (
                <Badge tone="neutral">Unknown: {unknownCount}</Badge>
              ) : null}
            </div>
          ) : null
        }
      />
      <CardBody>
        {!simulation ? (
          <EmptyState
            icon={<PackageCheck className="h-8 w-8" />}
            title="No Order Impact Data"
            description="Run a disruption simulation to evaluate which downstream customer orders breach their delivery deadlines."
          />
        ) : orderImpacts.length === 0 ? (
          <EmptyState
            icon={<PackageCheck className="h-8 w-8" />}
            title="Zero Downstream Orders Impacted"
            description="No customer purchase orders were reached downstream from the selected supplier."
          />
        ) : (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div
                className="flex flex-wrap items-center gap-1.5"
                role="group"
                aria-label="Filter affected orders"
              >
                {(["ALL", "FAILED", "SAFE", "UNKNOWN"] as const).map((tab) => {
                  const count =
                    tab === "ALL"
                      ? orderImpacts.length
                      : tab === "FAILED"
                        ? failedCount
                        : tab === "SAFE"
                          ? safeCount
                          : unknownCount;

                  if (tab === "UNKNOWN" && unknownCount === 0) return null;

                  return (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setFilter(tab)}
                      className={`rounded-sm border px-2.5 py-1 font-mono text-[11px] font-medium transition-colors ${
                        filter === tab
                          ? "border-carbon-950 bg-carbon-950 text-white"
                          : "border-hairline bg-surface text-ink-muted hover:bg-canvas hover:text-ink"
                      }`}
                    >
                      {tab} ({count})
                    </button>
                  );
                })}
              </div>

              <span className="font-mono text-[11px] text-ink-muted">
                Backend total_breached: {simulation.stockout.total_breached}
              </span>
            </div>

            <div className="overflow-x-auto rounded-sm border border-hairline">
              <table className="w-full border-collapse text-left text-xs">
                <thead>
                  <tr className="border-b border-hairline bg-canvas text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
                    <th className="px-3.5 py-2.5">Order ID</th>
                    <th className="px-3.5 py-2.5">Customer / Product</th>
                    <th className="px-3.5 py-2.5">Delivery Deadline</th>
                    <th className="px-3.5 py-2.5">Status</th>
                    <th className="px-3.5 py-2.5">Assessment Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hairline bg-surface">
                  {visibleOrders.map((order) => (
                    <tr key={order.order_id} className="hover:bg-canvas/60">
                      <td className="whitespace-nowrap px-3.5 py-2.5 font-mono font-semibold text-ink">
                        {order.order_id}
                      </td>
                      <td className="px-3.5 py-2.5 text-ink-muted">
                        {order.customer ? (
                          <span>
                            <span className="font-medium text-ink">{order.customer}</span>
                            {order.product_id ? ` · ${order.product_id}` : ""}
                            {order.quantity ? ` (${order.quantity} units)` : ""}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="whitespace-nowrap px-3.5 py-2.5 font-mono text-ink">
                        {order.delivery_deadline_hours !== null
                          ? `Hour ${order.delivery_deadline_hours.toFixed(1)}`
                          : "—"}
                      </td>
                      <td className="whitespace-nowrap px-3.5 py-2.5">
                        {order.category === "FAILED" ? (
                          <Badge tone="breached">FAILED</Badge>
                        ) : order.category === "SAFE" ? (
                          <Badge tone="feasible">SAFE</Badge>
                        ) : (
                          <Badge tone="neutral">UNKNOWN</Badge>
                        )}
                      </td>
                      <td className="px-3.5 py-2.5 text-ink-muted">{order.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}

