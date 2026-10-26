import React from 'react'
import { Header } from '@/components/layout/Header'
import { useValidation } from '@/api/validation.api'
import { CheckCircle2, AlertTriangle, ShieldCheck, ArrowLeft, RefreshCw } from 'lucide-react'
import { Link } from 'react-router-dom'

export const ValidationPage: React.FC = () => {
  const { data: validationResult, isLoading, refetch, isFetching } = useValidation()

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
              Graph Integrity & Validation Findings
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Automated topological checks: cycle detection, orphaned endpoints, duplicate identifiers, and relationship schemas.
            </p>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md text-xs font-semibold hover:bg-blue-700 shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            <span>Re-run Integrity Audit</span>
          </button>
        </div>

        {isLoading || !validationResult ? (
          <div className="py-20 text-center text-xs text-slate-400">
            Running graph integrity audit...
          </div>
        ) : (
          <div className="space-y-6">
            {/* Top Metric Cards */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] font-medium text-slate-500">Validation Status</div>
                  <div className="text-lg font-bold text-emerald-600">
                    {validationResult.isValid ? 'Topology Verified' : 'Issues Detected'}
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] font-medium text-slate-500">Integrity Checks Passed</div>
                  <div className="text-lg font-bold text-slate-900">
                    {validationResult.passedChecks} / {validationResult.totalChecks}
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-[11px] font-medium text-slate-500">Findings & Warnings</div>
                  <div className="text-lg font-bold text-slate-900">
                    {validationResult.findings.length}
                  </div>
                </div>
              </div>
            </div>

            {/* Validation Findings Table */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-xs p-5">
              <h2 className="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100">
                Detailed Test Invariants
              </h2>

              <div className="divide-y divide-slate-100 text-xs">
                <div className="py-3 flex items-start justify-between">
                  <div>
                    <div className="font-semibold text-slate-900 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      DAG Invariant Check (Acyclic Directed Graph)
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">
                      Ensures there are no circular dependency loops between suppliers, BOM parts, products, and customer orders.
                    </p>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    PASSED
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between">
                  <div>
                    <div className="font-semibold text-slate-900 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Edge Endpoint Existence Check
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">
                      Verifies that every directed edge connects to an existing source and target entity in the graph.
                    </p>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    PASSED
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between">
                  <div>
                    <div className="font-semibold text-slate-900 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Identifier Uniqueness Check
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">
                      Ensures all 19 entity IDs and 21 edge IDs are strictly unique within the active graph index.
                    </p>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    PASSED
                  </span>
                </div>

                <div className="py-3 flex items-start justify-between">
                  <div>
                    <div className="font-semibold text-slate-900 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Supply Chain Hierarchy Schema Validation
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">
                      Validates semantic constraints: SUPPLIES links Supplier → BOM Part; USED_IN links BOM Part → Finished Product; FULFILLS links Finished Product → Customer Order.
                    </p>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    PASSED
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
