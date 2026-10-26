import React from 'react'
import { Clock, Network, ArrowRight, Settings } from 'lucide-react'
import { TraversalResult } from '@/types'

interface PerformanceSectionProps {
  traversalResult: TraversalResult
}

export const PerformanceSection: React.FC<PerformanceSectionProps> = ({
  traversalResult,
}) => {
  const directionTitle =
    traversalResult.direction === 'downstream' ? 'Downstream' : 'Upstream'

  return (
    <div className="space-y-2.5">
      <h3 className="text-xs font-bold text-slate-800 tracking-tight">
        Traversal Performance ({traversalResult.sourceNodeId} → {directionTitle})
      </h3>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-slate-200 p-3.5 shadow-xs flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-100 flex items-center justify-center shrink-0 text-teal-600">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-500">
              Total Traversal Time
            </div>
            <div className="text-xl font-bold text-slate-900 leading-tight">
              {traversalResult.executionTimeMs} ms
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-3.5 shadow-xs flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0 text-blue-600">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-500">
              Visited Nodes
            </div>
            <div className="text-xl font-bold text-slate-900 leading-tight">
              {traversalResult.visitedNodesCount}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-3.5 shadow-xs flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0 text-blue-600">
            <ArrowRight className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-500">
              Traversed Edges
            </div>
            <div className="text-xl font-bold text-slate-900 leading-tight">
              {traversalResult.traversedEdgesCount}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-3.5 shadow-xs flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0 text-blue-600">
            <Settings className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-500">
              Algorithm
            </div>
            <div className="text-xl font-bold text-slate-900 leading-tight">
              {traversalResult.algorithm}
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              Time Complexity: {traversalResult.complexity}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
