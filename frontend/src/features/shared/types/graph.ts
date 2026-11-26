export type NodeTier = "supplier" | "part" | "product" | "order";

export interface GraphNode {
  id: string;
  tier: NodeTier | string;
  kind: NodeTier | string;
  name?: string;
  label?: string;
  recovery_lead_time_hours?: number;
  location?: string;
  note?: string;
  stock_on_hand?: number;
  daily_consumption?: number;
  days_of_supply?: number;
  initial_stock_units?: number;
  hourly_consumption_units?: number;
  parts_needed?: string;
  customer?: string;
  product_id?: string;
  quantity?: number;
  deadline?: string;
  delivery_deadline_hours?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation?: string;
  relationship_type?: string;
  lead_time_hours?: number;
  max_capacity_units_per_day?: number;
  quantity_per_unit?: number;
  quantity_per_product?: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  links?: GraphEdge[];
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  node_count: number;
  edge_count: number;
}

export interface DownstreamResponse {
  root: string;
  node_id: string;
  downstream: string[];
  count: number;
}

export interface GraphMutationResponse {
  status?: string;
  deleted?: string[];
  deleted_node_id?: string;
  edges_removed?: number;
  elapsed_ms?: number;
  graph?: GraphResponse;
  node_count?: number;
  edge_count?: number;
}

