import React, { useState, useEffect } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { SummaryCards } from '@/components/dashboard/SummaryCards'
import { GraphCanvas } from '@/components/graph/GraphCanvas'
import { RightPanel } from '@/components/layout/RightPanel'
import { PerformanceSection } from '@/components/dashboard/PerformanceSection'
import { StepwiseTimingTable } from '@/components/dashboard/StepwiseTimingTable'
import { ReachableOrders } from '@/components/dashboard/ReachableOrders'
import { useScenarioGraph } from '@/api/graph.api'
import { useTraversal } from '@/api/traversal.api'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setAvailableSuppliers, setSelectedSupplier } from '@/store/slices/graphUiSlice'
import { TraversalRequest } from '@/types'
import { GraphGenerationParams, DEFAULT_GRAPH_PARAMS } from '@/types/graph.types'

export const GraphExplorerPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const {
    supplierCount,
    partCount,
    productCount,
    orderCount,
    selectedSupplier,
    traceDirection,
    highlightDepth,
    nodeFilters,
    showUnaffected,
  } = useAppSelector((state) => state.graphUi)

  // Active generation params that are currently rendered
  const [activeParams, setActiveParams] = useState<GraphGenerationParams>(DEFAULT_GRAPH_PARAMS)

  // Traversal request state
  const [activeRequest, setActiveRequest] = useState<TraversalRequest>({
    sourceNodeId: selectedSupplier,
    direction: traceDirection,
    depth: highlightDepth,
    nodeFilters,
    showUnaffected,
  })

  // Queries
  const { data: graph, isLoading: isGraphLoading, isError: isGraphError } = useScenarioGraph(activeParams)
  const { data: traversalResult, isLoading: isTraversalLoading } = useTraversal(graph, activeRequest)

  // Keep available suppliers synced with generated graph
  useEffect(() => {
    if (graph?.suppliers && graph.suppliers.length > 0) {
      const supIds = graph.suppliers.map((s) => s.id)
      dispatch(setAvailableSuppliers(supIds))
      if (!supIds.includes(activeRequest.sourceNodeId)) {
        const nextSupplier = supIds[0] || 'SUP-01'
        dispatch(setSelectedSupplier(nextSupplier))
        setActiveRequest((prev) => ({ ...prev, sourceNodeId: nextSupplier }))
      }
    }
  }, [graph, dispatch, activeRequest.sourceNodeId])

  // Regenerate / apply input parameters
  const handleGenerateGraph = () => {
    const newParams: GraphGenerationParams = {
      supplierCount,
      partCount,
      productCount,
      orderCount,
    }
    setActiveParams(newParams)
    setActiveRequest({
      sourceNodeId: selectedSupplier,
      direction: traceDirection,
      depth: highlightDepth,
      nodeFilters,
      showUnaffected,
    })
  }

  // Fallback while loading
  if (isGraphLoading || !graph || isTraversalLoading || !traversalResult) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Generating IntelliTwin supply chain graph...</p>
        </div>
      </div>
    )
  }

  if (isGraphError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="bg-white p-6 rounded-lg border border-red-200 text-center shadow-sm max-w-md">
          <h2 className="text-base font-bold text-red-600 mb-2">Graph Generation Failed</h2>
          <p className="text-xs text-slate-600 mb-4">Could not generate valid supply chain graph topology.</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-semibold rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const directionTitle =
    activeRequest.direction === 'downstream' ? 'Downstream' : 'Upstream'

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      <Sidebar
        graph={graph}
        traversalResult={traversalResult}
        onGenerateGraph={handleGenerateGraph}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="p-6 space-y-6 max-w-[1640px] mx-auto w-full">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 leading-tight">
              {directionTitle} trace from {traversalResult.sourceNodeId}
            </h1>
            <p className="text-xs font-medium text-slate-500 mt-1">
              {traversalResult.totalEntitiesReached} entities reached,{' '}
              {traversalResult.reachableOrders.length} customer orders affected ({graph.nodes.length} nodes, {graph.edges.length} directed edges)
            </p>
          </div>

          <SummaryCards graph={graph} />

          <div className="flex gap-6 items-start">
            <div className="flex-1 min-w-0 space-y-6">
              <GraphCanvas
                graph={graph}
                traversalResult={traversalResult}
              />

              <PerformanceSection traversalResult={traversalResult} />

              <div className="flex gap-4 items-stretch">
                <StepwiseTimingTable
                  steps={traversalResult.examplePath}
                  sourceSupplier={traversalResult.sourceNodeId}
                />
                <ReachableOrders
                  orders={graph.orders}
                  reachableOrderIds={traversalResult.reachableOrders}
                />
              </div>
            </div>

            <RightPanel
              graph={graph}
              traversalResult={traversalResult}
            />
          </div>
        </main>
      </div>
    </div>
  )
}
