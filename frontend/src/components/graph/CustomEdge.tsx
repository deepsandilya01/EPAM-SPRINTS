import React, { memo } from 'react'
import {
  BaseEdge,
  EdgeProps,
  getBezierPath,
  EdgeLabelRenderer,
} from '@xyflow/react'
import { RelationType } from '@/types'

export interface CustomEdgeData {
  relation: RelationType
  isAffected: boolean
  isHoverHighlighted?: boolean
  isHoverDimmed?: boolean
}

const CustomEdgeComponent: React.FC<EdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
  selected,
}) => {
  const edgeData = data as unknown as CustomEdgeData | undefined
  const isAffected = edgeData?.isAffected ?? false
  const relation = edgeData?.relation ?? 'SUPPLIES'
  const isHoverHighlighted = edgeData?.isHoverHighlighted ?? false
  const isHoverDimmed = edgeData?.isHoverDimmed ?? false

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  let strokeColor = '#cbd5e1'
  let strokeWidth = 1.5
  let opacity = 1.0

  if (isHoverDimmed) {
    opacity = 0.2
    strokeColor = '#e2e8f0'
  } else if (isHoverHighlighted) {
    strokeWidth = 2.5
    opacity = 1.0
    switch (relation) {
      case 'SUPPLIES':
        strokeColor = '#ef4444'
        break
      case 'USED_IN':
        strokeColor = '#f59e0b'
        break
      case 'FULFILLS':
        strokeColor = '#2563eb'
        break
    }
  } else if (isAffected) {
    strokeWidth = 2
    switch (relation) {
      case 'SUPPLIES':
        strokeColor = '#ef4444'
        break
      case 'USED_IN':
        strokeColor = '#f59e0b'
        break
      case 'FULFILLS':
        strokeColor = '#2563eb'
        break
    }
  }

  if (selected) {
    strokeWidth = 3
    strokeColor = '#1d4ed8'
  }

  return (
    <>
      <g className={isHoverHighlighted ? 'edge-flow-active' : ''}>
        <BaseEdge
          id={id}
          path={edgePath}
          markerEnd={markerEnd}
          style={{
            ...style,
            stroke: strokeColor,
            strokeWidth,
            opacity,
            transition: 'stroke 0.2s ease, stroke-width 0.2s ease, opacity 0.2s ease',
          }}
        />
      </g>

      {/* Render relationship badge on highlighted hover paths */}
      {isHoverHighlighted && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'none',
            }}
            className={`px-1.5 py-0.5 rounded border text-[9px] font-mono font-bold shadow-xs z-20 select-none animate-in fade-in zoom-in-95 duration-150 ${
              relation === 'SUPPLIES'
                ? 'bg-red-50/95 border-red-200 text-red-600'
                : relation === 'USED_IN'
                ? 'bg-amber-50/95 border-amber-200 text-amber-700'
                : 'bg-blue-50/95 border-blue-200 text-blue-600'
            }`}
          >
            {relation}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  )
}

export const CustomEdge = memo(CustomEdgeComponent)
