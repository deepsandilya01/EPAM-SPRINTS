export type DisruptionType = "SUPPLIER_DELAY" | "CAPACITY_DROP" | "FORCE_MAJEURE";

export type InterventionStatus = "FEASIBLE" | "CRITICAL" | "BREACHED";

export interface DisruptionRequest {
  supplier_id: string;
  disruption_type: DisruptionType;
  delay_duration_hours: number;
  description?: string;
}

export interface DisruptionEventData {
  event_id: string;
  supplier_id: string;
  disruption_type: DisruptionType | string;
  delay_duration_hours: number;
  created_at: string;
  description: string;
}

export interface RippleImpactSummary {
  disrupted_supplier: string;
  affected_parts: string[];
  affected_products: string[];
  affected_orders: string[];
  total_affected_nodes: number;
}

export interface HourlyStockPoint {
  hour: number;
  stock_units: number;
  supply_blocked: boolean;
}

export interface BreachedOrder {
  order_id: string;
  delivery_deadline_hours: number;
  will_fail: boolean;
  reason: string;
}

export interface StockoutPredictionResult {
  part_id: string;
  stockout_hour: number | null;
  no_stockout: boolean;
  breached_orders: BreachedOrder[];
  total_breached: number;
}

export interface InterventionWindowResult {
  stockout_hour: number | null;
  current_hour: number;
  recovery_lead_time_hours: number;
  delta_t_hours: number | null;
  is_feasible: boolean;
  status: InterventionStatus | string;
  affected_order_ids: string[];
  message: string;
}

export interface CriticalPartMetadata {
  part_id: string;
  initial_stock: number;
  hourly_consumption: number;
}

export interface SimulationResponse {
  status: string;
  event: DisruptionEventData;
  impact: RippleImpactSummary;
  depletion_timeline: HourlyStockPoint[];
  stockout: StockoutPredictionResult;
  intervention: InterventionWindowResult;
  critical_part: CriticalPartMetadata | null;
  execution_time_ms: number;
}

export type OrderImpactCategory = "FAILED" | "SAFE" | "UNKNOWN";

export interface DerivedOrderImpact {
  order_id: string;
  customer?: string;
  product_id?: string;
  quantity?: number;
  delivery_deadline_hours: number | null;
  category: OrderImpactCategory;
  reason: string;
}

