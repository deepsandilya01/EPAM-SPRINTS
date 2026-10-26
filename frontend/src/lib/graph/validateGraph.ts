import { ValidationResult, ValidationFinding, ScenarioGraph } from '@/types'

export function validateGeneratedGraph(graph: ScenarioGraph): ValidationResult {
  const findings: ValidationFinding[] = []
  let totalChecks = 0
  let passedChecks = 0

  // 1. Ensure all node identifiers are globally unique
  totalChecks++
  const nodeIds = new Set<string>()
  const duplicateNodeIds: string[] = []
  for (const node of graph.nodes) {
    if (nodeIds.has(node.id)) {
      duplicateNodeIds.push(node.id)
    }
    nodeIds.add(node.id)
  }
  if (duplicateNodeIds.length > 0) {
    findings.push({
      id: 'val-dup-nodes',
      severity: 'error',
      category: 'duplicate_id',
      message: `Found duplicate node IDs: ${duplicateNodeIds.join(', ')}`,
      affectedEntities: duplicateNodeIds,
    })
  } else {
    passedChecks++
  }

  // 2. Ensure every edge references existing source and target nodes
  totalChecks++
  const missingEndpoints: string[] = []
  for (const edge of graph.edges) {
    if (!nodeIds.has(edge.source)) {
      missingEndpoints.push(`Missing source: ${edge.source} in edge ${edge.id}`)
    }
    if (!nodeIds.has(edge.target)) {
      missingEndpoints.push(`Missing target: ${edge.target} in edge ${edge.id}`)
    }
  }
  if (missingEndpoints.length > 0) {
    findings.push({
      id: 'val-missing-endpoints',
      severity: 'error',
      category: 'missing_endpoint',
      message: `Edges with missing endpoints: ${missingEndpoints.join('; ')}`,
      affectedEntities: missingEndpoints,
    })
  } else {
    passedChecks++
  }

  // 3. Verify DAG acyclicity via tri-state DFS cycle detection
  totalChecks++
  const adjacency = new Map<string, string[]>()
  for (const node of graph.nodes) {
    adjacency.set(node.id, [])
  }
  for (const edge of graph.edges) {
    adjacency.get(edge.source)?.push(edge.target)
  }

  const visited = new Map<string, number>() // 0: unvisited, 1: visiting (in-stack), 2: visited
  let hasCycle = false
  const cycleNodes: string[] = []

  function dfsDetectCycle(nodeId: string): boolean {
    visited.set(nodeId, 1)
    for (const neighbor of adjacency.get(nodeId) || []) {
      const state = visited.get(neighbor) || 0
      if (state === 1) {
        cycleNodes.push(neighbor, nodeId)
        return true
      }
      if (state === 0 && dfsDetectCycle(neighbor)) {
        return true
      }
    }
    visited.set(nodeId, 2)
    return false
  }

  for (const node of graph.nodes) {
    if ((visited.get(node.id) || 0) === 0) {
      if (dfsDetectCycle(node.id)) {
        hasCycle = true
        break
      }
    }
  }

  if (hasCycle) {
    findings.push({
      id: 'val-cycle-detected',
      severity: 'error',
      category: 'cycle_detection',
      message: `Graph contains circular dependencies: ${cycleNodes.join(' -> ')}`,
      affectedEntities: cycleNodes,
    })
  } else {
    passedChecks++
  }

  // 4. Validate tiered relationship schema compliance
  totalChecks++
  const nodeTypeMap = new Map<string, string>()
  for (const node of graph.nodes) {
    nodeTypeMap.set(node.id, node.type)
  }
  const invalidRelations: string[] = []
  for (const edge of graph.edges) {
    const srcType = nodeTypeMap.get(edge.source)
    const tgtType = nodeTypeMap.get(edge.target)
    if (edge.relation === 'SUPPLIES' && (srcType !== 'SUPPLIER' || tgtType !== 'BOM_PART')) {
      invalidRelations.push(`${edge.id}: SUPPLIES must connect SUPPLIER -> BOM_PART, got ${srcType} -> ${tgtType}`)
    }
    if (edge.relation === 'USED_IN' && (srcType !== 'BOM_PART' || tgtType !== 'FINISHED_PRODUCT')) {
      invalidRelations.push(`${edge.id}: USED_IN must connect BOM_PART -> FINISHED_PRODUCT, got ${srcType} -> ${tgtType}`)
    }
    if (edge.relation === 'FULFILLS' && (srcType !== 'FINISHED_PRODUCT' || tgtType !== 'CUSTOMER_ORDER')) {
      invalidRelations.push(`${edge.id}: FULFILLS must connect FINISHED_PRODUCT -> CUSTOMER_ORDER, got ${srcType} -> ${tgtType}`)
    }
  }
  if (invalidRelations.length > 0) {
    findings.push({
      id: 'val-semantic-mismatch',
      severity: 'error',
      category: 'schema_mismatch',
      message: `Relationship hierarchy mismatch: ${invalidRelations.join('; ')}`,
      affectedEntities: invalidRelations,
    })
  } else {
    passedChecks++
  }

  return {
    isValid: findings.filter((f) => f.severity === 'error').length === 0,
    totalChecks,
    passedChecks,
    findings,
  }
}
