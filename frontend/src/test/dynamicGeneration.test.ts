import { describe, it, expect } from 'vitest'
import { generateSupplyChainGraph } from '@/lib/graph/generateGraph'
import { traverseGraph } from '@/lib/graph/traverseGraph'
import { validateGeneratedGraph } from '@/lib/graph/validateGraph'

describe('Dynamic Supply Chain Graph Generation Tests', () => {
  it('generates exact canonical graph for (2, 5, 2, 10)', () => {
    const graph = generateSupplyChainGraph({
      supplierCount: 2,
      partCount: 5,
      productCount: 2,
      orderCount: 10,
    })

    expect(graph.suppliers.length).toBe(2)
    expect(graph.parts.length).toBe(5)
    expect(graph.products.length).toBe(2)
    expect(graph.orders.length).toBe(10)
    expect(graph.nodes.length).toBe(19)
    expect(graph.edges.length).toBe(21)

    const validation = validateGeneratedGraph(graph)
    expect(validation.isValid).toBe(true)

    // SUP-01 reachability
    const traversal01 = traverseGraph(graph, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'all',
    })
    expect(traversal01.totalEntitiesReached).toBe(10)
    expect(traversal01.reachableOrders.length).toBe(6)
  })

  it('generates scaled graph for (5, 12, 4, 30)', () => {
    const graph = generateSupplyChainGraph({
      supplierCount: 5,
      partCount: 12,
      productCount: 4,
      orderCount: 30,
    })

    expect(graph.suppliers.length).toBe(5)
    expect(graph.parts.length).toBe(12)
    expect(graph.products.length).toBe(4)
    expect(graph.orders.length).toBe(30)
    expect(graph.nodes.length).toBe(51) // 5 + 12 + 4 + 30 = 51

    // Verify all IDs are unique
    const nodeIds = new Set(graph.nodes.map((n) => n.id))
    expect(nodeIds.size).toBe(51)

    const validation = validateGeneratedGraph(graph)
    expect(validation.isValid).toBe(true)

    // Traversal from SUP-01
    const traversal = traverseGraph(graph, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'all',
    })
    expect(traversal.reachableParts.length).toBeGreaterThan(0)
    expect(traversal.reachableProducts.length).toBeGreaterThan(0)
    expect(traversal.reachableOrders.length).toBeGreaterThan(0)
    // No duplicates in traversal results
    const uniqueReached = new Set(traversal.allReachedNodeIds)
    expect(uniqueReached.size).toBe(traversal.allReachedNodeIds.length)
  })

  it('generates minimal graph for (1, 1, 1, 1)', () => {
    const graph = generateSupplyChainGraph({
      supplierCount: 1,
      partCount: 1,
      productCount: 1,
      orderCount: 1,
    })

    expect(graph.suppliers.length).toBe(1)
    expect(graph.parts.length).toBe(1)
    expect(graph.products.length).toBe(1)
    expect(graph.orders.length).toBe(1)
    expect(graph.nodes.length).toBe(4)
    expect(graph.edges.length).toBe(3) // 1 SUPPLIES + 1 USED_IN + 1 FULFILLS

    const validation = validateGeneratedGraph(graph)
    expect(validation.isValid).toBe(true)

    const traversal = traverseGraph(graph, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'all',
    })
    expect(traversal.totalEntitiesReached).toBe(3)
    expect(traversal.reachableParts).toEqual(['PART-01'])
    expect(traversal.reachableProducts).toEqual(['PROD-01'])
    expect(traversal.reachableOrders).toEqual(['ORD-01'])
  })

  it('repeated generation with same inputs produces identical deterministic results', () => {
    const params = { supplierCount: 3, partCount: 7, productCount: 3, orderCount: 15 }
    const graphA = generateSupplyChainGraph(params)
    const graphB = generateSupplyChainGraph(params)

    expect(graphA.nodes.length).toBe(graphB.nodes.length)
    expect(graphA.edges.length).toBe(graphB.edges.length)
    expect(graphA.edges.map((e) => e.id)).toEqual(graphB.edges.map((e) => e.id))
  })
})
