import React, { memo } from 'react'
import { Handle, Position, NodeProps } from '@xyflow/react'
import { Factory, Package, Box, FileText } from 'lucide-react'
import { GraphNodeData } from '@/types'

export interface ExtendedGraphNodeData extends GraphNodeData {
  isHovered?: boolean
  isHoverConnected?: boolean
  isHoverDimmed?: boolean
}

const CustomNodeComponent: React.FC<NodeProps> = ({ id, data, selected }) => {
  const nodeData = data as unknown as ExtendedGraphNodeData
  const { type, label, isAffected, isSource, isHovered, isHoverConnected, isHoverDimmed } = nodeData

  const renderIcon = () => {
    const isColored = isHoverConnected || (isAffected && !isHoverDimmed)
    const iconClass = isColored ? 'w-4 h-4 text-white' : 'w-4 h-4 text-slate-500'
    switch (type) {
      case 'SUPPLIER':
        return <Factory className={iconClass} />
      case 'BOM_PART':
        return <Package className={iconClass} />
      case 'FINISHED_PRODUCT':
        return <Box className={iconClass} />
      case 'CUSTOMER_ORDER':
        return <FileText className={iconClass} />
      default:
        return <Box className={iconClass} />
    }
  }

  let badgeBg = 'bg-slate-200 border-slate-300 text-slate-500'
  let ringStyle = ''
  let opacityStyle = 'opacity-100'

  if (isHoverDimmed) {
    opacityStyle = 'opacity-25'
    badgeBg = 'bg-slate-200 border-slate-300 text-slate-400'
  } else if (isHovered) {
    opacityStyle = 'opacity-100'
    ringStyle = 'ring-4 ring-blue-400 ring-offset-2 shadow-lg scale-105'
    switch (type) {
      case 'SUPPLIER':
        badgeBg = 'bg-red-500 border-red-400 text-white'
        break
      case 'BOM_PART':
        badgeBg = 'bg-amber-500 border-amber-400 text-white'
        break
      case 'FINISHED_PRODUCT':
        badgeBg = 'bg-teal-600 border-teal-500 text-white'
        break
      case 'CUSTOMER_ORDER':
        badgeBg = 'bg-blue-600 border-blue-500 text-white'
        break
    }
  } else if (isHoverConnected) {
    opacityStyle = 'opacity-100'
    ringStyle = 'ring-3 ring-blue-200 shadow-sm'
    switch (type) {
      case 'SUPPLIER':
        badgeBg = 'bg-red-500 border-red-400 text-white'
        break
      case 'BOM_PART':
        badgeBg = 'bg-amber-500 border-amber-400 text-white'
        break
      case 'FINISHED_PRODUCT':
        badgeBg = 'bg-teal-600 border-teal-500 text-white'
        break
      case 'CUSTOMER_ORDER':
        badgeBg = 'bg-blue-600 border-blue-500 text-white'
        break
    }
  } else if (isAffected) {
    switch (type) {
      case 'SUPPLIER':
        badgeBg = 'bg-red-500 border-red-400 text-white shadow-md'
        ringStyle = isSource ? 'ring-4 ring-red-200 node-pulse-supplier' : 'ring-2 ring-red-200'
        break
      case 'BOM_PART':
        badgeBg = 'bg-amber-500 border-amber-400 text-white shadow-md'
        ringStyle = 'ring-3 ring-amber-200'
        break
      case 'FINISHED_PRODUCT':
        badgeBg = 'bg-teal-600 border-teal-500 text-white shadow-md'
        ringStyle = 'ring-4 ring-teal-200 node-pulse-product'
        break
      case 'CUSTOMER_ORDER':
        badgeBg = 'bg-blue-600 border-blue-500 text-white shadow-md'
        ringStyle = 'ring-2 ring-blue-200'
        break
    }
  }

  const selectedOutline = selected && !isHoverDimmed ? 'ring-2 ring-offset-2 ring-blue-600' : ''

  // Suppliers and Products place labels underneath; BOM Parts and Orders place labels to the right
  const isLabelUnder = type === 'SUPPLIER' || type === 'FINISHED_PRODUCT'

  return (
    <div
      className={`relative group flex items-center cursor-pointer select-none transition-all duration-200 ${opacityStyle} ${
        isLabelUnder ? 'flex-col justify-center' : 'flex-row gap-2.5'
      }`}
      title={`${id} (${type})`}
      tabIndex={0}
      role="button"
      aria-label={`${id} ${type}`}
      onFocus={() => (nodeData as any)?.onNodeFocus?.(id)}
      onBlur={() => (nodeData as any)?.onNodeBlur?.()}
    >
      {type !== 'SUPPLIER' && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-2 !h-2 !bg-transparent !border-none !min-w-0"
          style={{ left: isLabelUnder ? '50%' : 0, transform: isLabelUnder ? 'translateX(-50%)' : 'none' }}
        />
      )}

      <div
        className={`w-9 h-9 rounded-full flex items-center justify-center border transition-all duration-200 ${badgeBg} ${ringStyle} ${selectedOutline}`}
      >
        {renderIcon()}
      </div>

      <div
        className={`text-[11px] font-semibold tracking-tight transition-colors whitespace-nowrap ${
          isLabelUnder ? 'mt-1.5 text-center' : ''
        } ${
          isHoverConnected || (isAffected && !isHoverDimmed) ? 'text-slate-900 font-bold' : 'text-slate-600'
        } ${selected ? 'text-blue-700 underline underline-offset-2' : ''}`}
      >
        {label}
      </div>

      {type !== 'CUSTOMER_ORDER' && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-2 !h-2 !bg-transparent !border-none !min-w-0"
          style={{ right: isLabelUnder ? '50%' : 0, transform: isLabelUnder ? 'translateX(50%)' : 'none' }}
        />
      )}
    </div>
  )
}

export const CustomNode = memo(CustomNodeComponent)
