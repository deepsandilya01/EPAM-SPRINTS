import { useQuery } from '@tanstack/react-query'
import { apiClient, DATA_MODE } from './client'
import { ScenarioGraph } from '@/types'
import { GraphGenerationParams, DEFAULT_GRAPH_PARAMS } from '@/types/graph.types'
import { generateSupplyChainGraph } from '@/lib/graph/generateGraph'

export async function fetchScenarioGraph(params: GraphGenerationParams = DEFAULT_GRAPH_PARAMS): Promise<ScenarioGraph> {
  if (DATA_MODE === 'live') {
    const response = await apiClient.post<ScenarioGraph>('/api/graph/generate', params)
    return response.data
  }
  // Local dynamic generation mode
  return Promise.resolve(generateSupplyChainGraph(params))
}

export function useScenarioGraph(params: GraphGenerationParams = DEFAULT_GRAPH_PARAMS) {
  return useQuery({
    queryKey: ['scenario-graph', params.supplierCount, params.partCount, params.productCount, params.orderCount, DATA_MODE],
    queryFn: () => fetchScenarioGraph(params),
    staleTime: Infinity,
  })
}
