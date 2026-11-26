"use client";

import type { ReactNode } from "react";
import { Provider } from "react-redux";

import { ErrorBoundary } from "@/features/shared/components/ErrorBoundary";
import { store } from "@/store";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <Provider store={store}>
      <ErrorBoundary>{children}</ErrorBoundary>
    </Provider>
  );
}
