import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { store } from '@/store'
import { SummaryCards } from '@/components/dashboard/SummaryCards'
import { StepwiseTimingTable } from '@/components/dashboard/StepwiseTimingTable'
import { ReachableOrders } from '@/components/dashboard/ReachableOrders'
import { INITIAL_SCENARIO_GRAPH } from '@/mocks/graph'
import {
  setSelectedSupplier,
  toggleNodeFilter,
  setShowUnaffected,
  resetUiState,
} from '@/store/slices/graphUiSlice'
import { CANONICAL_ORDERS } from '@/mocks/scenario'

describe('UI Dashboard Components & Redux Store', () => {
  it('renders SummaryCards with exact category counts', () => {
    render(<SummaryCards graph={INITIAL_SCENARIO_GRAPH} />)

    expect(screen.getByText('Suppliers')).toBeInTheDocument()
    expect(screen.getByText('BOM Parts')).toBeInTheDocument()
    expect(screen.getByText('Finished Products')).toBeInTheDocument()
    expect(screen.getByText('Customer Orders')).toBeInTheDocument()

    // Counts: 2 suppliers, 5 parts, 2 products, 10 orders
    expect(screen.getAllByText('2').length).toBe(2) // 2 Suppliers and 2 Products
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  it('renders StepwiseTimingTable with step timings and cumulative latency', () => {
    const mockSteps = [
      {
        step: 1,
        fromNode: 'SUP-01',
        toNode: 'PART-01',
        relation: 'SUPPLIES' as const,
        traversalTimeMs: 0.8,
        cumulativeTimeMs: 0.8,
      },
      {
        step: 2,
        fromNode: 'PART-01',
        toNode: 'PROD-01',
        relation: 'USED_IN' as const,
        traversalTimeMs: 1.2,
        cumulativeTimeMs: 2.0,
      },
    ]

    render(<StepwiseTimingTable steps={mockSteps} sourceSupplier="SUP-01" />)

    expect(screen.getByText('SUP-01')).toBeInTheDocument()
    expect(screen.getAllByText('PART-01').length).toBe(2)
    expect(screen.getByText('PROD-01')).toBeInTheDocument()
    expect(screen.getByText('SUPPLIES')).toBeInTheDocument()
    expect(screen.getByText('USED_IN')).toBeInTheDocument()
    expect(screen.getByText('2.0')).toBeInTheDocument()
  })

  it('renders ReachableOrders with reachable blue pills for ORD-01 through ORD-06', () => {
    const reachableIds = ['ORD-01', 'ORD-02', 'ORD-03', 'ORD-04', 'ORD-05', 'ORD-06']

    render(
      <Provider store={store}>
        <ReachableOrders orders={CANONICAL_ORDERS} reachableOrderIds={reachableIds} />
      </Provider>
    )

    expect(screen.getByText('Reachable Customer Orders (6)')).toBeInTheDocument()
    expect(screen.getByText('ORD-01')).toBeInTheDocument()
    expect(screen.getByText('ORD-06')).toBeInTheDocument()
    expect(screen.getByText('ORD-07')).toBeInTheDocument()
  })

  it('updates Redux store on client actions and resets state', () => {
    store.dispatch(setSelectedSupplier('SUP-02'))
    expect(store.getState().graphUi.selectedSupplier).toBe('SUP-02')

    store.dispatch(toggleNodeFilter('BOM_PART'))
    expect(store.getState().graphUi.nodeFilters).not.toContain('BOM_PART')

    store.dispatch(setShowUnaffected(false))
    expect(store.getState().graphUi.showUnaffected).toBe(false)

    store.dispatch(resetUiState())
    expect(store.getState().graphUi.selectedSupplier).toBe('SUP-01')
    expect(store.getState().graphUi.showUnaffected).toBe(true)
    expect(store.getState().graphUi.nodeFilters).toContain('BOM_PART')
  })
})
