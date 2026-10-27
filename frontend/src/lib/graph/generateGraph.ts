import {
  Supplier,
  BOMPart,
  FinishedProduct,
  CustomerOrder,
  GraphNodeData,
  GraphEdgeData,
  ScenarioGraph,
} from '@/types'
import { GraphGenerationParams, DEFAULT_GRAPH_PARAMS } from '@/types/graph.types'
import {
  CANONICAL_SUPPLIERS,
  CANONICAL_PARTS,
  CANONICAL_PRODUCTS,
  CANONICAL_ORDERS,
  CANONICAL_EDGES,
} from '@/mocks/scenario'

const LOCATIONS = ['USA', 'Germany', 'Japan', 'South Korea', 'Taiwan', 'Canada', 'Mexico', 'UK']
const SUPPLIER_TYPES = ['Raw Material Supplier', 'Component Fabricator', 'Semiconductor Foundry', 'Precision Assembly']
const PART_NAMES = [
  'Microcontroller Core', 'Sensor Array Module', 'Power Management IC',
  'Communication Antenna', 'Enclosure Chassis', 'Flash Memory Module',
  'Voltage Regulator', 'Optocoupler Unit', 'Oscillator Crystal',
  'Bus Transceiver', 'Capacitor Bank', 'Thermal Heat Sink',
  'Connector Interface', 'Display Driver', 'Battery Cell Pack'
]
const PART_CATEGORIES = ['Semiconductor', 'Optoelectronics', 'Power Electronics', 'RF Components', 'Mechanical Housing', 'Passive Components']
const PRODUCT_NAMES = [
  'Industrial IoT Gateway', 'Smart Edge Sensor Node', 'Automated Telemetry Controller',
  'Embedded Fleet Tracker', 'High-Precision Mesh Router', 'Secure Data Concentrator'
]
const CUSTOMER_NAMES = [
  'Acme Corporation', 'Global Logistics Inc', 'Apex Manufacturing',
  'Quantum Systems', 'Helios Energy', 'Pacific Automation',
  'Vanguard Defense', 'Nordic Instruments', 'Horizon Robotics',
  'Cybernet Dynamics', 'Starlight Avionics', 'Nexus Robotics'
]
const PRIORITIES: ('Standard' | 'High' | 'Urgent')[] = ['Standard', 'High', 'Urgent']
const STATUSES: ('Pending' | 'In Production' | 'Delayed' | 'Shipped')[] = ['Pending', 'In Production', 'Delayed', 'Shipped']

export function formatEntityId(prefix: string, index: number): string {
  const numStr = index < 10 ? `0${index}` : `${index}`
  return `${prefix}-${numStr}`
}

