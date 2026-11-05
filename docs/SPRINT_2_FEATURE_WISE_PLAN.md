# RE:Flow — Team PHOTON
# SPRINT 2: FEATURE-WISE DEVELOPMENT & WORK ALLOCATION PLAN
### Temporal Disruption Simulation, Dynamic Inventory Evolution & Intervention Windows

**Project:** EPAM Sprints — PHOTON / RE:Flow  
**Sprint:** Sprint 2 (Feature-Driven Delivery Model)  
**Standard:** Enterprise Clean Architecture (FastAPI Ready)  
**Official Target:** 8-Hour Supplier Delay Benchmark Scenario (AC-01 to AC-10)

---

## 1. Executive Mission & What Is NEW in Sprint 2

### 1.1 The Fundamental Shift: Static $\to$ Temporal
- **Sprint 1 (Delivered):** Answered *"WHAT is connected downstream?"* (Static DAG Graph, Reachability BFS, Pre-construction validation, 130 tests passing).
- **Sprint 2 (Current Focus):** Answers **"WHEN will inventory hit zero, WHICH 2 customer orders will fail, and HOW MUCH TIME do we have to intervene?"** (Time Dimension $t$, Discrete-Time Inventory Depletion, Stockout Prediction, and Intervention Window Calculation).

```
                                SPRINT 2 FEATURE PIPELINE
                                
 ┌──────────────────────┐      ┌─────────────────────────┐      ┌──────────────────────────┐
 │  FEATURE 1           │      │  FEATURE 2              │      │  FEATURE 3               │
 │  Disruption Event    │ ───► │  Downstream Ripple      │ ───► │  Inventory Depletion     │
 │  Generator           │      │  Propagation Engine     │      │  Simulator (Hourly)      │
 └──────────────────────┘      └─────────────────────────┘      └────────────┬─────────────┘
                                                                             │
                                                                             ▼
 ┌──────────────────────┐      ┌─────────────────────────┐      ┌──────────────────────────┐
 │  FEATURE 6 to 10     │      │  FEATURE 5              │      │  FEATURE 4               │
 │  FastAPI, D3 Slider, │ ◄─── │  Intervention Window    │ ◄─── │  Stockout Predictor &    │
 │  & AC-01..10 Tests   │      │  Calculator (ΔT Engine) │      │  2-Order Delay Matcher   │
 └──────────────────────┘      └─────────────────────────┘      └──────────────────────────┘
```

---

## 2. Comprehensive Breakdown of All 10 Features

---

### 🟢 FEATURE 1: Disruption Event Generator
* **Real-World Purpose:** Allows a supply chain manager to inject a disruption event on a specific vendor.
* **What is NEW in Sprint 2:** Converts a passive graph into an active simulation by attaching dynamic disruption metadata to supplier nodes.
* **Functional Requirements:**
  - Select an affected supplier from the graph (e.g., `SUP-01`).
  - Define disruption type (e.g., `SUPPLIER_DELAY`, `CAPACITY_DROP`).
  - Specify delay duration (Benchmark baseline: **8 hours**).
  - Record the disruption as an immutable event object.
  - Associate the event with the targeted supplier node.
* **Input:** `supplier_id: str`, `disruption_type: str`, `delay_duration_hours: float`.
* **Output:** Validated `DisruptionEvent` object ready for downstream engine consumption.
* **Assigned Lead:** **SOUMYA** | *Backup Support:* **Deep Sandilya**

---

### 🟢 FEATURE 2: Downstream Ripple Effect Propagation Engine
* **Real-World Purpose:** Traces the cascade of failure from the disrupted supplier through BOM parts and finished products down to customer orders.
* **What is NEW in Sprint 2:** Event-driven downstream traversal that applies disruption boundaries and strictly prevents repeatedly processing the same node (cycle-safe deduplication).
* **Functional Requirements:**
  - Start propagation strictly from the disrupted supplier.
  - Traverse downstream dependency hierarchy: Supplier $\to$ BOM Parts $\to$ Finished Products $\to$ Customer Orders.
  - Identify all affected intermediate BOM parts.
  - Identify all affected finished products.
  - Identify all affected customer orders.
  - Avoid redundant processing of multi-parent nodes using visited-state sets.
* **Input:** Target `supplier_id` + `SupplyChainGraph`.
* **Output:** `RippleImpactSummary` containing distinct lists of affected parts, products, and customer orders.
* **Assigned Lead:** **ANSH** | *Backup Support:* **Preetam**

---

