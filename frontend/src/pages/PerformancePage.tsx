import React, { useState } from 'react'
import { Header } from '@/components/layout/Header'
import { useBenchmark } from '@/api/benchmark.api'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Cpu, Zap, Activity, ArrowLeft, Play } from 'lucide-react'
import { Link } from 'react-router-dom'

export const PerformancePage: React.FC = () => {
  const [iterations, setIterations] = useState<number>(100)
  const { data: benchmarkResult, isLoading, refetch, isFetching } = useBenchmark(iterations)

  const chartData = benchmarkResult
    ? [
        {
          metric: 'Average (ms)',
          BFS: benchmarkResult.bfsMetrics.averageDurationMs,
          DFS: benchmarkResult.dfsMetrics.averageDurationMs,
        },
        {
          metric: 'P95 Latency (ms)',
          BFS: benchmarkResult.bfsMetrics.p95DurationMs,
          DFS: benchmarkResult.dfsMetrics.p95DurationMs,
        },
        {
          metric: 'P99 Latency (ms)',
          BFS: benchmarkResult.bfsMetrics.p99DurationMs,
          DFS: benchmarkResult.dfsMetrics.p99DurationMs,
        },
      ]
    : []

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col">
      <Header />

      <main className="p-8 max-w-[1400px] mx-auto w-full space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Link
                to="/graph-explorer"
                className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 font-semibold"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Back to Graph Explorer
              </Link>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Traversal Performance & Benchmark Profiles
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Comparative empirical benchmarks measuring BFS queue traversal versus DFS stack recursion across synthetic load iterations.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={iterations}
              onChange={(e) => setIterations(Number(e.target.value))}
              className="text-xs border border-slate-200 rounded-md px-3 py-2 bg-white text-slate-800 shadow-xs outline-none"
            >
              <option value={50}>50 iterations</option>
              <option value={100}>100 iterations</option>
              <option value={500}>500 iterations</option>
            </select>

            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-md text-xs font-semibold hover:bg-blue-700 shadow-xs transition-colors cursor-pointer disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>{isFetching ? 'Profiling...' : 'Run Benchmark'}</span>
            </button>
          </div>
        </div>

        {isLoading || !benchmarkResult ? (
          <div className="py-20 text-center text-xs text-slate-400">
            Executing algorithmic performance profile...
          </div>
        ) : (
          <div className="space-y-6">
            {/* Metric Overview Cards */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] font-medium text-slate-500">BFS Avg Latency</div>
                  <div className="text-xl font-bold text-slate-900">
                    {benchmarkResult.bfsMetrics.averageDurationMs} ms
                  </div>
                  <div className="text-[10px] text-slate-400">
                    P99: {benchmarkResult.bfsMetrics.p99DurationMs} ms
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Activity className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] font-medium text-slate-500">DFS Avg Latency</div>
                  <div className="text-xl font-bold text-slate-900">
                    {benchmarkResult.dfsMetrics.averageDurationMs} ms
                  </div>
                  <div className="text-[10px] text-slate-400">
                    P99: {benchmarkResult.dfsMetrics.p99DurationMs} ms
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] font-medium text-slate-500">Memory Allocation</div>
                  <div className="text-xl font-bold text-slate-900">
                    {benchmarkResult.bfsMetrics.memoryUsageKb} KB
                  </div>
                  <div className="text-[10px] text-slate-400">Auxiliary queue overhead</div>
                </div>
              </div>
            </div>

            {/* Recharts Bar Chart */}
            <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-xs">
              <h2 className="text-sm font-bold text-slate-900 mb-4">
                Latency Distribution (BFS vs. DFS) across {iterations} Runs
              </h2>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="metric" tick={{ fontSize: 12, fill: '#64748b' }} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} unit=" ms" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        borderColor: '#e2e8f0',
                        fontSize: '12px',
                        borderRadius: '6px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <Legend />
                    <Bar dataKey="BFS" fill="#0d9488" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="DFS" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Complexity & Specifications */}
            <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-xs grid grid-cols-2 gap-6 text-xs">
              <div>
                <h3 className="font-bold text-slate-900 text-sm mb-2">Algorithm Complexity Bounds</h3>
                <ul className="space-y-2 text-slate-600">
                  <li>
                    <span className="font-semibold text-slate-800">Time Complexity:</span> O(V + E) —
                    where |V| = 19 nodes, |E| = 21 directed edges.
                  </li>
                  <li>
                    <span className="font-semibold text-slate-800">Auxiliary Space Complexity:</span> O(V) —
                    constrained by visited node HashSet and queue buffer.
                  </li>
                  <li>
                    <span className="font-semibold text-slate-800">Spanning Tree Convention:</span> First-seen
                    predecessors formulate tree edges, deduplicating multi-supplier convergence.
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-bold text-slate-900 text-sm mb-2">Measurement Methodology</h3>
                <p className="text-slate-600 leading-relaxed">
                  Execution durations represent real wall-clock elapsed time measured with high-precision{' '}
                  <code className="text-blue-600 font-mono">performance.now()</code>. Edge latencies displayed
                  in step-wise tables represent calibrated micro-models for downstream supply pipeline visualization.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
