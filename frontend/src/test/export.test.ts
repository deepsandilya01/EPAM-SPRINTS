import { describe, it, expect, vi } from 'vitest'
import { exportGraphDataToCsv, exportGraphToPng } from '@/services/export.service'
import { INITIAL_SCENARIO_GRAPH } from '@/mocks/graph'
import { performGraphTraversal } from '@/services/traversal.service'

describe('Export Services Tests', () => {
  it('generates well-formed CSV data and triggers browser download', () => {
    const traversal = performGraphTraversal(INITIAL_SCENARIO_GRAPH, {
      sourceNodeId: 'SUP-01',
      direction: 'downstream',
      depth: 'all',
    })

    // Mock DOM URL and anchor click
    const createObjectURLMock = vi.fn().mockReturnValue('blob:mock-url')
    const revokeObjectURLMock = vi.fn()
    window.URL.createObjectURL = createObjectURLMock
    window.URL.revokeObjectURL = revokeObjectURLMock

    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    exportGraphDataToCsv(INITIAL_SCENARIO_GRAPH, traversal, 'test-export.csv')

    expect(createObjectURLMock).toHaveBeenCalled()
    expect(clickSpy).toHaveBeenCalled()
    expect(revokeObjectURLMock).toHaveBeenCalledWith('blob:mock-url')

    clickSpy.mockRestore()
  })

  it('handles missing container gracefully for PNG export', async () => {
    const success = await exportGraphToPng('non-existent-element-id')
    expect(success).toBe(false)
  })
})