### 🟢 FEATURE 3: Dynamic Inventory Depletion Simulator
* **Real-World Purpose:** Models physical warehouse reality. Factories don't halt instantly when a supplier delays; they consume existing safety stock and stock on hand.
* **What is NEW in Sprint 2:** Introduces discrete time steps ($t$ in hours) to model inventory depletion over time.
* **Mathematical Equation:**
  $$\text{Stock}_p(h) = \max\Big(0,\; \text{Stock}_p(h-1) - \text{HourlyConsumption}_p\Big)$$
  *(Under an 8-hour supplier delay, incoming shipment replenishment is delayed until Hour 8).*
* **Functional Requirements:**
  - Ingest current on-hand warehouse inventory.
  - Account for hourly component burn/consumption rates ($\text{daily\_consumption} / 24$).
  - Factor in delayed incoming supplier replenishment.
  - Generate hour-by-hour stock trajectory ($h = 0 \dots 72\text{ hours}$).
  - Flag the exact inflection point when inventory falls below minimum buffer.
* **Input:** Part inventory levels, burn rates, and supplier delay duration (8h).
* **Output:** `InventoryDepletionTimeline` (Hourly stock array and depletion curve).
* **Assigned Lead:** **AADEE** *(Step-Up Role)* | *Backup Support:* **Anushka**

---

### 🟢 FEATURE 4: Stockout Timestamp Predictor & 2-Order Delay Matcher
* **Real-World Purpose:** Predicts the exact hour when inventory hits absolute zero ($T_{\text{stockout}}$) and matches which specific customer purchase orders will breach their delivery promise.
* **What is NEW in Sprint 2:** Replaces rough static estimation with deterministic timestamp calculation and directly links stockout to customer contract liabilities.
* **Official Benchmark Target:** When an 8-hour supplier delay is simulated, this feature **must identify EXACTLY TWO affected customer orders** (`ORD-01` and `ORD-02`).
* **Functional Requirements:**
  - Identify the earliest hour where $\text{Stock}_p(h) = 0$.
  - Convert depletion hour into predicted ISO stockout timestamp ($T_{\text{stockout}}$).
  - Map stockout parts to finished products and traverse to downstream customer orders.
  - Evaluate order due-dates against assembly recovery timeline.
  - Output exactly the two breached customer commitments for the benchmark scenario.
* **Input:** `InventoryDepletionTimeline` + Order delivery deadlines.
* **Output:** $T_{\text{stockout}}$ timestamp + List of **exactly 2 delayed customer orders**.
* **Assigned Lead:** **SONAL** *(Step-Up Role)* | *Backup Support:* **Divyanshu**

---

### 🟢 FEATURE 5: Intervention Window Calculator ($\Delta T_{\text{intervention}}$)
* **Real-World Purpose:** **The Crown Jewel of Sprint 2!** Computes the exact operational window supply chain planners have to take corrective action (e.g., place emergency orders with alternate vendors) before operational failure becomes irreversible.
* **The Official Formula:**
  $$\Delta T_{\text{intervention}} = T_{\text{stockout}} - T_{\text{current}} - t_{\text{recovery lead time}}$$
* **Operational Interpretation Matrix:**
  - $\Delta T_{\text{intervention}} > 0\text{ hours} \implies$ **FEASIBLE (Positive Window):** Planners can successfully intervene; alternate shipment will arrive before stockout.
  - $\Delta T_{\text{intervention}} \le 0\text{ hours} \implies$ **CRITICAL BREACH (Negative/Zero Window):** Action cannot prevent factory shutdown; replacement arrives too late.
* **Functional Requirements:**
  - Compute $T_{\text{stockout}} - T_{\text{current}}$.
  - Subtract alternate supplier expedited recovery lead time ($t_{\text{recovery lead time}}$).
  - Classify feasibility status (`FEASIBLE` vs `BREACHED`).
  - Calculate remaining intervention hours.
* **Input:** $T_{\text{stockout}}$, $T_{\text{current}}$ (Hour 0), $t_{\text{recovery lead time}}$.
* **Output:** $\Delta T_{\text{intervention}}$ (Hours), Feasibility Boolean, and Action Recommendation.
* **Assigned Lead:** **DIVYANSHU** *(Step-Up Role)* | *Backup Support:* **Deep Sandilya**

---

### 🟢 FEATURE 6: Scenario Data & Benchmark Configuration
* **Real-World Purpose:** Provides verified dataset parameters so the 8-hour delay scenario deterministically produces the official benchmark results.
* **Functional Requirements:**
  - Enrich `scenario_dataset.json` with hourly consumption rates, safety stocks, and alternate vendor recovery lead times.
  - Calibrate customer order deadlines so that an 8-hour delay on `SUP-01` affects **exactly 2 customer orders**.
* **Assigned Lead:** **ANUSHKA** | *Backup Support:* **Deep Sandilya**

---

### 🟢 FEATURE 7: Simulation Engine Orchestration Pipeline
* **Real-World Purpose:** Connects Features 1 through 5 into a single high-performance pipeline:
  $$\text{Disruption Event} \longrightarrow \text{Ripple Engine} \longrightarrow \text{Inventory Depletion} \longrightarrow \text{Stockout Prediction} \longrightarrow \text{Intervention Calculation}$$
