import {
  ApiClientError,
  axiosInstance,
  extractErrorMessage,
} from "@/features/shared/services/axiosInstance";
import type { GraphNode } from "@/features/shared/types/graph";
import type {
  DerivedOrderImpact,
  DisruptionRequest,
  HourlyStockPoint,
  SimulationResponse,
} from "@/features/shared/types/simulation";

function assertValidSimulationPayload(data: unknown): SimulationResponse {
  if (!data || typeof data !== "object") {
    throw new ApiClientError(
      "Simulation response is empty or not a JSON object.",
      "INVALID_RESPONSE"
    );
  }

  const candidate = data as Partial<SimulationResponse>;

  if (
    !candidate.event ||
    !candidate.impact ||
    !candidate.stockout ||
    !candidate.intervention ||
    typeof candidate.execution_time_ms !== "number"
  ) {
    throw new ApiClientError(
      "Incomplete simulation payload: required fields (event, impact, stockout, intervention, execution_time_ms) are missing.",
      "INVALID_RESPONSE"
    );
  }

  const rawTimeline = Array.isArray(candidate.depletion_timeline)
    ? candidate.depletion_timeline
    : [];

  if (rawTimeline.length === 0) {
    throw new ApiClientError(
      "Simulation returned an empty depletion_timeline array.",
      "INVALID_RESPONSE"
    );
  }

  const normalizedTimeline: HourlyStockPoint[] = rawTimeline
    .filter(
      (pt): pt is HourlyStockPoint =>
        pt !== null &&
        typeof pt === "object" &&
        typeof pt.hour === "number" &&
        typeof pt.stock_units === "number"
    )
    .map((pt) => ({
      hour: pt.hour,
      stock_units: pt.stock_units,
      supply_blocked: Boolean(pt.supply_blocked),
    }));

  if (normalizedTimeline.length === 0) {
    throw new ApiClientError(
      "Simulation depletion_timeline contained no valid numeric points.",
      "INVALID_RESPONSE"
    );
  }

  return {
    status: candidate.status ?? "success",
    event: candidate.event,
    impact: {
      disrupted_supplier: candidate.impact.disrupted_supplier ?? "",
      affected_parts: Array.isArray(candidate.impact.affected_parts)
        ? candidate.impact.affected_parts
        : [],
      affected_products: Array.isArray(candidate.impact.affected_products)
        ? candidate.impact.affected_products
        : [],
      affected_orders: Array.isArray(candidate.impact.affected_orders)
        ? candidate.impact.affected_orders
        : [],
      total_affected_nodes: Number(candidate.impact.total_affected_nodes ?? 0),
    },
    depletion_timeline: normalizedTimeline,
    stockout: {
      part_id: candidate.stockout.part_id ?? "UNKNOWN",
      stockout_hour:
        typeof candidate.stockout.stockout_hour === "number"
          ? candidate.stockout.stockout_hour
          : null,
      no_stockout: Boolean(candidate.stockout.no_stockout),
      breached_orders: Array.isArray(candidate.stockout.breached_orders)
        ? candidate.stockout.breached_orders
        : [],
      total_breached: Number(candidate.stockout.total_breached ?? 0),
    },
    intervention: {
      stockout_hour:
        typeof candidate.intervention.stockout_hour === "number"
          ? candidate.intervention.stockout_hour
          : null,
      current_hour: Number(candidate.intervention.current_hour ?? 0),
      recovery_lead_time_hours: Number(
        candidate.intervention.recovery_lead_time_hours ?? 0
      ),
      delta_t_hours:
        typeof candidate.intervention.delta_t_hours === "number"
          ? candidate.intervention.delta_t_hours
          : null,
      is_feasible: Boolean(candidate.intervention.is_feasible),
      status: candidate.intervention.status ?? "BREACHED",
      affected_order_ids: Array.isArray(candidate.intervention.affected_order_ids)
        ? candidate.intervention.affected_order_ids
        : [],
      message: candidate.intervention.message ?? "",
    },
    critical_part: candidate.critical_part ?? null,
    execution_time_ms: candidate.execution_time_ms,
  };
}

export const simulationApi = {
  async runDisruptionSimulation(payload: DisruptionRequest): Promise<SimulationResponse> {
    try {
      const response = await axiosInstance.post<unknown>(
        "/api/v1/simulation/disrupt",
        payload
      );
      return assertValidSimulationPayload(response.data);
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  async runBenchmarkSimulation(): Promise<SimulationResponse> {
    try {
      const response = await axiosInstance.get<unknown>("/api/v1/simulation/benchmark");
      return assertValidSimulationPayload(response.data);
    } catch (error) {
      throw extractErrorMessage(error);
    }
  },

  deriveOrderImpacts(
    simulation: SimulationResponse | null,
    graphNodes: GraphNode[]
  ): DerivedOrderImpact[] {
    if (!simulation) {
      return [];
    }

    const orderMetaMap = new Map<string, GraphNode>();
    for (const node of graphNodes) {
      if (node.kind === "order" || node.tier === "order" || node.id.startsWith("ORD-")) {
        orderMetaMap.set(node.id, node);
      }
    }

    const breachedMap = new Map(
      simulation.stockout.breached_orders.map((b) => [b.order_id, b])
    );

    const orderedIds = Array.from(
      new Set([
        ...simulation.stockout.breached_orders.map((b) => b.order_id),
        ...simulation.impact.affected_orders,
      ])
    );

    return orderedIds.map((orderId) => {
      const meta = orderMetaMap.get(orderId);
      const breached = breachedMap.get(orderId);
      const deadline =
        breached?.delivery_deadline_hours ??
        (typeof meta?.delivery_deadline_hours === "number"
          ? meta.delivery_deadline_hours
          : null);

      if (breached && breached.will_fail) {
        return {
          order_id: orderId,
          customer: meta?.customer,
          product_id: meta?.product_id,
          quantity: meta?.quantity,
          delivery_deadline_hours: deadline,
          category: "FAILED",
          reason: breached.reason,
        };
      }

      if (deadline !== null && simulation.stockout.stockout_hour !== null) {
        const recoveryComplete =
          simulation.stockout.stockout_hour +
          simulation.intervention.recovery_lead_time_hours;
        return {
          order_id: orderId,
          customer: meta?.customer,
          product_id: meta?.product_id,
          quantity: meta?.quantity,
          delivery_deadline_hours: deadline,
          category: "SAFE",
          reason: `Deadline at hour ${deadline.toFixed(1)} clears recovery at hour ${recoveryComplete.toFixed(1)}.`,
        };
      }

      if (simulation.stockout.no_stockout) {
        return {
          order_id: orderId,
          customer: meta?.customer,
          product_id: meta?.product_id,
          quantity: meta?.quantity,
          delivery_deadline_hours: deadline,
          category: "SAFE",
          reason: "No stockout predicted within the 72-hour horizon.",
        };
      }

      return {
        order_id: orderId,
        customer: meta?.customer,
        product_id: meta?.product_id,
        quantity: meta?.quantity,
        delivery_deadline_hours: deadline,
        category: "UNKNOWN",
        reason: "Delivery deadline metadata unavailable for order verification.",
      };
    });
  },
};

