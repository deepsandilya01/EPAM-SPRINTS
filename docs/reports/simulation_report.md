# RE:Flow Sprint 2 — Simulation Pipeline Performance SLA Report

> **Owner:** Shanu — Feature 11: Performance SLA Benchmarking  
> **Depends On:** Ansh (`backend/app/simulation/engine.py` — `run_disruption_simulation()`)  
> **Handoff Target:** Sumit (Final Sprint 2 Review & Sign-Off)  
> **SLA Requirement:** End-to-end 72-hour disruption simulation pipeline execution **< 25.0 ms** across **1,000 runs**  
> **Overall Verdict:** **PASS** — **1,000 / 1,000 runs (100.0%)** completed under 25.0 ms (`P99 = 0.5568 ms`, `Max = 1.1341 ms`)

---

## 1. Executive Summary

The Sprint 2 disruption simulation pipeline (`run_disruption_simulation()`) was benchmarked across **1,000 measured iterations** (preceded by **50 warm-up iterations**) against the canonical 8-hour supplier delay scenario (`SUP-01`, 72-hour simulation horizon, 19-node / 21-edge Sprint 1 supply chain graph).

- **SLA Compliance:** `1000 / 1000` iterations (`100.0%`) executed below the `25.0 ms` SLA target.
- **P99 Latency:** `0.556793 ms` (**~44.9x faster** than the `25.0 ms` threshold).
- **Worst-Case (Max) Latency:** `1.134100 ms` (**~22.0x faster** than the `25.0 ms` threshold).
- **Mean / Median Latency:** `0.178109 ms` mean / `0.151600 ms` median (P50).
- **Deterministic Oracle Accuracy:** Every benchmarked run matched the Sprint 2 oracle (`PART-05` stockout at `T_stockout = 8.0h`, `2` breached orders `["ORD-01", "ORD-02"]`, `ΔT = +3.0h`, status `FEASIBLE`) with zero mutation to the underlying Sprint 1 `nx.DiGraph`.

---

## 2. End-to-End Statistical SLA Metrics (1,000 Iterations)

Measured via `time.perf_counter_ns()` in [benchmark_simulation.py](../../backend/benchmarks/benchmark_simulation.py) and persisted in [simulation_benchmark_report.json](../../backend/reports/simulation_benchmark_report.json).

| Metric | Measured Latency (ms) | SLA Target (ms) | Margin vs SLA | Status |
|---|---|---|---|---|
| **Min** | `0.133200` | `< 25.0` | `24.8668 ms` | PASS |
| **Mean** | `0.178109` | `< 25.0` | `24.8219 ms` | PASS |
| **Median (P50)** | `0.151600` | `< 25.0` | `24.8484 ms` | PASS |
| **P90** | `0.250050` | `< 25.0` | `24.7500 ms` | PASS |
| **P95** | `0.316545` | `< 25.0` | `24.6835 ms` | PASS |
| **P99** | `0.556793` | `< 25.0` | `24.4432 ms` | PASS |
| **Max** | `1.134100` | `< 25.0` | `23.8659 ms` | PASS |
| **Std Deviation** | `0.088142` | — | — | — |
| **Runs < 25.0 ms** | `1000 / 1000 (100.0%)` | `100%` | — | **PASS** |

---

## 3. Stage-by-Stage Latency Breakdown

| Pipeline Stage | Module Owner | Min (ms) | Mean (ms) | Median P50 (ms) | P95 (ms) | P99 (ms) | Max (ms) |
|---|---|---|---|---|---|---|---|
| **1. Ripple Propagation** | Aadee (`ripple.py`) | `0.009700` | `0.016608` | `0.011700` | `0.029155` | `0.083554` | `0.712800` |
| **2. Inventory Depletion** | Sonal (`inventory.py`) | `0.082700` | `0.105179` | `0.090800` | `0.173060` | `0.356507` | `0.993700` |
| **3. Stockout Prediction** | Anushka (`stockout.py`) | `0.007600` | `0.011864` | `0.009300` | `0.019705` | `0.072601` | `0.126100` |
| **4. Intervention Window** | Mishti (`intervention.py`) | `0.004400` | `0.008147` | `0.005800` | `0.015105` | `0.038814` | `0.212900` |

> **Observation:** Stage 2 (discrete 73-step hourly inventory depletion with Pydantic `HourlyStockPoint` model construction) accounts for ~59% of mean pipeline runtime (`0.105 ms` out of `0.178 ms`), while stages 1, 3, and 4 execute in sub-0.02 ms on average. Total pipeline execution including stage wrappers and result assembly stays under `1.14 ms` even at worst-case jitter.

---

## 4. Oracle & Invariant Verification

| Check | Expected Value | Observed Value | Status |
|---|---|---|---|
| **Graph Immutability** | 19 nodes, 21 edges unchanged | 19 nodes, 21 edges unchanged (`graph_unmutated: true`) | PASS |
| **Critical Part Selected** | `PART-05` | `PART-05` | PASS |
| **Stockout Timestamp (`T_stockout`)** | `8.0` hours | `8.0` hours | PASS |
| **Breached Order Count** | `2` | `2` | PASS |
| **Breached Order IDs** | `ORD-01`, `ORD-02` | `["ORD-01", "ORD-02"]` | PASS |
| **Intervention Window (`ΔT`)** | `+3.0` hours | `3.0` hours | PASS |
| **Intervention Feasibility Status** | `FEASIBLE` | `FEASIBLE` | PASS |

---

## 5. Workload & Test Environment

| Parameter | Value |
|---|---|
| **Timestamp (UTC)** | `2026-11-26T17:36:21.236511+00:00` |
| **Workload** | `SUP-01`, `SUPPLIER_DELAY`, `8.0` hours delay, `72`-hour horizon |
| **Graph Size** | `19` nodes, `21` edges |
| **Warm-up / Measured Runs** | `50` warm-up / `1000` measured |
| **Python** | `3.14.2` (`CPython`) |
| **NetworkX** | `3.7` |
| **Operating System** | `Windows 11` (`10.0.26300`, `AMD64`) |
| **Processor** | `Intel64 Family 6 Model 151 Stepping 2, GenuineIntel` |

---

## 6. Reproducibility Command & Artifacts

```bash
python backend/benchmarks/benchmark_simulation.py
```

- **Benchmark Script:** `backend/benchmarks/benchmark_simulation.py`
- **Raw JSON Report:** `backend/reports/simulation_benchmark_report.json`
- **Markdown Report:** `docs/reports/simulation_report.md`
