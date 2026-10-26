import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { EntityType, TraceDirection, HighlightDepth } from '@/types'
import { GraphGenerationParams, DEFAULT_GRAPH_PARAMS, GRAPH_LIMITS } from '@/types/graph.types'

export interface GraphUiState {
  // Dynamic generation parameters
  supplierCount: number
  partCount: number
  productCount: number
  orderCount: number
  inputErrors: Record<string, string>
  availableSuppliers: string[]

  // Selection & filtering state
  selectedSupplier: string
  selectedNodeId: string | null
  traceDirection: TraceDirection
  highlightDepth: HighlightDepth
  nodeFilters: EntityType[]
  showUnaffected: boolean
  isSimulating: boolean
}

const initialState: GraphUiState = {
  supplierCount: DEFAULT_GRAPH_PARAMS.supplierCount,
  partCount: DEFAULT_GRAPH_PARAMS.partCount,
  productCount: DEFAULT_GRAPH_PARAMS.productCount,
  orderCount: DEFAULT_GRAPH_PARAMS.orderCount,
  inputErrors: {},
  availableSuppliers: ['SUP-01', 'SUP-02'],

  selectedSupplier: 'SUP-01',
  selectedNodeId: 'SUP-01',
  traceDirection: 'downstream',
  highlightDepth: 'all',
  nodeFilters: ['SUPPLIER', 'BOM_PART', 'FINISHED_PRODUCT', 'CUSTOMER_ORDER'],
  showUnaffected: true,
  isSimulating: false,
}

export const graphUiSlice = createSlice({
  name: 'graphUi',
  initialState,
  reducers: {
    setGraphCount: (
      state,
      action: PayloadAction<{ field: keyof GraphGenerationParams; value: number }>
    ) => {
      const { field, value } = action.payload
      state[field] = value

      // Clear inline error on change
      if (state.inputErrors[field]) {
        delete state.inputErrors[field]
      }
    },
    setInputErrors: (state, action: PayloadAction<Record<string, string>>) => {
      state.inputErrors = action.payload
    },
    setAvailableSuppliers: (state, action: PayloadAction<string[]>) => {
      state.availableSuppliers = action.payload
      if (!action.payload.includes(state.selectedSupplier)) {
        state.selectedSupplier = action.payload[0] || 'SUP-01'
        state.selectedNodeId = state.selectedSupplier
      }
    },
    setSelectedSupplier: (state, action: PayloadAction<string>) => {
      state.selectedSupplier = action.payload
      state.selectedNodeId = action.payload
    },
    setSelectedNodeId: (state, action: PayloadAction<string | null>) => {
      state.selectedNodeId = action.payload
    },
    setTraceDirection: (state, action: PayloadAction<TraceDirection>) => {
      state.traceDirection = action.payload
    },
    setHighlightDepth: (state, action: PayloadAction<HighlightDepth>) => {
      state.highlightDepth = action.payload
    },
    setNodeFilters: (state, action: PayloadAction<EntityType[]>) => {
      state.nodeFilters = action.payload
    },
    toggleNodeFilter: (state, action: PayloadAction<EntityType>) => {
      const type = action.payload
      if (state.nodeFilters.includes(type)) {
        state.nodeFilters = state.nodeFilters.filter((f) => f !== type)
      } else {
        state.nodeFilters.push(type)
      }
    },
    setShowUnaffected: (state, action: PayloadAction<boolean>) => {
      state.showUnaffected = action.payload
    },
    setIsSimulating: (state, action: PayloadAction<boolean>) => {
      state.isSimulating = action.payload
    },
    resetUiState: (state) => {
      state.supplierCount = DEFAULT_GRAPH_PARAMS.supplierCount
      state.partCount = DEFAULT_GRAPH_PARAMS.partCount
      state.productCount = DEFAULT_GRAPH_PARAMS.productCount
      state.orderCount = DEFAULT_GRAPH_PARAMS.orderCount
      state.inputErrors = {}
      state.availableSuppliers = ['SUP-01', 'SUP-02']

      state.selectedSupplier = 'SUP-01'
      state.selectedNodeId = 'SUP-01'
      state.traceDirection = 'downstream'
      state.highlightDepth = 'all'
      state.nodeFilters = ['SUPPLIER', 'BOM_PART', 'FINISHED_PRODUCT', 'CUSTOMER_ORDER']
      state.showUnaffected = true
      state.isSimulating = false
    },
  },
})

export const {
  setGraphCount,
  setInputErrors,
  setAvailableSuppliers,
  setSelectedSupplier,
  setSelectedNodeId,
  setTraceDirection,
  setHighlightDepth,
  setNodeFilters,
  toggleNodeFilter,
  setShowUnaffected,
  setIsSimulating,
  resetUiState,
} = graphUiSlice.actions

export default graphUiSlice.reducer
