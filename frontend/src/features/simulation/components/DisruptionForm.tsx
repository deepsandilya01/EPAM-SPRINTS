"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { AlertCircle, CheckCircle2, Loader2, Play, RotateCcw } from "lucide-react";
import { useForm } from "react-hook-form";

import {
  fetchBackendHealthThunk,
  resetGraphThunk,
} from "@/features/dashboard/slices/dashboardSlice";
import { Badge } from "@/features/shared/components/Badge";
import { Card, CardBody, CardHeader } from "@/features/shared/components/Card";
import {
  DEFAULT_BENCHMARK_REQUEST,
  SUPPORTED_DISRUPTION_TYPES,
  SUPPORTED_SUPPLIERS,
} from "@/features/shared/utils/constants";
import {
  disruptionFormSchema,
  type DisruptionFormValues,
} from "@/features/simulation/simulationSchema";
import {
  clearSimulationError,
  runDisruptionSimulationThunk,
  setSelectedDisruptionType,
  setSelectedSupplier,
  setValidating,
  setValidationFailed,
} from "@/features/simulation/slices/simulationSlice";
import { useAppDispatch, useAppSelector } from "@/store";

export function DisruptionForm() {
  const dispatch = useAppDispatch();
  const executionState = useAppSelector((state) => state.simulation.executionState);
  const error = useAppSelector((state) => state.simulation.error);
  const nodes = useAppSelector((state) => state.dashboard.nodes);

  const supplierOptions = SUPPORTED_SUPPLIERS.map((fallback) => {
    const graphNode = nodes.find((n) => n.id === fallback.id);
    if (graphNode && (graphNode.name || graphNode.label)) {
      const location = graphNode.location ? ` (${graphNode.location})` : "";
      return {
        id: fallback.id,
        label: `${fallback.id} — ${graphNode.name ?? graphNode.label}${location}`,
      };
    }
    return fallback;
  });

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<DisruptionFormValues>({
    resolver: zodResolver(disruptionFormSchema),
    mode: "onChange",
    defaultValues: {
      supplier_id: DEFAULT_BENCHMARK_REQUEST.supplier_id,
      disruption_type: DEFAULT_BENCHMARK_REQUEST.disruption_type,
      delay_duration_hours: DEFAULT_BENCHMARK_REQUEST.delay_duration_hours,
      description: DEFAULT_BENCHMARK_REQUEST.description,
    },
  });

  const watchedSupplier = watch("supplier_id");
  const watchedType = watch("disruption_type");

  useEffect(() => {
    if (watchedSupplier) {
      dispatch(setSelectedSupplier(watchedSupplier));
    }
  }, [dispatch, watchedSupplier]);

  useEffect(() => {
    if (watchedType) {
      dispatch(setSelectedDisruptionType(watchedType));
    }
  }, [dispatch, watchedType]);

  const isBusy =
    isSubmitting || executionState === "validating" || executionState === "running";

  const onValidSubmit = async (values: DisruptionFormValues) => {
    if (isBusy) return;

    const payload = {
      supplier_id: values.supplier_id,
      disruption_type: values.disruption_type,
      delay_duration_hours: Number(values.delay_duration_hours),
      description: values.description ?? "",
    };

    dispatch(setValidating(payload));
    const parsed = disruptionFormSchema.safeParse(payload);
    if (!parsed.success) {
      const msg = parsed.error.issues[0]?.message ?? "Invalid simulation input.";
      dispatch(setValidationFailed(msg));
      return;
    }

    await dispatch(runDisruptionSimulationThunk(payload));
  };

  const stateBadgeTone =
    executionState === "success"
      ? "feasible"
      : executionState === "failed"
        ? "breached"
        : executionState === "running" || executionState === "validating"
          ? "dark"
          : "neutral";

  return (
    <Card>
      <CardHeader
        title="Disruption Simulation Parameters"
        subtitle="Submit a Tier-1 disruption event to POST /api/v1/simulation/disrupt"
        action={<Badge tone={stateBadgeTone}>State: {executionState}</Badge>}
      />
      <CardBody>
        <form onSubmit={handleSubmit(onValidSubmit)} noValidate className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <label
                htmlFor="supplier_id"
                className="mb-1.5 block text-xs font-medium text-ink"
              >
                Supplier ID <span className="text-status-breached">*</span>
              </label>
              <select
                id="supplier_id"
                disabled={isBusy}
                {...register("supplier_id")}
                className="w-full rounded-sm border border-hairline bg-surface px-3 py-2 text-xs text-ink focus:border-carbon-950 focus:outline-none focus:ring-1 focus:ring-carbon-950 disabled:cursor-not-allowed disabled:bg-canvas"
              >
                {supplierOptions.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
              {errors.supplier_id ? (
                <p className="mt-1 text-[11px] text-status-breached">
                  {errors.supplier_id.message}
                </p>
              ) : null}
            </div>

            <div>
              <label
                htmlFor="disruption_type"
                className="mb-1.5 block text-xs font-medium text-ink"
              >
                Disruption Type <span className="text-status-breached">*</span>
              </label>
              <select
                id="disruption_type"
                disabled={isBusy}
                {...register("disruption_type")}
                className="w-full rounded-sm border border-hairline bg-surface px-3 py-2 text-xs text-ink focus:border-carbon-950 focus:outline-none focus:ring-1 focus:ring-carbon-950 disabled:cursor-not-allowed disabled:bg-canvas"
              >
                {SUPPORTED_DISRUPTION_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              {errors.disruption_type ? (
                <p className="mt-1 text-[11px] text-status-breached">
                  {errors.disruption_type.message}
                </p>
              ) : null}
            </div>

            <div>
              <label
                htmlFor="delay_duration_hours"
                className="mb-1.5 block text-xs font-medium text-ink"
              >
                Delay Duration (Hours) <span className="text-status-breached">*</span>
              </label>
              <input
                id="delay_duration_hours"
                type="number"
                step="0.5"
                min="0.5"
                max="720"
                disabled={isBusy}
                {...register("delay_duration_hours", { valueAsNumber: true })}
                className="w-full rounded-sm border border-hairline bg-surface px-3 py-2 font-mono text-xs text-ink focus:border-carbon-950 focus:outline-none focus:ring-1 focus:ring-carbon-950 disabled:cursor-not-allowed disabled:bg-canvas"
              />
              {errors.delay_duration_hours ? (
                <p className="mt-1 text-[11px] text-status-breached">
                  {errors.delay_duration_hours.message}
                </p>
              ) : null}
            </div>

            <div>
              <label
                htmlFor="description"
                className="mb-1.5 block text-xs font-medium text-ink"
              >
                Description <span className="text-ink-muted">(Optional)</span>
              </label>
              <input
                id="description"
                type="text"
                placeholder="Scenario notes..."
                disabled={isBusy}
                {...register("description")}
                className="w-full rounded-sm border border-hairline bg-surface px-3 py-2 text-xs text-ink placeholder:text-ink-muted focus:border-carbon-950 focus:outline-none focus:ring-1 focus:ring-carbon-950 disabled:cursor-not-allowed disabled:bg-canvas"
              />
              {errors.description ? (
                <p className="mt-1 text-[11px] text-status-breached">
                  {errors.description.message}
                </p>
              ) : null}
            </div>
          </div>

          {error ? (
            <div
              role="alert"
              className="flex flex-wrap items-start justify-between gap-3 rounded-sm border border-status-breached-border bg-status-breached-bg px-3.5 py-2.5 text-xs text-status-breached"
            >
              <div className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-semibold">
                    {error.code}
                    {error.statusCode ? ` (HTTP ${error.statusCode})` : ""}
                  </p>
                  <p className="mt-0.5">{error.message}</p>
                  {error.message.includes("not found in graph") ? (
                    <button
                      type="button"
                      onClick={() => {
                        void dispatch(resetGraphThunk()).then(() => {
                          void dispatch(fetchBackendHealthThunk());
                          dispatch(clearSimulationError());
                        });
                      }}
                      className="mt-2 inline-flex items-center gap-1.5 rounded-sm border border-status-breached-border bg-white px-2.5 py-1 font-medium text-status-breached hover:bg-canvas"
                    >
                      <RotateCcw className="h-3 w-3" aria-hidden="true" />
                      Restore Baseline Graph (Reset 19 Nodes)
                    </button>
                  ) : null}
                </div>
              </div>
              <button
                type="button"
                onClick={() => dispatch(clearSimulationError())}
                className="text-[11px] font-medium underline hover:opacity-80"
              >
                Dismiss
              </button>
            </div>
          ) : null}

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-hairline pt-3.5">
            <div className="flex items-center gap-2 text-xs text-ink-muted">
              {executionState === "success" ? (
                <span className="inline-flex items-center gap-1.5 text-status-feasible">
                  <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                  Backend response synchronized
                </span>
              ) : (
                <span>Benchmark preset: SUP-01 · SUPPLIER_DELAY · 8.0h</span>
              )}
            </div>

            <div className="flex items-center gap-2.5">
              <button
                type="button"
                disabled={isBusy}
                onClick={() =>
                  reset({
                    supplier_id: DEFAULT_BENCHMARK_REQUEST.supplier_id,
                    disruption_type: DEFAULT_BENCHMARK_REQUEST.disruption_type,
                    delay_duration_hours: DEFAULT_BENCHMARK_REQUEST.delay_duration_hours,
                    description: DEFAULT_BENCHMARK_REQUEST.description,
                  })
                }
                className="inline-flex items-center gap-1.5 rounded-sm border border-hairline bg-surface px-3 py-2 text-xs font-medium text-ink hover:bg-canvas disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-carbon-950"
              >
                <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
                Reset Form
              </button>

              <button
                type="submit"
                disabled={isBusy}
                className="inline-flex items-center gap-2 rounded-sm border border-carbon-950 bg-carbon-950 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white transition-colors hover:bg-carbon-800 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-carbon-950 focus-visible:ring-offset-2"
              >
                {isBusy ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                    Running Simulation…
                  </>
                ) : (
                  <>
                    <Play className="h-3.5 w-3.5" aria-hidden="true" />
                    RUN SIMULATION
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </CardBody>
    </Card>
  );
}

