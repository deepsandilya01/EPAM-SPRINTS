import {
  ScenarioGraph,
  GraphNodeData,
} from '@/types'
import {
  CANONICAL_SUPPLIERS,
  CANONICAL_PARTS,
  CANONICAL_PRODUCTS,
  CANONICAL_ORDERS,
  CANONICAL_EDGES,
} from './scenario'

export const COLUMN_X_POSITIONS = {
  1: 60,   // Suppliers
  2: 280,  // BOM Parts
  3: 540,  // Finished Products
  4: 800,  // Customer Orders
}

export const NODE_LAYOUT_COORDINATES: Record<string, { x: number; y: number }> = {
  // Column 1: Suppliers
  'SUP-01': { x: 60, y: 220 },
  'SUP-02': { x: 60, y: 340 },

  // Column 2: BOM Parts
  'PART-01': { x: 280, y: 110 },
  'PART-02': { x: 280, y: 180 },
  'PART-03': { x: 280, y: 250 },
  'PART-04': { x: 280, y: 320 },
  'PART-05': { x: 280, y: 390 },

  // Column 3: Finished Products
  'PROD-01': { x: 540, y: 230 },
  'PROD-02': { x: 540, y: 340 },

  // Column 4: Customer Orders
  'ORD-01': { x: 800, y: 80 },
  'ORD-02': { x: 800, y: 120 },
  'ORD-03': { x: 800, y: 160 },
  'ORD-04': { x: 800, y: 200 },
  'ORD-05': { x: 800, y: 240 },
  'ORD-06': { x: 800, y: 280 },
  'ORD-07': { x: 800, y: 320 },
  'ORD-08': { x: 800, y: 360 },
  'ORD-09': { x: 800, y: 400 },
  'ORD-10': { x: 800, y: 440 },
}

export function buildInitialScenarioGraph(): ScenarioGraph {
  const nodes: GraphNodeData[] = [
    // Suppliers (Column 1)
    ...CANONICAL_SUPPLIERS.map((s) => ({
      id: s.id,
      label: s.id,
      type: 'SUPPLIER' as const,
      isAffected: s.id === 'SUP-01',
      isSource: s.id === 'SUP-01',
      details: s,
      column: 1,
    })),

    // BOM Parts (Column 2)
    ...CANONICAL_PARTS.map((p) => ({
      id: p.id,
      label: p.id,
      type: 'BOM_PART' as const,
      isAffected: ['PART-01', 'PART-02', 'PART-05'].includes(p.id),
      isSource: false,
      details: p,
      column: 2,
    })),

    // Finished Products (Column 3)
    ...CANONICAL_PRODUCTS.map((prod) => ({
      id: prod.id,
      label: prod.id,
      type: 'FINISHED_PRODUCT' as const,
      isAffected: prod.id === 'PROD-01',
      isSource: false,
      details: prod,
      column: 3,
    })),

    // Customer Orders (Column 4)
    ...CANONICAL_ORDERS.map((ord) => ({
      id: ord.id,
      label: ord.id,
      type: 'CUSTOMER_ORDER' as const,
      isAffected: ['ORD-01', 'ORD-02', 'ORD-03', 'ORD-04', 'ORD-05', 'ORD-06'].includes(ord.id),
      isSource: false,
      details: ord,
      column: 4,
    })),
  ]

  return {
    suppliers: CANONICAL_SUPPLIERS,
    parts: CANONICAL_PARTS,
    products: CANONICAL_PRODUCTS,
    orders: CANONICAL_ORDERS,
    nodes,
    edges: CANONICAL_EDGES,
  }
}

export const INITIAL_SCENARIO_GRAPH = buildInitialScenarioGraph()
