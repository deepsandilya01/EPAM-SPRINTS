import { describe, it, expect } from 'vitest'
import { validateScenarioGraph } from '@/mocks/validation'
import { INITIAL_SCENARIO_GRAPH } from '@/mocks/graph'
import { ScenarioGraph } from '@/types'

describe('Graph Validation Service Tests', () => {
  it('validates that canonical scenario graph passes all integrity checks', () => {
    const result = validateScenarioGraph(INITIAL_SCENARIO_GRAPH)
    expect(result.isValid).toBe(true)
    expect(result.passedChecks).toBe(result.totalChecks)
    expect(result.findings.filter((f) => f.severity === 'error').length).toBe(0)
  })

  it('detects duplicate node identifiers', () => {
    const corruptedGraph: ScenarioGraph = {
      ...INITIAL_SCENARIO_GRAPH,
      nodes: [
        ...INITIAL_SCENARIO_GRAPH.nodes,
        {
          id: 'SUP-01', // duplicate
          label: 'SUP-01 duplicate',
          type: 'SUPPLIER',
          isAffected: false,
          isSource: false,
          details: INITIAL_SCENARIO_GRAPH.suppliers[0],
          column: 1,
        },
      ],
    }

    const result = validateScenarioGraph(corruptedGraph)
    expect(result.isValid).toBe(false)
    const dupFinding = result.findings.find((f) => f.category === 'duplicate_id')
    expect(dupFinding).toBeDefined()
    expect(dupFinding?.severity).toBe('error')
  })

  it('detects missing edge endpoints', () => {
    const corruptedGraph: ScenarioGraph = {
      ...INITIAL_SCENARIO_GRAPH,
      edges: [
        ...INITIAL_SCENARIO_GRAPH.edges,
        {
          id: 'e-bad-edge',
          source: 'NONEXISTENT_SOURCE',
          target: 'PART-01',
          relation: 'SUPPLIES',
          isAffected: false,
        },
      ],
    }

    const result = validateScenarioGraph(corruptedGraph)
    expect(result.isValid).toBe(false)
    const missingFinding = result.findings.find((f) => f.category === 'missing_endpoint')
    expect(missingFinding).toBeDefined()
  })

  it('detects cycle introduction in the directed graph', () => {
    const cyclicGraph: ScenarioGraph = {
      ...INITIAL_SCENARIO_GRAPH,
      edges: [
        ...INITIAL_SCENARIO_GRAPH.edges,
        // Introduce reverse cycle: PROD-01 -> SUP-01
        {
          id: 'e-cyclic',
          source: 'PROD-01',
          target: 'SUP-01',
          relation: 'SUPPLIES',
          isAffected: false,
        },
      ],
    }

    const result = validateScenarioGraph(cyclicGraph)
    expect(result.isValid).toBe(false)
    const cycleFinding = result.findings.find((f) => f.category === 'cycle_detection')
    expect(cycleFinding).toBeDefined()
  })
})
