import React from 'react'
import { Factory, Package, Box, FileText } from 'lucide-react'
import { ScenarioGraph } from '@/types'

interface SummaryCardsProps {
  graph: ScenarioGraph
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ graph }) => {
  const supplierCount = graph.suppliers.length
  const partCount = graph.parts.length
  const productCount = graph.products.length
  const orderCount = graph.orders.length

  const cards = [
    {
      title: 'Suppliers',
      count: supplierCount,
      subtext: 'total nodes',
      textColor: 'text-red-500',
      bgColor: 'bg-[#fff5f5]',
      borderColor: 'border-red-100/80',
      badgeBg: 'bg-red-500',
      icon: <Factory className="w-5 h-5 text-white" />,
    },
    {
      title: 'BOM Parts',
      count: partCount,
      subtext: 'total nodes',
      textColor: 'text-amber-500',
      bgColor: 'bg-[#fffbeb]',
      borderColor: 'border-amber-100/80',
      badgeBg: 'bg-amber-500',
      icon: <Package className="w-5 h-5 text-white" />,
    },
    {
      title: 'Finished Products',
      count: productCount,
      subtext: 'total nodes',
      textColor: 'text-teal-600',
      bgColor: 'bg-[#f0fdfa]',
      borderColor: 'border-teal-100/80',
      badgeBg: 'bg-teal-600',
      icon: <Box className="w-5 h-5 text-white" />,
    },
    {
      title: 'Customer Orders',
      count: orderCount,
      subtext: 'total nodes',
      textColor: 'text-blue-600',
      bgColor: 'bg-[#eff6ff]',
      borderColor: 'border-blue-100/80',
      badgeBg: 'bg-blue-600',
      icon: <FileText className="w-5 h-5 text-white" />,
    },
  ]

  return (
    <div className="grid grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className={`flex items-center gap-3.5 p-3.5 rounded-lg border shadow-xs transition-transform hover:-translate-y-0.5 duration-150 ${card.bgColor} ${card.borderColor}`}
        >
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 shadow-xs ${card.badgeBg}`}
          >
            {card.icon}
          </div>

          <div>
            <div className={`text-xs font-semibold tracking-tight ${card.textColor}`}>
              {card.title}
            </div>
            <div className="text-xl font-bold text-slate-900 leading-tight">
              {card.count}
            </div>
            <div className="text-[11px] text-slate-500 font-normal">
              {card.subtext}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
