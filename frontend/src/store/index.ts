import { configureStore } from '@reduxjs/toolkit'
import graphUiReducer from './slices/graphUiSlice'
import graphViewReducer from './slices/graphViewSlice'

export const store = configureStore({
  reducer: {
    graphUi: graphUiReducer,
    graphView: graphViewReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
