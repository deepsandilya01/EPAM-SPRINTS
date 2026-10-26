import React from 'react'
import { Header } from '@/components/layout/Header'
import { Network, ShieldAlert, BarChart3, ArrowRight, GitFork, Cpu, Layers } from 'lucide-react'
import { Link } from 'react-router-dom'

export const OverviewPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col">
      <Header />

      <main className="p-8 max-w-[1200px] mx-auto w-full space-y-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-900 to-slate-900 text-white rounded-xl p-8 shadow-sm">
          <div className="max-w-2xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              Team PHOTON • IntelliTwin Engine
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Enterprise Supply Chain Graph & Scenario Generator
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Real-time multi-tier dependency tracing, impact propagation, and simulated disruption analysis across suppliers, bill-of-materials parts, finished products, and customer orders.
            </p>
            <div className="pt-2">
              <Link
                to="/graph-explorer"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-sm transition-all"
              >
                <span>Launch Graph Explorer</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>

        {/* Core Modules Grid */}
        <div className="grid grid-cols-3 gap-6">
          <Link
            to="/graph-explorer"
            className="group bg-white rounded-lg border border-slate-200 p-6 shadow-xs hover:border-blue-400 hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <Network className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-slate-900 mb-2">
                Supply Chain Graph Explorer
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                Interactive 4-tier horizontal dependency visualization with upstream/downstream BFS traversal, highlight filters, and order reachability.
              </p>
            </div>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-blue-600 group-hover:text-blue-700">
              <span>Explore Graph</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          <Link
            to="/validation"
            className="group bg-white rounded-lg border border-slate-200 p-6 shadow-xs hover:border-blue-400 hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-slate-900 mb-2">
                Graph Integrity & Validation
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                Automated schema validation, DAG cycle detection, orphaned endpoint audits, and topological invariant checks.
              </p>
            </div>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-emerald-600 group-hover:text-emerald-700">
              <span>View Invariants</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          <Link
            to="/performance"
            className="group bg-white rounded-lg border border-slate-200 p-6 shadow-xs hover:border-blue-400 hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center mb-4 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                <BarChart3 className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-slate-900 mb-2">
                Performance Benchmarks
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                Empirical latency benchmarks comparing BFS vs DFS queue execution, p95/p99 distributions, and O(V + E) complexity bounds.
              </p>
            </div>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-purple-600 group-hover:text-purple-700">
              <span>Inspect Metrics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>
        </div>

        {/* Key Scenario Facts */}
        <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 mb-4">
            Sprint 1 Canonical Architecture
          </h3>
          <div className="grid grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded border border-slate-100">
              <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                <GitFork className="w-3.5 h-3.5 text-blue-600" />
                19 Graph Nodes
              </div>
              <div className="text-slate-500 mt-1">2 Suppliers, 5 BOM Parts, 2 Products, 10 Orders</div>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-100">
              <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                <ArrowRight className="w-3.5 h-3.5 text-blue-600" />
                21 Directed Edges
              </div>
              <div className="text-slate-500 mt-1">6 SUPPLIES, 5 USED_IN, 10 FULFILLS</div>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-100">
              <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-blue-600" />
                BFS Traversal
              </div>
              <div className="text-slate-500 mt-1">O(V + E) linear time, O(V) space complexity</div>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-100">
              <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-blue-600" />
                FastAPI Ready
              </div>
              <div className="text-slate-500 mt-1">Decoupled data provider & TanStack Query client</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