export function generateSupplyChainGraph(params: GraphGenerationParams): ScenarioGraph {
  const { supplierCount, partCount, productCount, orderCount } = params

  // Return canonical dataset for default scenario (2, 5, 2, 10) to preserve reference oracle
  const isDefault =
    supplierCount === DEFAULT_GRAPH_PARAMS.supplierCount &&
    partCount === DEFAULT_GRAPH_PARAMS.partCount &&
    productCount === DEFAULT_GRAPH_PARAMS.productCount &&
    orderCount === DEFAULT_GRAPH_PARAMS.orderCount

  if (isDefault) {
    const nodes: GraphNodeData[] = [
      ...CANONICAL_SUPPLIERS.map((s) => ({
        id: s.id,
        label: s.id,
        type: 'SUPPLIER' as const,
        isAffected: s.id === 'SUP-01',
        isSource: s.id === 'SUP-01',
        details: s,
        column: 1,
      })),
      ...CANONICAL_PARTS.map((p) => ({
        id: p.id,
        label: p.id,
        type: 'BOM_PART' as const,
        isAffected: ['PART-01', 'PART-02', 'PART-05'].includes(p.id),
        isSource: false,
        details: p,
        column: 2,
      })),
      ...CANONICAL_PRODUCTS.map((prod) => ({
        id: prod.id,
        label: prod.id,
        type: 'FINISHED_PRODUCT' as const,
        isAffected: prod.id === 'PROD-01',
        isSource: false,
        details: prod,
        column: 3,
      })),
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

  const suppliers: Supplier[] = Array.from({ length: supplierCount }, (_, i) => {
    const id = formatEntityId('SUP', i + 1)
    return {
      id,
      name: i === 0 ? 'Supplier 01 (Primary)' : `Supplier ${i + 1}`,
      location: LOCATIONS[i % LOCATIONS.length],
      type: SUPPLIER_TYPES[i % SUPPLIER_TYPES.length],
      note: i === 0 ? 'Primary strategic supplier' : `Tier-1 partner ${i + 1}`,
      reliabilityScore: Number((92 + ((i * 3.7) % 7.5)).toFixed(1)),
      contactEmail: `ops@${id.toLowerCase()}.supply.io`,
    }
  })

  const parts: BOMPart[] = Array.from({ length: partCount }, (_, i) => {
    const id = formatEntityId('PART', i + 1)
    return {
      id,
      name: PART_NAMES[i % PART_NAMES.length] + (i >= PART_NAMES.length ? ` v${Math.floor(i / PART_NAMES.length) + 1}` : ''),
      category: PART_CATEGORIES[i % PART_CATEGORIES.length],
      stockLevel: 500 + ((i * 320) % 3500),
      unitCost: Number((5.5 + ((i * 7.8) % 45)).toFixed(2)),
      leadTimeDays: 5 + ((i * 3) % 25),
      criticality: i % 3 === 0 ? 'High' : (i % 3 === 1 ? 'Medium' : 'Low'),
    }
  })

  const products: FinishedProduct[] = Array.from({ length: productCount }, (_, i) => {
    const id = formatEntityId('PROD', i + 1)
    return {
      id,
      name: PRODUCT_NAMES[i % PRODUCT_NAMES.length] + (i >= PRODUCT_NAMES.length ? ` Type-${i + 1}` : ''),
      sku: `SKU-${1000 + i * 50}`,
      currentInventory: 100 + ((i * 85) % 500),
      productionLine: `Line ${String.fromCharCode(65 + (i % 6))}`,
      dailyTarget: 40 + ((i * 15) % 60),
    }
  })

  const orders: CustomerOrder[] = Array.from({ length: orderCount }, (_, i) => {
    const id = formatEntityId('ORD', i + 1)
    const day = 1 + (i % 28)
    const dayStr = day < 10 ? `0${day}` : `${day}`
    return {
      id,
      customerName: CUSTOMER_NAMES[i % CUSTOMER_NAMES.length],
      orderDate: `2025-01-${dayStr}`,
      deliveryDeadline: `2025-02-${dayStr}`,
      quantity: 25 + ((i * 15) % 150),
      status: STATUSES[i % STATUSES.length],
      priority: PRIORITIES[i % PRIORITIES.length],
    }
  })

  const edges: GraphEdgeData[] = []
  const edgeKeys = new Set<string>()

  const addEdge = (source: string, target: string, relation: 'SUPPLIES' | 'USED_IN' | 'FULFILLS') => {
    const key = `${source}->${target}`
    if (edgeKeys.has(key)) return
    edgeKeys.add(key)
    edges.push({
      id: `e-${source}-${target}`,
      source,
      target,
      relation,
      isAffected: false,
    })
  }

  // Tier 1: Suppliers -> BOM Parts (SUPPLIES)
  parts.forEach((part, idx) => {
    const primarySup = suppliers[idx % supplierCount]
    addEdge(primarySup.id, part.id, 'SUPPLIES')

    // Multi-source alternating parts when multiple suppliers are configured
    if (supplierCount > 1 && idx % 2 === 1) {
      const secondarySup = suppliers[(idx + 1) % supplierCount]
      addEdge(secondarySup.id, part.id, 'SUPPLIES')
    }
  })

  // Prevent orphaned suppliers with zero outgoing edges
  suppliers.forEach((sup, idx) => {
    if (!edges.some((e) => e.source === sup.id)) {
      const targetPart = parts[idx % partCount]
      addEdge(sup.id, targetPart.id, 'SUPPLIES')
    }
  })

  // Tier 2: BOM Parts -> Finished Products (USED_IN)
  parts.forEach((part, idx) => {
    const primaryProd = products[idx % productCount]
    addEdge(part.id, primaryProd.id, 'USED_IN')

    if (productCount > 1 && idx % 3 === 0) {
      const secondaryProd = products[(idx + 1) % productCount]
      addEdge(part.id, secondaryProd.id, 'USED_IN')
    }
  })

  // Prevent orphaned products without component parts
  products.forEach((prod, idx) => {
    if (!edges.some((e) => e.target === prod.id)) {
      const sourcePart = parts[idx % partCount]
      addEdge(sourcePart.id, prod.id, 'USED_IN')
    }
  })

  // Tier 3: Finished Products -> Customer Orders (FULFILLS)
  orders.forEach((order, idx) => {
    const fulfillingProd = products[idx % productCount]
    addEdge(fulfillingProd.id, order.id, 'FULFILLS')
  })
  const nodes: GraphNodeData[] = [
    ...suppliers.map((s, idx) => ({
      id: s.id,
      label: s.id,
      type: 'SUPPLIER' as const,
      isAffected: idx === 0,
      isSource: idx === 0,
      details: s,
      column: 1,
    })),
    ...parts.map((p) => ({
      id: p.id,
      label: p.id,
      type: 'BOM_PART' as const,
      isAffected: false,
      isSource: false,
      details: p,
      column: 2,
    })),
    ...products.map((prod) => ({
      id: prod.id,
      label: prod.id,
      type: 'FINISHED_PRODUCT' as const,
      isAffected: false,
      isSource: false,
      details: prod,
      column: 3,
    })),
    ...orders.map((ord) => ({
      id: ord.id,
      label: ord.id,
      type: 'CUSTOMER_ORDER' as const,
      isAffected: false,
      isSource: false,
      details: ord,
      column: 4,
    })),
  ]

  return {
    suppliers,
    parts,
    products,
    orders,
    nodes,
    edges,
  }
}
