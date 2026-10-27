import React, { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ReactFlow,
  Node,
  Edge,
  MarkerType,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
} from '@xyflow/react'
import {
  Search,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  X,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setSelectedNodeId } from '@/store/slices/graphUiSlice'
import { setIsFullscreen } from '@/store/slices/graphViewSlice'
import { CustomNode } from './CustomNode'
import { CustomEdge } from './CustomEdge'
import { ScenarioGraph, TraversalResult, EntityType } from '@/types'
import { computeGraphLayout } from '@/lib/graph/layoutGraph'
import { getConnectedSupplyChainPaths } from '@/lib/graph/traverseGraph'

interface GraphCanvasProps {
  graph: ScenarioGraph
  traversalResult: TraversalResult
  onSelectEdge?: (edgeId: string | null) => void
}

const nodeTypes = {
  customNode: CustomNode,
}

const edgeTypes = {
  customEdge: CustomEdge,
}

const GraphCanvasInner: React.FC<GraphCanvasProps> = ({
  graph,
  traversalResult,
  onSelectEdge,
}) => {
  const dispatch = useAppDispatch()
  const { selectedNodeId, showUnaffected, nodeFilters } = useAppSelector(
    (state) => state.graphUi
  )
  const { isFullscreen, viewResetCounter } = useAppSelector((state) => state.graphView)

  const { fitView, zoomIn, zoomOut, getZoom } = useReactFlow()
  const [zoomPercent, setZoomPercent] = useState<number>(100)
  const [searchOpen, setSearchOpen] = useState<boolean>(false)
  const [searchTerm, setSearchTerm] = useState<string>('')

  // Hover state for interactive path highlighting
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null)
  const [hoverTooltipPos, setHoverTooltipPos] = useState<{ x: number; y: number } | null>(null)

  const hoverPathInfo = useMemo(() => {
    return getConnectedSupplyChainPaths(graph, hoveredNodeId)
  }, [graph, hoveredNodeId])

  const connectedNodesSet = useMemo(() => {
    return new Set(hoverPathInfo.connectedNodeIds)
  }, [hoverPathInfo.connectedNodeIds])

  const connectedEdgesSet = useMemo(() => {
    return new Set(hoverPathInfo.connectedEdgeIds)
  }, [hoverPathInfo.connectedEdgeIds])

  const reachedSet = useMemo(() => {
    return new Set(traversalResult.allReachedNodeIds)
  }, [traversalResult.allReachedNodeIds])

  const traversedEdgeSet = useMemo(() => {
    return new Set(traversalResult.traversedEdgeIds)
  }, [traversalResult.traversedEdgeIds])

  const nodeCoordinates = useMemo(() => {
    return computeGraphLayout(graph.suppliers, graph.parts, graph.products, graph.orders)
  }, [graph.suppliers, graph.parts, graph.products, graph.orders])

  // Focus handlers for keyboard accessibility
  const handleNodeFocus = useCallback(
    (nodeId: string) => {
      setHoveredNodeId(nodeId)
      const coords = nodeCoordinates[nodeId]
      if (coords) {
        setHoverTooltipPos({ x: coords.x + 40, y: coords.y })
      }
    },
    [nodeCoordinates]
  )

  const handleNodeBlur = useCallback(() => {
    setHoveredNodeId(null)
    setHoverTooltipPos(null)
  }, [])

  const computedNodes: Node[] = useMemo(() => {
    const isHoverActive = hoveredNodeId !== null

    return graph.nodes
      .filter((n) => {
        if (!nodeFilters.includes(n.type as EntityType)) {
          return false
        }
        const isAffected = reachedSet.has(n.id) || n.id === traversalResult.sourceNodeId
        if (!showUnaffected && !isAffected) {
          return false
        }
        if (searchTerm.trim()) {
          const match =
            n.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            ('name' in n.details && n.details.name.toLowerCase().includes(searchTerm.toLowerCase()))
          return match
        }
        return true
      })
      .map((n) => {
        const isAffected = reachedSet.has(n.id) || n.id === traversalResult.sourceNodeId
        const isSource = n.id === traversalResult.sourceNodeId
        const coords = nodeCoordinates[n.id] || { x: 100, y: 100 }

        const isHovered = hoveredNodeId === n.id
        const isHoverConnected = isHoverActive && connectedNodesSet.has(n.id)
        const isHoverDimmed = isHoverActive && !connectedNodesSet.has(n.id)

        return {
          id: n.id,
          type: 'customNode',
          position: coords,
          selected: selectedNodeId === n.id,
          data: {
            ...n,
            isAffected,
            isSource,
            isHovered,
            isHoverConnected,
            isHoverDimmed,
            onNodeFocus: handleNodeFocus,
            onNodeBlur: handleNodeBlur,
          },
        }
      })
  }, [
    graph.nodes,
    reachedSet,
    traversalResult.sourceNodeId,
    nodeFilters,
    showUnaffected,
    searchTerm,
    selectedNodeId,
    nodeCoordinates,
    hoveredNodeId,
    connectedNodesSet,
  ])

  const visibleNodeIdSet = useMemo(() => {
    return new Set(computedNodes.map((n) => n.id))
  }, [computedNodes])

  const computedEdges: Edge[] = useMemo(() => {
    const isHoverActive = hoveredNodeId !== null

    return graph.edges
      .filter((edge) => {
        if (!visibleNodeIdSet.has(edge.source) || !visibleNodeIdSet.has(edge.target)) {
          return false
        }
        if (!showUnaffected && !traversedEdgeSet.has(edge.id)) {
          return false
        }
        return true
      })
      .map((edge) => {
        const isAffected = traversedEdgeSet.has(edge.id)
        const isHoverHighlighted = isHoverActive && connectedEdgesSet.has(edge.id)
        const isHoverDimmed = isHoverActive && !connectedEdgesSet.has(edge.id)

        let arrowColor = '#cbd5e1'
        if (isHoverHighlighted) {
          if (edge.relation === 'SUPPLIES') arrowColor = '#ef4444'
          else if (edge.relation === 'USED_IN') arrowColor = '#f59e0b'
          else if (edge.relation === 'FULFILLS') arrowColor = '#2563eb'
        } else if (!isHoverDimmed && isAffected) {
          if (edge.relation === 'SUPPLIES') arrowColor = '#ef4444'
          else if (edge.relation === 'USED_IN') arrowColor = '#f59e0b'
          else if (edge.relation === 'FULFILLS') arrowColor = '#2563eb'
        }

        return {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: 'customEdge',
          data: {
            relation: edge.relation,
            isAffected,
            isHoverHighlighted,
            isHoverDimmed,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 14,
            height: 14,
            color: arrowColor,
          },
        }
      })
  }, [graph.edges, visibleNodeIdSet, showUnaffected, traversedEdgeSet, hoveredNodeId, connectedEdgesSet])

  const [nodes, setNodes, onNodesChange] = useNodesState(computedNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(computedEdges)

  useEffect(() => {
    setNodes(computedNodes)
  }, [computedNodes, setNodes])

  useEffect(() => {
    setEdges(computedEdges)
  }, [computedEdges, setEdges])

  // Auto-fit viewport whenever topology changes or view reset is triggered
  useEffect(() => {
    fitView({ padding: 0.18, duration: 450 })
    setZoomPercent(100)
  }, [viewResetCounter, graph.nodes.length, fitView])

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      dispatch(setSelectedNodeId(node.id))
      onSelectEdge?.(null)
    },
    [dispatch, onSelectEdge]
  )

  const handleNodeMouseEnter = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setHoveredNodeId(node.id)
      const containerRect = document.getElementById('graph-canvas-container')?.getBoundingClientRect()
      if (containerRect) {
        setHoverTooltipPos({
          x: event.clientX - containerRect.left,
          y: event.clientY - containerRect.top,
        })
      }
    },
    []
  )

  const handleNodeMouseLeave = useCallback(() => {
    setHoveredNodeId(null)
    setHoverTooltipPos(null)
  }, [])

  const handleEdgeClick = useCallback(
    (_: React.MouseEvent, edge: Edge) => {
      onSelectEdge?.(edge.id)
    },
    [onSelectEdge]
  )

  const handleZoomIn = () => {
    zoomIn({ duration: 300 })
    setTimeout(() => setZoomPercent(Math.round(getZoom() * 100)), 350)
  }

  const handleZoomOut = () => {
    zoomOut({ duration: 300 })
    setTimeout(() => setZoomPercent(Math.round(getZoom() * 100)), 350)
  }

  const handleFitView = () => {
    fitView({ padding: 0.15, duration: 400 })
    setTimeout(() => setZoomPercent(Math.round(getZoom() * 100)), 450)
  }

  const toggleFullscreen = () => {
    dispatch(setIsFullscreen(!isFullscreen))
  }

  const hoveredNode = hoveredNodeId ? graph.nodes.find((n) => n.id === hoveredNodeId) : null

  return (
    <div
      id="graph-canvas-container"
      className={`relative w-full bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden transition-all duration-300 ${
        isFullscreen ? 'fixed inset-4 z-50 shadow-2xl' : 'h-[540px]'
      }`}
    >
      {/* Floating controls toolbar */}
      <div className="export-ignore absolute top-3 right-3 z-20 flex items-center bg-white/95 backdrop-blur-sm border border-slate-200 rounded-md shadow-xs px-1.5 py-1 text-slate-600 text-xs gap-1 select-none">
        {searchOpen ? (
          <div className="flex items-center gap-1.5 pl-1 pr-1 bg-slate-50 rounded border border-slate-200">
            <Search className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search node..."
              className="w-28 text-xs outline-none bg-transparent text-slate-800 placeholder-slate-400"
              autoFocus
            />
            <button
              onClick={() => {
                setSearchTerm('')
                setSearchOpen(false)
              }}
              className="p-0.5 text-slate-400 hover:text-slate-600"
              title="Close search"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => setSearchOpen(true)}
            className={`p-1.5 rounded hover:bg-slate-100 hover:text-slate-900 transition-colors ${
              searchTerm ? 'text-blue-600 bg-blue-50' : ''
            }`}
            title="Search nodes"
            aria-label="Search nodes"
          >
            <Search className="w-3.5 h-3.5" />
          </button>
        )}

        <div className="h-4 w-[1px] bg-slate-200 mx-0.5" />

        <button
          onClick={handleZoomOut}
          className="p-1.5 rounded hover:bg-slate-100 hover:text-slate-900 transition-colors"
          title="Zoom out"
          aria-label="Zoom out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>

        <span className="px-1 font-mono text-[11px] text-slate-700 min-w-[36px] text-center">
          {zoomPercent}%
        </span>

        <button
          onClick={handleZoomIn}
          className="p-1.5 rounded hover:bg-slate-100 hover:text-slate-900 transition-colors"
          title="Zoom in"
          aria-label="Zoom in"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>

        <div className="h-4 w-[1px] bg-slate-200 mx-0.5" />

        <button
          onClick={handleFitView}
          className="px-2 py-1 rounded hover:bg-slate-100 hover:text-slate-900 font-medium transition-colors"
          title="Fit view to graph"
        >
          Fit View
        </button>

        <div className="h-4 w-[1px] bg-slate-200 mx-0.5" />

        <button
          onClick={toggleFullscreen}
          className="p-1.5 rounded hover:bg-slate-100 hover:text-slate-900 transition-colors"
          title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          aria-label={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
        >
          {isFullscreen ? (
            <Minimize2 className="w-3.5 h-3.5" />
          ) : (
            <Maximize2 className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Category column headers */}
      <div className="absolute top-[56px] left-0 right-0 pointer-events-none z-10 grid grid-cols-4 px-6 text-xs font-semibold select-none">
        <div className="text-center text-red-500 font-semibold tracking-wide">
          Suppliers ({graph.suppliers.length})
        </div>
        <div className="text-center text-amber-500 font-semibold tracking-wide">
          BOM Parts ({graph.parts.length})
        </div>
        <div className="text-center text-teal-600 font-semibold tracking-wide">
          Finished Products ({graph.products.length})
        </div>
        <div className="text-center text-blue-600 font-semibold tracking-wide">
          Customer Orders ({graph.orders.length})
        </div>
      </div>

      {/* Column separator guidelines */}
      <div className="absolute inset-0 pointer-events-none z-0 grid grid-cols-4 px-6 pt-[84px]">
        <div className="border-r border-dashed border-slate-200/60 h-full" />
        <div className="border-r border-dashed border-slate-200/60 h-full" />
        <div className="border-r border-dashed border-slate-200/60 h-full" />
        <div className="h-full" />
      </div>

      {/* Hover tooltip */}
      {hoveredNode && hoverTooltipPos && (
        <div
          style={{
            left: `${Math.min(hoverTooltipPos.x + 18, 700)}px`,
            top: `${Math.max(20, Math.min(hoverTooltipPos.y - 45, 420))}px`,
          }}
          className="export-ignore absolute z-30 pointer-events-none bg-slate-900/95 text-white p-2.5 rounded-lg shadow-xl backdrop-blur-xs text-xs border border-slate-700/80 animate-in fade-in duration-150 min-w-[210px]"
        >
          <div className="flex items-center justify-between gap-2 border-b border-slate-700/80 pb-1.5 mb-1.5">
            <span className="font-bold text-white text-xs tracking-tight">{hoveredNode.id}</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
              {hoveredNode.type.replace('_', ' ')}
            </span>
          </div>

          <div className="space-y-1 text-[11px] text-slate-300">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <ArrowUpRight className="w-3 h-3 text-emerald-400" /> Direct Upstream:
              </span>
              <span className="font-semibold text-white">{hoverPathInfo.directUpstreamCount}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <ArrowDownRight className="w-3 h-3 text-blue-400" /> Direct Downstream:
              </span>
              <span className="font-semibold text-white">{hoverPathInfo.directDownstreamCount}</span>
            </div>
            <div className="flex items-center justify-between pt-1 border-t border-slate-800 text-[10px]">
              <span className="text-slate-400">Total Upstream Reachable:</span>
              <span className="font-bold text-emerald-400">{hoverPathInfo.totalUpstreamCount}</span>
            </div>
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-slate-400">Total Downstream Reachable:</span>
              <span className="font-bold text-blue-400">{hoverPathInfo.totalDownstreamCount}</span>
            </div>
          </div>
        </div>
      )}

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        onNodeMouseEnter={handleNodeMouseEnter}
        onNodeMouseLeave={handleNodeMouseLeave}
        onEdgeClick={handleEdgeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
        minZoom={0.2}
        maxZoom={2.5}
        defaultViewport={{ x: 20, y: 10, zoom: 0.95 }}
        proOptions={{ hideAttribution: true }}
      />
    </div>
  )
}

export const GraphCanvas: React.FC<GraphCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  )
}
