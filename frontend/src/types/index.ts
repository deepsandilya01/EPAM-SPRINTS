// Entity Types
export type EntityType = 'SUPPLIER' | 'BOM_PART' | 'FINISHED_PRODUCT' | 'CUSTOMER_ORDER'

export type RelationType = 'SUPPLIES' | 'USED_IN' | 'FULFILLS'

export type TraceDirection = 'downstream' | 'upstream'

export type HighlightDepth = 'all' | 'direct' | 'parts_products' | 'custom'

// Domain Entities
export interface Supplier {
  id: string
  name: string
  location: string
  type: string
  note: string
  reliabilityScore?: number
  contactEmail?: string
}

export interface BOMPart {
  id: string
  name: string
  category: string
  stockLevel: number
  unitCost: number
  leadTimeDays: number
  criticality: 'High' | 'Medium' | 'Low'
}

export interface FinishedProduct {
  id: string
  name: string
  sku: string
  currentInventory: number
  productionLine: string
  dailyTarget: number
}

export interface CustomerOrder {
  id: string
  customerName: string
  orderDate: string
  deliveryDeadline: string
  quantity: number
  status: 'Pending' | 'In Production' | 'Delayed' | 'Shipped'
  priority: 'High' | 'Standard' | 'Urgent'
}

export type EntityDetails =
  | { type: 'SUPPLIER'; data: Supplier }
  | { type: 'BOM_PART'; data: BOMPart }
  | { type: 'FINISHED_PRODUCT'; data: FinishedProduct }
  | { type: 'CUSTOMER_ORDER'; data: CustomerOrder }

// Graph Types
export interface GraphNodeData {
  id: string
  label: string
  type: EntityType
  isAffected: boolean
  isSource: boolean
  details: Supplier | BOMPart | FinishedProduct | CustomerOrder
  column: number // 1: Suppliers, 2: BOM Parts, 3: Products, 4: Customer Orders
}

export interface GraphEdgeData {
  id: string
  source: string
  target: string
  relation: RelationType
  isAffected: boolean
}

export interface ScenarioGraph {
  suppliers: Supplier[]
  parts: BOMPart[]
  products: FinishedProduct[]
  orders: CustomerOrder[]
  nodes: GraphNodeData[]
  edges: GraphEdgeData[]
}

// Traversal Types
export interface TraversalRequest {
  sourceNodeId: string
  direction: TraceDirection
  depth?: HighlightDepth
  nodeFilters?: EntityType[]
  showUnaffected?: boolean
}

export interface TraversalStep {
  step: number
  fromNode: string
  toNode: string
  relation: RelationType
  traversalTimeMs: number
  cumulativeTimeMs: number
}

export interface TraversalResult {
  sourceNodeId: string
  direction: TraceDirection
  totalEntitiesReached: number
  reachableSuppliers: string[]
  reachableParts: string[]
  reachableProducts: string[]
  reachableOrders: string[]
  allReachedNodeIds: string[]
  traversedEdgeIds: string[]
  visitedNodesCount: number
  traversedEdgesCount: number
  executionTimeMs: number
  algorithm: 'BFS' | 'DFS'
  complexity: string
  spaceComplexity: string
  examplePath: TraversalStep[]
}

// Validation & Benchmark
export interface ValidationFinding {
  id: string
  severity: 'error' | 'warning' | 'info'
  category: 'orphaned_node' | 'cycle_detection' | 'missing_endpoint' | 'duplicate_id' | 'schema_mismatch'
  message: string
  affectedEntities: string[]
}

export interface ValidationResult {
  isValid: boolean
  totalChecks: number
  passedChecks: number
  findings: ValidationFinding[]
}

export interface BenchmarkMetrics {
  algorithm: 'BFS' | 'DFS'
  nodeCount: number
  edgeCount: number
  averageDurationMs: number
  p95DurationMs: number
  p99DurationMs: number
  memoryUsageKb: number
  iterations: number
}

export interface BenchmarkResult {
  bfsMetrics: BenchmarkMetrics
  dfsMetrics: BenchmarkMetrics
  timestamp: string
}
