import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface GraphViewState {
  searchQuery: string
  zoomLevel: number
  isFullscreen: boolean
  viewResetCounter: number
}

const initialState: GraphViewState = {
  searchQuery: '',
  zoomLevel: 100,
  isFullscreen: false,
  viewResetCounter: 0,
}

export const graphViewSlice = createSlice({
  name: 'graphView',
  initialState,
  reducers: {
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload
    },
    setZoomLevel: (state, action: PayloadAction<number>) => {
      state.zoomLevel = Math.max(25, Math.min(200, action.payload))
    },
    setIsFullscreen: (state, action: PayloadAction<boolean>) => {
      state.isFullscreen = action.payload
    },
    triggerResetView: (state) => {
      state.viewResetCounter += 1
      state.zoomLevel = 100
    },
  },
})

export const {
  setSearchQuery,
  setZoomLevel,
  setIsFullscreen,
  triggerResetView,
} = graphViewSlice.actions

export default graphViewSlice.reducer
