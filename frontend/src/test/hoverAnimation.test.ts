import { describe, it, expect } from 'vitest'
import { generateSupplyChainGraph } from '@/lib/graph/generateGraph'
import { getConnectedSupplyChainPaths } from '@/lib/graph/traverseGraph'

describe('Interactive Hover Supply Chain Path Highlighting Tests', () => {
  const graph = generateSupplyChainGraph({
    supplierCount: 2,
    partCount: 5,
    productCount: 2,
    orderCount: 10,
  })

  it('hover on Supplier: highlights downstream path only, upstream is empty', () => {
    const hover01 = getConnectedSupplyChainPaths(graph, 'SUP-01')

    expect(hover01.hoveredNodeId).toBe('SUP-01')
    expect(hover01.directUpstreamCount).toBe(0)
    expect(hover01.totalUpstreamCount).toBe(0)
    expect(hover01.upstreamNodeIds).toEqual([])

    // Downstream path connects to PART-01, PART-02, PART-05, PROD-01, and ORD-01..06
    expect(hover01.directDownstreamCount).toBe(3)
    expect(hover01.downstreamNodeIds).toContain('PART-01')
    expect(hover01.downstreamNodeIds).toContain('PART-02')
    expect(hover01.downstreamNodeIds).toContain('PART-05')
    expect(hover01.downstreamNodeIds).toContain('PROD-01')
    expect(hover01.downstreamNodeIds).toContain('ORD-01')

    // SUP-02 and PART-03, PART-04 are NOT connected to SUP-01!
    expect(hover01.connectedNodeIds).not.toContain('SUP-02')
    expect(hover01.connectedNodeIds).not.toContain('PART-03')
    expect(hover01.connectedNodeIds).not.toContain('PART-04')
    expect(hover01.connectedNodeIds).not.toContain('PROD-02')
  })

  it('hover on BOM Part: highlights connected upstream suppliers and downstream products/orders', () => {
    const hoverPart01 = getConnectedSupplyChainPaths(graph, 'PART-01')

    expect(hoverPart01.hoveredNodeId).toBe('PART-01')
    expect(hoverPart01.directUpstreamCount).toBe(1)
    expect(hoverPart01.upstreamNodeIds).toEqual(['SUP-01'])

    expect(hoverPart01.directDownstreamCount).toBe(1)
    expect(hoverPart01.downstreamNodeIds).toContain('PROD-01')
    expect(hoverPart01.downstreamNodeIds).toContain('ORD-01')
    expect(hoverPart01.downstreamNodeIds).not.toContain('PROD-02')
    expect(hoverPart01.downstreamNodeIds).not.toContain('ORD-07')
  })

  it('hover on Customer Order: highlights upstream product, BOM parts, and suppliers', () => {
    const hoverOrd01 = getConnectedSupplyChainPaths(graph, 'ORD-01')

    expect(hoverOrd01.hoveredNodeId).toBe('ORD-01')
    expect(hoverOrd01.directDownstreamCount).toBe(0)
    expect(hoverOrd01.totalDownstreamCount).toBe(0)

    // Directly fulfilled by PROD-01
    expect(hoverOrd01.directUpstreamCount).toBe(1)
    expect(hoverOrd01.upstreamNodeIds).toContain('PROD-01')
    expect(hoverOrd01.upstreamNodeIds).toContain('PART-01')
    expect(hoverOrd01.upstreamNodeIds).toContain('PART-02')
    expect(hoverOrd01.upstreamNodeIds).toContain('PART-05')
    expect(hoverOrd01.upstreamNodeIds).toContain('SUP-01')
  })

  it('hover with null node: returns zero connected elements safely', () => {
    const emptyHover = getConnectedSupplyChainPaths(graph, null)
    expect(emptyHover.hoveredNodeId).toBeNull()
    expect(emptyHover.connectedNodeIds).toEqual([])
    expect(emptyHover.connectedEdgeIds).toEqual([])
  })
})
