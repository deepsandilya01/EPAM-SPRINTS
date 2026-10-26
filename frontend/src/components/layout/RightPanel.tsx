import React, { useMemo } from 'react'
import {
  X,
  Factory,
  Package,
  Box,
  FileText,
  GitFork,
  ArrowRight,
} from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setSelectedNodeId } from '@/store/slices/graphUiSlice'
import { ScenarioGraph, TraversalResult } from '@/types'
import { getConnectedSupplyChainPaths } from '@/lib/graph/traverseGraph'

interface RightPanelProps {
  graph: ScenarioGraph
  traversalResult: TraversalResult
}

export const RightPanel: React.FC<RightPanelProps> = ({
  graph,
  traversalResult,
}) => {
  const dispatch = useAppDispatch()
  const { selectedNodeId } = useAppSelector((state) => state.graphUi)

  const selectedNode = selectedNodeId
    ? graph.nodes.find((n) => n.id === selectedNodeId)
    : graph.nodes.find((n) => n.id === traversalResult.sourceNodeId)

  const selectedPathInfo = useMemo(() => {
    return getConnectedSupplyChainPaths(graph, selectedNode?.id || null)
  }, [graph, selectedNode?.id])

  const handleClose = () => {
    dispatch(setSelectedNodeId(null))
  }

  const getNodeTypeBadge = () => {
    if (!selectedNode) return null
    switch (selectedNode.type) {
      case 'SUPPLIER':
        return {
          label: 'Supplier',
          bg: 'bg-red-50 text-red-600 border border-red-200',
          iconBg: 'bg-red-500',
          icon: <Factory className="w-5 h-5 text-white" />,
        }
      case 'BOM_PART':
        return {
          label: 'BOM Part',
          bg: 'bg-amber-50 text-amber-600 border border-amber-200',
          iconBg: 'bg-amber-500',
          icon: <Package className="w-5 h-5 text-white" />,
        }
      case 'FINISHED_PRODUCT':
        return {
          label: 'Product',
          bg: 'bg-teal-50 text-teal-700 border border-teal-200',
          iconBg: 'bg-teal-600',
          icon: <Box className="w-5 h-5 text-white" />,
        }
      case 'CUSTOMER_ORDER':
        return {
          label: 'Customer Order',
          bg: 'bg-blue-50 text-blue-600 border border-blue-200',
          iconBg: 'bg-blue-600',
          icon: <FileText className="w-5 h-5 text-white" />,
        }
    }
  }

  const badgeInfo = getNodeTypeBadge()

  const renderAttributes = () => {
    if (!selectedNode) return null
    const { details, type } = selectedNode

    if (type === 'SUPPLIER' && 'location' in details) {
      return (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Name</span>
            <span className="font-medium text-slate-800">{details.name}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Location</span>
            <span className="font-medium text-slate-800">{details.location}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Type</span>
            <span className="font-medium text-slate-800">{details.type}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Note</span>
            <span className="font-medium text-slate-800">{details.note}</span>
          </div>
          {details.reliabilityScore && (
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Reliability</span>
              <span className="font-semibold text-emerald-600">
                {details.reliabilityScore}%
              </span>
            </div>
          )}
        </div>
      )
    }

    if (type === 'BOM_PART' && 'stockLevel' in details) {
      return (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Part Name</span>
            <span className="font-medium text-slate-800">{details.name}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Category</span>
            <span className="font-medium text-slate-800">{details.category}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Stock Level</span>
            <span className="font-semibold text-slate-900">{details.stockLevel} units</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Unit Cost</span>
            <span className="font-medium text-slate-800">${details.unitCost.toFixed(2)}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-500">Lead Time</span>
            <span className="font-medium text-slate-800">{details.leadTimeDays} days</span>
          </div>
        </div>
      )
    }

    if (type === 'FINISHED_PRODUCT' && 'sku' in details) {
      return (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Product Name</span>
            <span className="font-medium text-slate-800">{details.name}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">SKU</span>
            <span className="font-medium text-slate-800">{details.sku}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Inventory</span>
            <span className="font-semibold text-slate-900">
              {details.currentInventory} units
            </span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Production Line</span>
            <span className="font-medium text-slate-800">{details.productionLine}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-500">Daily Target</span>
            <span className="font-medium text-slate-800">{details.dailyTarget} units/day</span>
          </div>
        </div>
      )
    }

    if (type === 'CUSTOMER_ORDER' && 'customerName' in details) {
      return (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Customer</span>
            <span className="font-medium text-slate-800">{details.customerName}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Quantity</span>
            <span className="font-semibold text-slate-900">{details.quantity} units</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Deadline</span>
            <span className="font-medium text-slate-800">{details.deliveryDeadline}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500">Status</span>
            <span className="font-medium text-blue-600">{details.status}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-500">Priority</span>
            <span
              className={`font-semibold ${
                details.priority === 'Urgent' ? 'text-red-600' : 'text-slate-800'
              }`}
            >
              {details.priority}
            </span>
          </div>
        </div>
      )
    }

    return null
  }

  return (
    <aside className="w-[300px] shrink-0 space-y-4 select-none">
      {/* Node details */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-bold text-xs text-slate-900 tracking-tight">
            Node Details
          </h3>
          <button
            onClick={handleClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors"
            title="Deselect node"
            aria-label="Close details"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        {selectedNode && badgeInfo ? (
          <div className="pt-3 space-y-3.5">
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-xs ${badgeInfo.iconBg}`}
              >
                {badgeInfo.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base text-slate-900">
                    {selectedNode.id}
                  </span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${badgeInfo.bg}`}
                  >
                    {badgeInfo.label}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-1">{renderAttributes()}</div>

            {/* Path connectivity */}
            <div className="pt-2 border-t border-slate-100">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Path Connectivity
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-50 p-2 rounded border border-slate-100">
                  <div className="text-[10px] text-slate-500">Direct Upstream</div>
                  <div className="text-sm font-bold text-slate-900">
                    {selectedPathInfo.directUpstreamCount}
                  </div>
                </div>
                <div className="bg-slate-50 p-2 rounded border border-slate-100">
                  <div className="text-[10px] text-slate-500">Direct Downstream</div>
                  <div className="text-sm font-bold text-slate-900">
                    {selectedPathInfo.directDownstreamCount}
                  </div>
                </div>
                <div className="bg-slate-50 p-2 rounded border border-slate-100">
                  <div className="text-[10px] text-slate-500">Total Upstream</div>
                  <div className="text-sm font-bold text-emerald-600">
                    {selectedPathInfo.totalUpstreamCount}
                  </div>
                </div>
                <div className="bg-slate-50 p-2 rounded border border-slate-100">
                  <div className="text-[10px] text-slate-500">Total Downstream</div>
                  <div className="text-sm font-bold text-blue-600">
                    {selectedPathInfo.totalDownstreamCount}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-slate-400">
            Click on any node to view details
          </div>
        )}
      </div>

      {/* Traversal summary */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs">
        <h3 className="font-bold text-xs text-slate-900 tracking-tight pb-3 border-b border-slate-100">
          Traversal Summary
        </h3>

        <div className="pt-3 space-y-3 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-600">
              <GitFork className="w-4 h-4 text-red-500" />
              <span>Source Supplier</span>
            </div>
            <span className="font-bold text-slate-900">
              {traversalResult.sourceNodeId}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-600">
              <Package className="w-4 h-4 text-amber-500" />
              <span>Total Entities Reached</span>
            </div>
            <span className="font-bold text-slate-900">
              {traversalResult.totalEntitiesReached}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-600">
              <Package className="w-4 h-4 text-amber-500" />
              <span>BOM Parts Reached</span>
            </div>
            <span className="font-bold text-teal-600">
              {traversalResult.reachableParts.length}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-600">
              <Box className="w-4 h-4 text-teal-600" />
              <span>Products Reached</span>
            </div>
            <span className="font-bold text-teal-600">
              {traversalResult.reachableProducts.length}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-600">
              <FileText className="w-4 h-4 text-blue-600" />
              <span>Customer Orders Reached</span>
            </div>
            <span className="font-bold text-blue-600">
              {traversalResult.reachableOrders.length}
            </span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs">
        <h3 className="font-bold text-xs text-slate-900 tracking-tight pb-3 border-b border-slate-100">
          Legend
        </h3>

        <div className="pt-3 space-y-2.5 text-xs">
          <div className="flex items-center gap-2.5 text-slate-700">
            <span className="w-3 h-3 rounded-full bg-red-500 shrink-0" />
            <span>Supplier (affected)</span>
          </div>
          <div className="flex items-center gap-2.5 text-slate-700">
            <span className="w-3 h-3 rounded-full bg-amber-500 shrink-0" />
            <span>BOM Part (affected)</span>
          </div>
          <div className="flex items-center gap-2.5 text-slate-700">
            <span className="w-3 h-3 rounded-full bg-teal-600 shrink-0" />
            <span>Product (affected)</span>
          </div>
          <div className="flex items-center gap-2.5 text-slate-700">
            <span className="w-3 h-3 rounded-full bg-blue-600 shrink-0" />
            <span>Customer Order (affected)</span>
          </div>
          <div className="flex items-center gap-2.5 text-slate-700">
            <span className="w-3 h-3 rounded-full bg-slate-300 shrink-0" />
            <span>Not affected</span>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center gap-2 text-slate-600 font-medium text-[11px]">
            <ArrowRight className="w-3.5 h-3.5 text-slate-800" />
            <span>SUPPLIES / USED_IN / FULFILLS</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
