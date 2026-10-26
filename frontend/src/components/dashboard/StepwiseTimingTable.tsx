import React from 'react'
import { TraversalStep } from '@/types'

interface StepwiseTimingTableProps {
  steps: TraversalStep[]
  sourceSupplier: string
}

export const StepwiseTimingTable: React.FC<StepwiseTimingTableProps> = ({
  steps,
  sourceSupplier,
}) => {
  const targetOrder = sourceSupplier === 'SUP-01' ? 'ORD-01' : 'ORD-07'

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs flex-1 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="text-xs font-bold text-slate-900 tracking-tight">
            Step-wise Traversal Timing (Example Path to {targetOrder})
          </h3>
          <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-mono">
            Simulated Path Latency
          </span>
        </div>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="text-slate-400 font-semibold border-b border-slate-100 text-[11px]">
                <th className="py-2 px-2">Step</th>
                <th className="py-2 px-2">From Node</th>
                <th className="py-2 px-2">To Node</th>
                <th className="py-2 px-2">Relation</th>
                <th className="py-2 px-2 text-right">Traversal Time (ms)</th>
                <th className="py-2 px-2 text-right">Cumulative Time (ms)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 font-medium">
              {steps.map((step) => {
                let relationColor = 'text-slate-600'
                if (step.relation === 'SUPPLIES') relationColor = 'text-red-600'
                else if (step.relation === 'USED_IN') relationColor = 'text-amber-600'
                else if (step.relation === 'FULFILLS') relationColor = 'text-blue-600'

                return (
                  <tr key={step.step} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-2 text-slate-500 font-mono">{step.step}</td>
                    <td className="py-2.5 px-2 font-bold text-slate-800">{step.fromNode}</td>
                    <td className="py-2.5 px-2 font-bold text-slate-800">{step.toNode}</td>
                    <td className={`py-2.5 px-2 font-semibold ${relationColor}`}>
                      {step.relation}
                    </td>
                    <td className="py-2.5 px-2 text-right font-mono text-slate-700">
                      {step.traversalTimeMs.toFixed(1)}
                    </td>
                    <td className="py-2.5 px-2 text-right font-mono font-bold text-slate-900">
                      {step.cumulativeTimeMs.toFixed(1)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="pt-2 text-[10px] text-slate-400 italic">
        *Per-edge traversal timings are simulated benchmark models. Wall-clock traversal is calculated independently.
      </div>
    </div>
  )
}
