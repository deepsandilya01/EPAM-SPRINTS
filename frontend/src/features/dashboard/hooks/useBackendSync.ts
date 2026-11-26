"use client";

import { useCallback, useEffect } from "react";

import {
  fetchBackendHealthThunk,
  fetchSupplyChainGraphThunk,
} from "@/features/dashboard/slices/dashboardSlice";
import { useAppDispatch, useAppSelector } from "@/store";

export function useBackendSync() {
  const dispatch = useAppDispatch();
  const dashboard = useAppSelector((state) => state.dashboard);

  const refreshBackendData = useCallback(() => {
    void dispatch(fetchBackendHealthThunk());
    void dispatch(fetchSupplyChainGraphThunk());
  }, [dispatch]);

  useEffect(() => {
    if (dashboard.nodes.length === 0 && !dashboard.graphLoading && !dashboard.graphError) {
      refreshBackendData();
    } else if (dashboard.connectionStatus === "checking" && !dashboard.health) {
      void dispatch(fetchBackendHealthThunk());
    }
  }, [
    dashboard.connectionStatus,
    dashboard.graphError,
    dashboard.graphLoading,
    dashboard.health,
    dashboard.nodes.length,
    dispatch,
    refreshBackendData,
  ]);

  return {
    ...dashboard,
    refreshBackendData,
  };
}

