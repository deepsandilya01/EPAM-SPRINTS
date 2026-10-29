import {
  EntityType,
  RelationType,
  Supplier,
  BOMPart,
  FinishedProduct,
  CustomerOrder,
  GraphNodeData,
  GraphEdgeData,
  ScenarioGraph,
} from './index'

export interface GraphGenerationParams {
  supplierCount: number
  partCount: number
  productCount: number
  orderCount: number
}

export interface GraphInputErrors {
  supplierCount?: string
  partCount?: string
  productCount?: string
  orderCount?: string
}

export interface HoverPathInfo {
  hoveredNodeId: string | null
  upstreamNodeIds: string[]
  downstreamNodeIds: string[]
  connectedNodeIds: string[]
  connectedEdgeIds: string[]
  directUpstreamCount: number
  directDownstreamCount: number
  totalUpstreamCount: number
  totalDownstreamCount: number
}

export interface NodeHoverTooltipData {
  nodeId: string
  label: string
  type: EntityType
  directUpstream: number
  directDownstream: number
  totalUpstream: number
  totalDownstream: number
  x: number
  y: number
}

export const GRAPH_LIMITS = {
  MIN_COUNT: 1,
  MAX_SUPPLIERS: 20,
  MAX_PARTS: 50,
  MAX_PRODUCTS: 20,
  MAX_ORDERS: 100,
} as const

export const DEFAULT_GRAPH_PARAMS: GraphGenerationParams = {
  supplierCount: 2,
  partCount: 5,
  productCount: 2,
  orderCount: 10,
}