* **Performance Constraint:** Complete simulation execution must complete in **$< 25.0\text{ ms}$** SLA without any database dependency.
* **Assigned Lead:** **PREETAM** | *Backup Support:* **Ansh**

---

### 🟢 FEATURE 8: FastAPI API Integration & OpenAPI Contracts
* **Real-World Purpose:** Exposes simulation capabilities over modern REST endpoints with native Pydantic validation and automatic interactive Swagger documentation (`/docs`).
* **Endpoints:**
  - `POST /api/v1/simulation/disrupt` (Accepts disruption parameters, returns complete timeline & intervention analysis).
  - `GET /api/v1/simulation/scenarios/benchmark-8hr` (Pre-configured 8-hour benchmark run).
* **Assigned Lead:** **KANAK** *(Step-Up Role)* | *Backup Support:* **Deep Sandilya**

---

### 🟢 FEATURE 9: Official Benchmark Automated Test Suite (AC-01 to AC-10)
* **Real-World Purpose:** Automated Pytest test suite using FastAPI `TestClient` to verify that all 10 acceptance criteria pass with 100% green status.
* **Assigned Lead:** **SHANU** | *Backup Support:* **Soumya**

---

### 🟢 FEATURE 10: Interactive Simulation Timeline UI & Visual Gauge
* **Real-World Purpose:** Frontend D3.js dashboard featuring:
  - Interactive Timeline Scrubber (Hour 0 to Hour 72 slider).
  - Dynamic Stock Depletion Curve (visualizing inventory dropping to zero).
  - Intervention Window Countdown Gauge (Green $\to$ Amber $\to$ Red status badge).
* **Assigned Lead:** **SUMIT** *(Step-Up Role)* | *Backup Support:* **Kanak**

---

### 🟢 FEATURE 11: Core Architecture, Domain Contracts & Team Backup
* **Real-World Purpose:** Sets immutable Pydantic contracts and domain models (`models/disruption.py`, `models/simulation.py`, `schemas/simulation.py`), oversees FastAPI integration, and serves as the **Lead Technical Backup** across all modules.
* **Assigned Lead:** **DEEP SANDILYA**

---

### 🟢 FEATURE 12: Sprint 2 Coordination & Official Benchmark Acceptance Sign-Off
* **Real-World Purpose:** Coordinates daily milestone progress across all 12 members, leads code review integration, and delivers the official AC-01 to AC-10 benchmark sign-off report for mentors.
* **Assigned Lead:** **MISHTI**

---

# 3. Team PHOTON 12-Member Work Allocation Matrix

### Smart Workload Rebalancing Policy:
- **Sprint 1 Heavy Hitters** (Deep, Soumya, Preetam, Shanu) are positioned in **Architecture, Contracts, Pipeline Orchestration, Testing, and Backup Review**.
- **Sprint 1 Light Contributors** (Aadee, Sonal, Divyanshu, Kanak, Sumit) are stepped up into **Core Feature Leads**.

| # | Team Member | Sprint 2 Assigned Feature | Core Responsibility & Deliverable | Backup Support Lead |
|---|---|---|---|---|
| **1** | **MISHTI** | **Sprint 2 Lead & AC Sign-off** | Benchmark verification, milestone tracking, review documentation | Deep Sandilya |
| **2** | **DEEP** *(You)* | **Architecture & Data Contracts** | Domain models, Pydantic schemas, FastAPI oversight, **Lead Backup for all members** | — *(Core Anchor)* |
| **3** | **ANUSHKA** | **Feature 6: Scenario Data** | 8-hour benchmark data calibration, recovery lead times in JSON | Deep Sandilya |
| **4** | **SOUMYA** | **Feature 1: Disruption Generator** | Supplier disruption event creation, parameter validation & checks | Shanu |
| **5** | **ANSH** | **Feature 2: Ripple Engine** | Event-driven downstream traversal, deduplicated affected entities | Preetam |
| **6** | **AADEE** | **Feature 3: Inventory Depletion** | Discrete hourly stock depletion math & replenishment delay logic | Anushka |
| **7** | **SONAL** | **Feature 4: Stockout & 2 Orders** | $T_{\text{stockout}}$ timestamp calculation, matching exactly 2 failing orders | Divyanshu |
| **8** | **DIVYANSHU**| **Feature 5: Intervention Window** | $\Delta T_{\text{intervention}}$ calculation, feasibility check, remaining hours | Deep Sandilya |
| **9** | **PREETAM** | **Feature 7: Engine Pipeline** | Orchestrating Features 1–5 into an end-to-end execution pipeline | Ansh |
| **10**| **KANAK** | **Feature 8: FastAPI Endpoints** | REST API routes, Pydantic request handling, Swagger `/docs` | Deep Sandilya |
| **11**| **SHANU** | **Feature 9: Testing Suite** | Automated Pytest tests for AC-01 through AC-10 verification | Soumya |
| **12**| **SUMIT** | **Feature 10: D3 Timeline UI** | Hour 0–72 playback slider, stock depletion chart, intervention gauge | Kanak |

