import { describe, it, expect } from 'vitest'
import { performGraphTraversal } from '@/services/traversal.service'
import { INITIAL_SCENARIO_GRAPH } from '@/mocks/graph'

describe('Graph Traversal Engine Verification', () => {
  it('correctly computes reachability for SUP-01', () => {
    const result = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'all',
    })

    // Expected oracle for SUP-01
    expect(result.sourceNodeId).toBe('SUP-01')
    expect(result.reachableParts).toEqual(expect.arrayContaining(['PART-01', 'PART-02', 'PART-05']))
    expect(result.reachableParts.length).toBe(3)

    expect(result.reachableProducts).toEqual(['PROD-01'])
    expect(result.reachableProducts.length).toBe(1)

    expect(result.reachableOrders).toEqual(
      expect.arrayContaining(['ORD-01', 'ORD-02', 'ORD-03', 'ORD-04', 'ORD-05', 'ORD-06'])
    )
    expect(result.reachableOrders.length).toBe(6)

    // Total reached entities = 3 parts + 1 product + 6 orders = 10
    expect(result.totalEntitiesReached).toBe(10)
    expect(result.visitedNodesCount).toBe(10)
  })

  it('correctly computes reachability for SUP-02', () => {
    const result = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-02',
      direction: 'downstream',
      depth: 'all',
    })

    // Expected oracle for SUP-02
    expect(result.sourceNodeId).toBe('SUP-02')
    expect(result.reachableParts).toEqual(expect.arrayContaining(['PART-03', 'PART-04', 'PART-05']))
    expect(result.reachableParts.length).toBe(3)

    expect(result.reachableProducts).toEqual(expect.arrayContaining(['PROD-01', 'PROD-02']))
    expect(result.reachableProducts.length).toBe(2)

    expect(result.reachableOrders.length).toBe(10)
    expect(result.totalEntitiesReached).toBe(15) // 3 parts + 2 products + 10 orders
  })

  it('contains zero duplicate entities in traversal results', () => {
    const result = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-02',
      direction: 'downstream',
      depth: 'all',
    })

    const uniqueIds = new Set(result.allReachedNodeIds)
    expect(uniqueIds.size).toBe(result.allReachedNodeIds.length)
  })

  it('respects highlight depth parameter constraints', () => {
    // Level 1: direct parts only
    const directResult = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'direct',
    })
    expect(directResult.reachableParts.length).toBe(3)
    expect(directResult.reachableProducts.length).toBe(0)
    expect(directResult.reachableOrders.length).toBe(0)

    // Level 2: parts + products
    const partsProdResult = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'parts_products',
    })
    expect(partsProdResult.reachableParts.length).toBe(3)
    expect(partsProdResult.reachableProducts.length).toBe(1)
    expect(partsProdResult.reachableOrders.length).toBe(0)
  })

  it('handles upstream traversal correctly from Customer Order', () => {
    const upstreamResult = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'ORD-01',
      direction: 'upstream',
      depth: 'all',
    })

    expect(upstreamResult.reachableProducts).toContain('PROD-01')
    expect(upstreamResult.reachableParts).toEqual(expect.arrayContaining(['PART-01', 'PART-02', 'PART-05']))
    expect(upstreamResult.reachableSuppliers).toEqual(expect.arrayContaining(['SUP-01', 'SUP-02']))
  })

  it('gracefully handles unknown supplier node ID', () => {
    const unknownResult = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-999',
      direction: 'downstream',
      depth: 'all',
    })

    expect(unknownResult.totalEntitiesReached).toBe(0)
    expect(unknownResult.reachableParts.length).toBe(0)
    expect(unknownResult.reachableProducts.length).toBe(0)
    expect(unknownResult.reachableOrders.length).toBe(0)
  })
})
