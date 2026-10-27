import React, { useState } from 'react'
import {
  RotateCcw,
  Factory,
  ChevronDown,
  Play,
  Maximize,
  Download,
  FileSpreadsheet,
  Layers,
  Check,
  AlertCircle,
} from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import {
  setGraphCount,
  setInputErrors,
  setSelectedSupplier,
  setTraceDirection,
  setHighlightDepth,
  toggleNodeFilter,
  setShowUnaffected,
  resetUiState,
} from '@/store/slices/graphUiSlice'
import { triggerResetView } from '@/store/slices/graphViewSlice'
import { EntityType, HighlightDepth, TraceDirection, ScenarioGraph, TraversalResult } from '@/types'
import { GRAPH_LIMITS, GraphGenerationParams } from '@/types/graph.types'
import { exportGraphToPng, exportGraphDataToCsv } from '@/services/export.service'

interface SidebarProps {
  graph: ScenarioGraph
  traversalResult: TraversalResult
  onGenerateGraph: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  graph,
  traversalResult,
  onGenerateGraph,
}) => {
  const dispatch = useAppDispatch()
  const {
    supplierCount,
    partCount,
    productCount,
    orderCount,
    inputErrors,
    availableSuppliers,
    selectedSupplier,
    traceDirection,
    highlightDepth,
    nodeFilters,
    showUnaffected,
  } = useAppSelector((state) => state.graphUi)

  const [supplierDropdownOpen, setSupplierDropdownOpen] = useState(false)
  const [depthDropdownOpen, setDepthDropdownOpen] = useState(false)
  const [filterDropdownOpen, setFilterDropdownOpen] = useState(false)
  const [isExportingPng, setIsExportingPng] = useState(false)

  // Local text input state for immediate typing feedback and validation
  const [localSupplierCount, setLocalSupplierCount] = useState(String(supplierCount))
  const [localPartCount, setLocalPartCount] = useState(String(partCount))
  const [localProductCount, setLocalProductCount] = useState(String(productCount))
  const [localOrderCount, setLocalOrderCount] = useState(String(orderCount))

  // Synchronize local input state on external reset
  React.useEffect(() => {
    setLocalSupplierCount(String(supplierCount))
    setLocalPartCount(String(partCount))
    setLocalProductCount(String(productCount))
    setLocalOrderCount(String(orderCount))
  }, [supplierCount, partCount, productCount, orderCount])

  const validateField = (
    field: keyof GraphGenerationParams,
    rawVal: string,
    min: number,
    max: number,
    label: string
  ): string | null => {
    if (!rawVal.trim()) {
      return `${label} is required`
    }
    const num = Number(rawVal)
    if (!Number.isInteger(num)) {
      return 'Must be a whole integer'
    }
    if (num < min) {
      return `Must be at least ${min}`
    }
    if (num > max) {
      return `Max limit is ${max}`
    }
    return null
  }

  const handleCountChange = (
    field: keyof GraphGenerationParams,
    value: string,
    setLocal: (v: string) => void,
    min: number,
    max: number,
    label: string
  ) => {
    setLocal(value)
    const err = validateField(field, value, min, max, label)
    const newErrors = { ...inputErrors }
    if (err) {
      newErrors[field] = err
    } else {
      delete newErrors[field]
      dispatch(setGraphCount({ field, value: parseInt(value, 10) }))
    }
    dispatch(setInputErrors(newErrors))
  }

  const handleGenerateClick = () => {
    const errs: Record<string, string> = {}
    const supErr = validateField('supplierCount', localSupplierCount, GRAPH_LIMITS.MIN_COUNT, GRAPH_LIMITS.MAX_SUPPLIERS, 'Suppliers')
    const partErr = validateField('partCount', localPartCount, GRAPH_LIMITS.MIN_COUNT, GRAPH_LIMITS.MAX_PARTS, 'BOM Parts')
    const prodErr = validateField('productCount', localProductCount, GRAPH_LIMITS.MIN_COUNT, GRAPH_LIMITS.MAX_PRODUCTS, 'Products')
    const ordErr = validateField('orderCount', localOrderCount, GRAPH_LIMITS.MIN_COUNT, GRAPH_LIMITS.MAX_ORDERS, 'Orders')

    if (supErr) errs.supplierCount = supErr
    if (partErr) errs.partCount = partErr
    if (prodErr) errs.productCount = prodErr
    if (ordErr) errs.orderCount = ordErr

    if (Object.keys(errs).length > 0) {
      dispatch(setInputErrors(errs))
      return
    }

    onGenerateGraph()
  }

  const handleReset = () => {
    dispatch(resetUiState())
    dispatch(triggerResetView())
  }

  const handleResetView = () => {
    dispatch(triggerResetView())
  }

  const handleDownloadPng = async () => {
    setIsExportingPng(true)
    await exportGraphToPng('graph-canvas-container', `intellitwin-${selectedSupplier}-graph.png`)
    setIsExportingPng(false)
  }

  const handleExportCsv = () => {
    exportGraphDataToCsv(graph, traversalResult, `intellitwin-${selectedSupplier}-data.csv`)
  }

  const filterOptions: { label: string; value: EntityType }[] = [
    { label: 'Suppliers', value: 'SUPPLIER' },
    { label: 'BOM Parts', value: 'BOM_PART' },
    { label: 'Products', value: 'FINISHED_PRODUCT' },
    { label: 'Customer Orders', value: 'CUSTOMER_ORDER' },
  ]

  const depthLabels: Record<HighlightDepth, string> = {
    all: 'All Levels',
    direct: 'Direct Parts (Level 1)',
    parts_products: 'Parts + Products (Level 2)',
    custom: 'Custom Depth',
  }

  return (
    <aside className="w-[275px] shrink-0 bg-white border-r border-slate-200 flex flex-col justify-between h-screen sticky top-0 overflow-y-auto select-none p-4 text-slate-800">
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2.5 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white shadow-xs">
              <div className="relative w-4 h-4">
                <span className="absolute inset-0 rounded-full border-2 border-white opacity-80" />
                <span className="absolute inset-1 rounded-full bg-white" />
              </div>
            </div>
            <span className="font-bold text-base tracking-tight text-slate-900">
              IntelliTwin
            </span>
          </div>
          <button
            className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors"
            title="Toggle sidebar"
            aria-label="Toggle sidebar"
          >
            <Layers className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-sm text-slate-900">Input Parameters</h2>
          <button
            onClick={handleReset}
            className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        </div>

        {/* Entity generator inputs */}
        <div className="space-y-2 bg-slate-50/80 p-2.5 rounded-lg border border-slate-200/70">
          <div className="text-[11px] font-bold text-slate-700 flex items-center justify-between">
            <span>Graph Generator Quantities</span>
            <span className="text-[10px] text-slate-400 font-normal">Positive ints</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <label className="text-[10px] font-semibold text-slate-600 block mb-0.5">
                Suppliers <span className="text-slate-400 font-normal">(1-20)</span>
              </label>
              <input
                type="number"
                min={GRAPH_LIMITS.MIN_COUNT}
                max={GRAPH_LIMITS.MAX_SUPPLIERS}
                value={localSupplierCount}
                onChange={(e) =>
                  handleCountChange('supplierCount', e.target.value, setLocalSupplierCount, 1, GRAPH_LIMITS.MAX_SUPPLIERS, 'Suppliers')
                }
                className={`w-full px-2 py-1 text-xs bg-white border rounded shadow-2xs outline-none ${
                  inputErrors.supplierCount ? 'border-red-400 bg-red-50/30' : 'border-slate-200 focus:border-blue-500'
                }`}
              />
              {inputErrors.supplierCount && (
                <span className="text-[9px] text-red-500 flex items-center gap-0.5 mt-0.5">
                  <AlertCircle className="w-2.5 h-2.5 shrink-0" />
                  {inputErrors.supplierCount}
                </span>
              )}
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-600 block mb-0.5">
                BOM Parts <span className="text-slate-400 font-normal">(1-50)</span>
              </label>
              <input
                type="number"
                min={GRAPH_LIMITS.MIN_COUNT}
                max={GRAPH_LIMITS.MAX_PARTS}
                value={localPartCount}
                onChange={(e) =>
                  handleCountChange('partCount', e.target.value, setLocalPartCount, 1, GRAPH_LIMITS.MAX_PARTS, 'BOM Parts')
                }
                className={`w-full px-2 py-1 text-xs bg-white border rounded shadow-2xs outline-none ${
                  inputErrors.partCount ? 'border-red-400 bg-red-50/30' : 'border-slate-200 focus:border-blue-500'
                }`}
              />
              {inputErrors.partCount && (
                <span className="text-[9px] text-red-500 flex items-center gap-0.5 mt-0.5">
                  <AlertCircle className="w-2.5 h-2.5 shrink-0" />
                  {inputErrors.partCount}
                </span>
              )}
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-600 block mb-0.5">
                Products <span className="text-slate-400 font-normal">(1-20)</span>
              </label>
              <input
                type="number"
                min={GRAPH_LIMITS.MIN_COUNT}
                max={GRAPH_LIMITS.MAX_PRODUCTS}
                value={localProductCount}
                onChange={(e) =>
                  handleCountChange('productCount', e.target.value, setLocalProductCount, 1, GRAPH_LIMITS.MAX_PRODUCTS, 'Products')
                }
                className={`w-full px-2 py-1 text-xs bg-white border rounded shadow-2xs outline-none ${
                  inputErrors.productCount ? 'border-red-400 bg-red-50/30' : 'border-slate-200 focus:border-blue-500'
                }`}
              />
              {inputErrors.productCount && (
                <span className="text-[9px] text-red-500 flex items-center gap-0.5 mt-0.5">
                  <AlertCircle className="w-2.5 h-2.5 shrink-0" />
                  {inputErrors.productCount}
                </span>
              )}
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-600 block mb-0.5">
                Orders <span className="text-slate-400 font-normal">(1-100)</span>
              </label>
              <input
                type="number"
                min={GRAPH_LIMITS.MIN_COUNT}
                max={GRAPH_LIMITS.MAX_ORDERS}
                value={localOrderCount}
                onChange={(e) =>
                  handleCountChange('orderCount', e.target.value, setLocalOrderCount, 1, GRAPH_LIMITS.MAX_ORDERS, 'Orders')
                }
                className={`w-full px-2 py-1 text-xs bg-white border rounded shadow-2xs outline-none ${
                  inputErrors.orderCount ? 'border-red-400 bg-red-50/30' : 'border-slate-200 focus:border-blue-500'
                }`}
              />
              {inputErrors.orderCount && (
                <span className="text-[9px] text-red-500 flex items-center gap-0.5 mt-0.5">
                  <AlertCircle className="w-2.5 h-2.5 shrink-0" />
                  {inputErrors.orderCount}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Supplier selector */}
        <div className="space-y-1.5 relative">
          <label className="text-xs font-semibold text-slate-700 flex items-center">
            Select Supplier <span className="text-red-500 ml-0.5">*</span>
          </label>
          <button
            type="button"
            onClick={() => setSupplierDropdownOpen(!supplierDropdownOpen)}
            className="w-full flex items-center justify-between px-3 py-2 bg-white border border-slate-200 rounded-md shadow-xs text-xs font-medium text-slate-800 hover:border-slate-300 transition-colors"
          >
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 rounded bg-red-100 flex items-center justify-center text-red-600">
                <Factory className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold">{selectedSupplier}</span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {supplierDropdownOpen && (
            <div className="absolute left-0 right-0 top-[58px] z-30 bg-white border border-slate-200 rounded-md shadow-lg py-1 max-h-48 overflow-y-auto animate-in fade-in-50 duration-100">
              {availableSuppliers.map((supId) => (
                <button
                  key={supId}
                  onClick={() => {
                    dispatch(setSelectedSupplier(supId))
                    setSupplierDropdownOpen(false)
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2 text-xs text-left hover:bg-slate-50 transition-colors ${
                    selectedSupplier === supId ? 'bg-blue-50/60 font-semibold text-blue-700' : 'text-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Factory className="w-3.5 h-3.5 text-red-500" />
                    <span>{supId}</span>
                  </div>
                  {selectedSupplier === supId && <Check className="w-3.5 h-3.5 text-blue-600" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Trace direction */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-700">Trace Type</label>
          <div className="grid grid-cols-2 gap-1 p-0.5 bg-slate-100/90 rounded-md border border-slate-200/80">
            {(['downstream', 'upstream'] as TraceDirection[]).map((direction) => {
              const active = traceDirection === direction
              return (
                <button
                  key={direction}
                  type="button"
                  onClick={() => dispatch(setTraceDirection(direction))}
                  className={`py-1.5 text-xs font-semibold rounded capitalize transition-all duration-150 ${
                    active
                      ? 'bg-white text-blue-600 shadow-xs border border-blue-200'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {direction}
                </button>
              )
            })}
          </div>
        </div>

        {/* Highlight depth */}
        <div className="space-y-1 relative">
          <label className="text-xs font-semibold text-slate-700">
            Highlight Depth (Optional)
          </label>
          <button
            type="button"
            onClick={() => setDepthDropdownOpen(!depthDropdownOpen)}
            className="w-full flex items-center justify-between px-3 py-2 bg-white border border-slate-200 rounded-md shadow-xs text-xs text-slate-800 hover:border-slate-300 transition-colors"
          >
            <span className="font-medium">{depthLabels[highlightDepth]}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>
          <p className="text-[10px] text-slate-400 italic">
            e.g., 1 = direct parts, 2 = parts + products
          </p>

          {depthDropdownOpen && (
            <div className="absolute left-0 right-0 top-[54px] z-30 bg-white border border-slate-200 rounded-md shadow-lg py-1 animate-in fade-in-50 duration-100">
              {(['all', 'direct', 'parts_products'] as HighlightDepth[]).map((depth) => (
                <button
                  key={depth}
                  onClick={() => {
                    dispatch(setHighlightDepth(depth))
                    setDepthDropdownOpen(false)
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2 text-xs text-left hover:bg-slate-50 transition-colors ${
                    highlightDepth === depth ? 'bg-blue-50/60 font-semibold text-blue-700' : 'text-slate-700'
                  }`}
                >
                  <span>{depthLabels[depth]}</span>
                  {highlightDepth === depth && <Check className="w-3.5 h-3.5 text-blue-600" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Node category filters */}
        <div className="space-y-1.5 relative">
          <label className="text-xs font-semibold text-slate-700">
            Node Filter (Optional)
          </label>
          <div
            onClick={() => setFilterDropdownOpen(!filterDropdownOpen)}
            className="w-full min-h-[36px] p-1.5 bg-white border border-slate-200 rounded-md shadow-xs flex flex-wrap gap-1 items-center cursor-pointer hover:border-slate-300 transition-colors"
          >
            {filterOptions.map((opt) => {
              const isIncluded = nodeFilters.includes(opt.value)
              if (!isIncluded) return null
              return (
                <span
                  key={opt.value}
                  className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-[10px] font-medium text-slate-700"
                  onClick={(e) => {
                    e.stopPropagation()
                    dispatch(toggleNodeFilter(opt.value))
                  }}
                >
                  {opt.label}
                  <span className="text-slate-400 hover:text-slate-600">✕</span>
                </span>
              )
            })}
            <div className="ml-auto pr-1">
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </div>
          </div>

          {filterDropdownOpen && (
            <div className="absolute left-0 right-0 top-[58px] z-30 bg-white border border-slate-200 rounded-md shadow-lg py-1 animate-in fade-in-50 duration-100">
              {filterOptions.map((opt) => {
                const isSelected = nodeFilters.includes(opt.value)
                return (
                  <button
                    key={opt.value}
                    onClick={() => dispatch(toggleNodeFilter(opt.value))}
                    className="w-full flex items-center justify-between px-3 py-1.5 text-xs text-left hover:bg-slate-50 transition-colors text-slate-700"
                  >
                    <span>{opt.label}</span>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      readOnly
                      className="rounded text-blue-600 focus:ring-0"
                    />
                  </button>
                )
              })}
            </div>
          )}
        </div>

        {/* Unaffected nodes toggle */}
        <div className="flex items-center justify-between pt-0.5">
          <span className="text-xs font-semibold text-slate-700">
            Show Unaffected Nodes
          </span>
          <button
            type="button"
            role="switch"
            aria-checked={showUnaffected}
            onClick={() => dispatch(setShowUnaffected(!showUnaffected))}
            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
              showUnaffected ? 'bg-blue-600' : 'bg-slate-200'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                showUnaffected ? 'translate-x-4' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        <button
          type="button"
          onClick={handleGenerateClick}
          className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold text-xs rounded-md shadow-xs flex items-center justify-center gap-2 transition-colors cursor-pointer"
        >
          <Play className="w-3.5 h-3.5 fill-white" />
          <span>Generate Graph</span>
        </button>

        <div className="pt-2 space-y-1.5 border-t border-slate-100">
          <h3 className="text-xs font-bold text-slate-900 tracking-tight">
            Quick Actions
          </h3>

          <div className="space-y-0.5">
            <button
              onClick={handleResetView}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>Reset View</span>
            </button>

            <button
              onClick={handleResetView}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
            >
              <Maximize className="w-3.5 h-3.5 text-slate-500" />
              <span>Fit to Screen</span>
            </button>

            <button
              onClick={handleDownloadPng}
              disabled={isExportingPng}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-100 rounded-md transition-colors disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              <span>{isExportingPng ? 'Exporting...' : 'Download Graph (PNG)'}</span>
            </button>

            <button
              onClick={handleExportCsv}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-slate-500" />
              <span>Export Data (CSV)</span>
            </button>
          </div>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-100 text-[10px] text-slate-400 text-center">
        Sprint 1 • Team PHOTON
      </div>
    </aside>
  )
}
