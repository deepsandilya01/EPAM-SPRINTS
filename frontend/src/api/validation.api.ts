import { useQuery } from '@tanstack/react-query'
import { apiClient, DATA_MODE } from './client'
import { ValidationResult } from '@/types'
import { validateScenarioGraph } from '@/mocks/validation'
import { INITIAL_SCENARIO_GRAPH } from '@/mocks/graph'

export async function fetchValidationResult(): Promise<ValidationResult> {
  if (DATA_MODE === 'live') {
    const response = await apiClient.get<ValidationResult>('/api/validation/check')
    return response.data
  }

  return Promise.resolve(validateScenarioGraph(INITIAL_SCENARIO_GRAPH))
}

export function useValidation() {
  return useQuery({
    queryKey: ['graph-validation', DATA_MODE],
    queryFn: fetchValidationResult,
  })
}
