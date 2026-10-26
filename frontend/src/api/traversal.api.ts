import { useQuery } from '@tanstack/react-query'
import { apiClient, DATA_MODE } from './client'
import { ScenarioGraph, TraversalRequest, TraversalResult } from '@/types'
import { traverseGraph } from '@/lib/graph/traverseGraph'

export async function fetchTraversalResult(
  graph: ScenarioGraph,
  request: TraversalRequest
): Promise<TraversalResult> {
  if (DATA_MODE === 'live') {
    const response = await apiClient.post<TraversalResult>('/api/traversal/run', request)
    return response.data
  }

  // Local simulated execution over dynamic scenario graph
  return Promise.resolve(traverseGraph(graph, request))
}

export function useTraversal(graph: ScenarioGraph | undefined, request: TraversalRequest) {
  return useQuery({
    queryKey: [
      'traversal',
      graph?.nodes.length,
      graph?.edges.length,
      request.sourceNodeId,
      request.direction,
      request.depth,
      DATA_MODE,
    ],
    queryFn: () => {
      if (!graph) throw new Error('Graph not loaded')
      return fetchTraversalResult(graph, request)
    },
    enabled: !!graph,
    staleTime: 60000,
  })
}
