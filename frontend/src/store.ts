import { configureStore } from "@reduxjs/toolkit";
import { useDispatch, useSelector, type TypedUseSelectorHook } from "react-redux";

import dashboardReducer from "@/features/dashboard/slices/dashboardSlice";
import simulationReducer from "@/features/simulation/slices/simulationSlice";

export const store = configureStore({
  reducer: {
    simulation: simulationReducer,
    dashboard: dashboardReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