---

# 4. The Official Benchmark: 8-Hour Delay Exact Walkthrough

To ensure all teammates build toward the exact same benchmark oracle:

```
[Target Supplier: SUP-01]
Delay Injected: 8.0 Hours
       │
       ▼ (Ripple Effect)
Supplies: PART-01 (Burn rate: 2 units/hour | On-hand: 16 units)
Used in:  PROD-01 (Enterprise Laptop)
       │
       ▼ (Inventory Depletion)
Hour 0: 16 units in warehouse
Hour 2: 12 units
Hour 4: 8 units (Normal replenishment delayed by 8 hours!)
Hour 8: 0 units  ──► [STOCKOUT DETECTED: T_stockout = Hour 8]
       │
       ▼ (Downstream Customer Commitments)
PROD-01 fulfills orders:
• ORD-01 (Delivery Due: Hour 10) ──► FAILED (Cannot assemble without PART-01)
• ORD-02 (Delivery Due: Hour 12) ──► FAILED (Cannot assemble without PART-01)
• ORD-03..10 (Delivery Due: Day 10+) ──► SAFE (Sufficient recovery buffer)
Result: EXACTLY TWO CUSTOMER ORDERS AFFECTED!
       │
       ▼ (Intervention Window Calculation)
T_stockout = 8.0 Hours
T_current  = 0.0 Hours
t_recovery = 5.0 Hours (Alternate expedited supplier delivery lead time)
ΔT_intervention = 8.0 - 0.0 - 5.0 = +3.0 HOURS!
Status: FEASIBLE (3 Hours remaining to place order before factory shutdown)
```

---

# 5. Sprint 2 Official Acceptance Criteria (AC-01 to AC-10)

Every member's feature must satisfy these 10 testable checks:

| ID | Acceptance Criterion | Test Verification Method | Feature Owner |
| :--- | :--- | :--- | :--- |
| **AC-01** | An 8-hour supplier delay can be introduced into the system. | API payload accepts `delay_duration_hours = 8.0`. | Soumya |
| **AC-02** | The disruption is associated with the correct supplier node. | Event target references valid `SUP-01` ID. | Soumya |
| **AC-03** | Downstream dependencies are correctly identified. | Propagation traverses all 4 tiers without cycle traps. | Ansh |
| **AC-04** | Affected BOM parts are identified. | `PART-01` is identified in ripple output. | Ansh |
| **AC-05** | Affected finished products are identified. | `PROD-01` is identified in ripple output. | Ansh |
| **AC-06** | **Exactly two expected customer orders are identified in benchmark.** | Assert `affected_orders == ["ORD-01", "ORD-02"]`. | Sonal |
| **AC-07** | Inventory depletion is calculated over time. | Array of hourly stock levels is generated correctly. | Aadee |
| **AC-08** | Stockout timestamp is predicted accurately. | Stockout occurs at exact hour $16 / 2 = \text{Hour } 8$. | Sonal |
| **AC-09** | Intervention window is calculated using specified formula. | $\Delta T = 8.0 - 0.0 - 5.0 = +3.0\text{ hours}$ (FEASIBLE). | Divyanshu |
| **AC-10** | Results are available for API verification. | Endpoint returns complete structured JSON within $< 25\text{ ms}$. | Kanak & Shanu |

---

# 6. Sprint Boundaries (What is Out of Scope)

To prevent scope creep, remind all members what is **NOT** part of Sprint 2:

| Feature / Capability | Planned Sprint | Status in Sprint 2 |
| :--- | :---: | :--- |
| Supply Chain Graph & Scenario Generator | Sprint 1 | **Delivered & Frozen** |
| Ripple Simulation & Stockout Timing | Sprint 2 | **CURRENT SPRINT** |
| Intervention Window Calculation | Sprint 2 | **CURRENT SPRINT** |
| Google OR-Tools Recovery Optimizer | Sprint 3 | **STRICTLY FORBIDDEN** |
| Top-3 Recovery Options Recommendation | Sprint 3 | **STRICTLY FORBIDDEN** |
| Operational Control Tower Dashboard | Sprint 4 | **STRICTLY FORBIDDEN** |
| Human Approval Workflow & Audit Log | Sprint 4 | **STRICTLY FORBIDDEN** |

---
*End of Sprint 2 Feature-Wise Plan — Team PHOTON*

