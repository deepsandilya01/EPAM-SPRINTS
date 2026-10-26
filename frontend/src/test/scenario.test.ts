import { describe, it, expect } from 'vitest'
import {
  CANONICAL_SUPPLIERS,
  CANONICAL_PARTS,
  CANONICAL_PRODUCTS,
  CANONICAL_ORDERS,
  CANONICAL_EDGES,
} from '@/mocks/scenario'
import { INITIAL_SCENARIO_GRAPH } from '@/mocks/graph'

describe('Scenario Specification Verification', () => {
  it('has exact canonical entity counts matching specification', () => {
    expect(CANONICAL_SUPPLIERS.length).toBe(2)
    expect(CANONICAL_PARTS.length).toBe(5)
    expect(CANONICAL_PRODUCTS.length).toBe(2)
    expect(CANONICAL_ORDERS.length).toBe(10)
    expect(INITIAL_SCENARIO_GRAPH.nodes.length).toBe(19)
  })

  it('has exact canonical edge count and relationship breakdowns', () => {
    expect(CANONICAL_EDGES.length).toBe(21)

    const suppliesEdges = CANONICAL_EDGES.filter((e) => e.relation === 'SUPPLIES')
    const usedInEdges = CANONICAL_EDGES.filter((e) => e.relation === 'USED_IN')
    const fulfillsEdges = CANONICAL_EDGES.filter((e) => e.relation === 'FULFILLS')

    expect(suppliesEdges.length).toBe(6)
    expect(usedInEdges.length).toBe(5)
    expect(fulfillsEdges.length).toBe(10)
  })

  it('preserves correct direction of each edge type', () => {
    const suppliers = new Set(CANONICAL_SUPPLIERS.map((s) => s.id))
    const parts = new Set(CANONICAL_PARTS.map((p) => p.id))
    const products = new Set(CANONICAL_PRODUCTS.map((p) => p.id))
    const orders = new Set(CANONICAL_ORDERS.map((o) => o.id))

    for (const edge of CANONICAL_EDGES) {
      if (edge.relation === 'SUPPLIES') {
        expect(suppliers.has(edge.source)).toBe(true)
        expect(parts.has(edge.target)).toBe(true)
      } else if (edge.relation === 'USED_IN') {
        expect(parts.has(edge.source)).toBe(true)
        expect(products.has(edge.target)).toBe(true)
      } else if (edge.relation === 'FULFILLS') {
        expect(products.has(edge.source)).toBe(true)
        expect(orders.has(edge.target)).toBe(true)
      }
    }
  })
})
