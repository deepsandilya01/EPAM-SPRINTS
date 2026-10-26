import { useQuery } from '@tanstack/react-query'
import { apiClient, DATA_MODE } from './client'
import { BenchmarkResult } from '@/types'
import { runLocalBenchmark } from '@/mocks/benchmark'

export async function fetchBenchmarkResult(iterations = 100): Promise<BenchmarkResult> {
  if (DATA_MODE === 'live') {
    const response = await apiClient.post<BenchmarkResult>('/api/benchmark/run', { iterations })
    return response.data
  }

  return Promise.resolve(runLocalBenchmark(iterations))
}

export function useBenchmark(iterations = 100) {
  return useQuery({
    queryKey: ['benchmark-metrics', iterations, DATA_MODE],
    queryFn: () => fetchBenchmarkResult(iterations),
  })
}
