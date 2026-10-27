import React from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setSelectedNodeId } from '@/store/slices/graphUiSlice'
import { CustomerOrder } from '@/types'

interface ReachableOrdersProps {
  orders: CustomerOrder[]
  reachableOrderIds: string[]
}

export const ReachableOrders: React.FC<ReachableOrdersProps> = ({
  orders,
  reachableOrderIds,
}) => {
  const dispatch = useAppDispatch()
  const { selectedNodeId } = useAppSelector((state) => state.graphUi)
  const reachableSet = new Set(reachableOrderIds)

  const handleSelectOrder = (orderId: string) => {
    dispatch(setSelectedNodeId(orderId))
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-xs w-[340px] shrink-0 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="text-xs font-bold text-slate-900 tracking-tight">
            Reachable Customer Orders ({reachableOrderIds.length})
          </h3>
          <span className="text-[10px] text-slate-400">
            {reachableOrderIds.length} of {orders.length} affected
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2 pt-3">
          {orders.map((order) => {
            const isReachable = reachableSet.has(order.id)
            const isSelected = selectedNodeId === order.id

            return (
              <button
                key={order.id}
                onClick={() => handleSelectOrder(order.id)}
                className={`py-1.5 px-2.5 rounded-full text-xs font-semibold tracking-tight transition-all text-center select-none cursor-pointer ${
                  isReachable
                    ? 'bg-blue-100 hover:bg-blue-200 text-blue-700 border border-blue-300 shadow-xs'
                    : 'bg-slate-50 hover:bg-slate-100 text-slate-400 border border-slate-200'
                } ${isSelected ? 'ring-2 ring-blue-600 ring-offset-1 font-bold' : ''}`}
                title={`${order.id}: ${order.customerName} (${isReachable ? 'Affected' : 'Unaffected'})`}
              >
                {order.id}
              </button>
            )
          })}
        </div>
      </div>

      <div className="pt-3 text-[10px] text-slate-400 text-center border-t border-slate-100">
        Click any order pill to inspect node details & fulfillment timeline
      </div>
    </div>
  )
}
