"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    message: "",
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      message: error.message || "An unexpected rendering error occurred.",
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("RE:Flow ErrorBoundary caught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="m-6 rounded-md border border-status-breached-border bg-status-breached-bg p-6 text-status-breached">
          <h2 className="text-sm font-semibold uppercase tracking-wider">
            Application Rendering Error
          </h2>
          <p className="mt-2 text-xs">{this.state.message}</p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false, message: "" })}
            className="mt-4 rounded-sm border border-carbon-950 bg-carbon-950 px-3 py-1.5 text-xs font-medium text-white hover:bg-carbon-800"
          >
            Recover View
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

