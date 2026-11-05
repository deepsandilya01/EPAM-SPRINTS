# RE:Flow — Team PHOTON
# SPRINT 2 IMPLEMENTATION & ARCHITECTURE PLAN
### Temporal Disruption Simulation, Dynamic Inventory Evolution & Intervention Windows

**Project:** EPAM Sprints — PHOTON / RE:Flow  
**Phase:** Sprint 2 Implementation Blueprint (Documentation Only — No Code Changes)  
**Standard:** Enterprise Clean/Hexagonal Architecture  
**Dependencies:** Builds strictly upon Sprint 1 Verified Foundation (19 Nodes, 21 Edges, 130/130 Passing Tests)

---

## 1. Executive Summary & Sprint 2 Objective

In **Sprint 1**, Team PHOTON successfully established the **Static Dependency Foundation**:
- 4-Tier Directed Acyclic Graph (DAG) in NetworkX
- Pre-construction validation engine & acyclicity guarantee
- Sub-millisecond downstream reachability traversal ($0.15\text{ ms}$ BFS)
- D3.js interactive graph dashboard

### The Core Problem Sprint 2 Solves:
Sprint 1 answers: *"If Supplier $X$ fails, **WHAT** entities are connected downstream?"* (Static Reachability).  
However, real-world supply chain managers cannot take action on static reachability alone, because **factories do not halt immediately upon supplier failure**. Factories have warehouse inventory buffers (Safety Stock & Stock on Hand).

**Sprint 2 introduces the TIME dimension ($t$):**
1. **Dynamic Disruption Injection:** Simulating supplier capacity drops ($100\% \to 0\%$ or partial drops), lead-time spikes, and factory shutdowns.
2. **Temporal Inventory Depletion:** Simulating day-by-day inventory consumption over a discrete simulation horizon ($t = 0 \dots 30\text{ days}$).
3. **Stockout Timing Prediction ($T_{\text{stockout}}$):** Computing the exact calendar day each part runs out of stock.
4. **Intervention Window ($W_{\text{intervention}}$):** Calculating the exact remaining time window planners have to secure alternative suppliers before customer delivery SLA breaches become unavoidable.

---

## 2. Core Mathematical Formulations for Sprint 2

Sprint 2 implementation revolves around three deterministic mathematical models:

### 2.1 Daily Inventory Depletion Equation
For each BOM Part $p \in V_{\text{parts}}$ at discrete time step $t \in [0, T_{\text{horizon}}]$ (where $t$ is measured in days):

$$\text{Stock}_p(t+1) = \max\Big(0,\; \text{Stock}_p(t) + \text{Inflow}_p(t) - \text{Consumption}_p(t)\Big)$$

Where:
- $\text{Stock}_p(0) = \text{stock\_on\_hand}$ from canonical dataset.
- $\text{Consumption}_p(t) = \text{daily\_consumption}_p \times \text{OperationalStatus}(\text{AssemblyLines})$.
- $\text{Inflow}_p(t) = \sum_{s \in \text{Suppliers}(p)} \text{Capacity}_s(t - L_{s,p})$, where $L_{s,p}$ is lead time in days.
- Under a disruption event on supplier $s^*$, $\text{Capacity}_{s^*}(t) = 0$ (or reduced by severity $\alpha$).

---

### 2.2 Stockout Time ($T_{\text{stockout}}$)
The earliest time step $\tau$ where on-hand inventory drops to zero:

$$T_{\text{stockout}}(p) = \min \Big\{ t \ge 0 \;\Big|\; \text{Stock}_p(t) = 0 \Big\}$$

*Linear baseline approximation (when inflow is zero):*
$$T_{\text{stockout\_linear}}(p) = \frac{\text{Stock}_p(0)}{\text{DailyConsumption}_p} = \text{days\_of\_supply}_p$$

---

### 2.3 The Intervention Window Formula ($W_{\text{intervention}}$)
The critical operational metric that tells the planner: *"When can we still act?"*

$$W_{\text{intervention}}(p) = T_{\text{stockout}}(p) - T_{\text{current}} - \text{RecoveryLeadTime}_{\text{alt}}(p)$$

Where:
- $T_{\text{stockout}}(p)$: Day on which part $p$ runs out of inventory.
- $T_{\text{current}}$: Current simulation day (usually $t=0$).
- $\text{RecoveryLeadTime}_{\text{alt}}(p)$: Time required for an alternative supplier or expedited shipment to deliver replacement parts.

#### Status Interpretation Matrix:
| Value of $W_{\text{intervention}}$ | Health Status | Operational Meaning | UI Indicator |
| :--- | :--- | :--- | :--- |
| **$W_{\text{intervention}} > 3\text{ days}$** | **STABLE (Green)** | Ample buffer. Action can be planned normally. | Precision Emerald |
| **$0 \le W_{\text{intervention}} \le 3\text{ days}$** | **WARNING (Amber)** | Urgent action required. Alternative order must be triggered immediately. | Burnished Amber |
| **$W_{\text{intervention}} < 0\text{ days}$** | **BREACHED (Red)** | Too late to prevent factory shutdown. Customer order delay unavoidable. | Flash Red / Obsidian |

---

## 3. Folder-Wise Architecture for Sprint 2

Sprint 2 strictly maintains the **Clean Layered Architecture** established in Sprint 1. New capabilities are integrated into their designated architectural layers without coupling:

```
EPAM-SPRINTS/backend/app/
├── core/                         # [MODIFIED] Constants, SLAs, and Custom Exceptions
│   ├── constants.py              # + Simulation modes, Horizon limit (30d), Disruption types
│   └── exceptions.py             # + SimulationError, StockoutPredictionError, NegativeInventoryError
├── models/                       # [MODIFIED] Domain Models & State Snapshots (Deep Sandilya)
│   ├── nodes.py                  # + Temporal fields (safety_stock, recovery_lead_time_days)
│   ├── disruption.py             # [NEW] DisruptionScenario, DisruptionEvent dataclasses
│   └── simulation.py             # [NEW] DailyStateSnapshot, SimulationTimeline aggregate
├── schemas/                      # [MODIFIED] Pydantic Data Contracts (Deep Sandilya)
│   ├── disruption.py             # [NEW] DisruptionRequestSchema, DisruptionEventSchema
│   └── simulation.py             # [NEW] SimulationResponseSchema, InterventionWindowSchema
├── simulation/                   # [NEW MODULE] Discrete-Time Simulation Engine
│   ├── __init__.py               # Package exports
│   ├── engine.py                 # Time-stepped discrete execution engine (t = 0..30)
│   ├── inventory.py              # Daily inventory evolution & buffer depletion
│   ├── timeline.py               # Cumulative downstream delay curves & order impact
│   └── intervention.py           # Intervention window calculator
├── services/                     # [MODIFIED] Service Layer Orchestration
│   ├── graph_service.py          # Coordinates simulation engine with cached DiGraph
│   └── simulation_service.py     # [NEW] Facade service for simulation execution & caching
├── api/routes/                   # [MODIFIED] HTTP REST API Blueprints
│   └── simulation.py             # [NEW] POST /api/simulation/run, POST /api/simulation/inject
├── static/                       # [MODIFIED] Frontend Presentation Layer (D3.js)
│   ├── sprint-2-demo.html        # [NEW] Interactive temporal simulation command center
│   ├── js/timeline_slider.js     # [NEW] Day 0 to Day 30 time-scrubber playback control
│   └── js/inventory_chart.js     # [NEW] D3.js line chart showing stock depletion curves
└── tests/                        # [MODIFIED] Automated Pytest Suite
    ├── unit/test_simulation.py   # [NEW] 25+ unit tests for temporal simulation
    └── integration/test_sim_api.py # [NEW] End-to-end integration tests for simulation API
```

---

## 4. Deep Sandilya's Exact Sprint 2 Responsibilities

As the **Domain Models & API Data Contracts Lead**, Deep Sandilya's responsibilities expand to anchor the data structures for temporal simulation:

### 4.1 `core/constants.py` Updates
```python
# Sprint 2 Simulation Constants
DEFAULT_SIMULATION_HORIZON_DAYS = 30
MAX_SIMULATION_HORIZON_DAYS = 90
DEFAULT_RECOVERY_LEAD_TIME_DAYS = 5
MAX_SIMULATION_LATENCY_MS = 25.0  # Performance SLA for 30-day simulation

class DisruptionType(str, Enum):
    SUPPLIER_SHUTDOWN = "SUPPLIER_SHUTDOWN"       # 100% capacity loss
    CAPACITY_REDUCTION = "CAPACITY_REDUCTION"     # Partial percentage reduction
    LOGISTICS_DELAY = "LOGISTICS_DELAY"           # Transit lead-time spike

class InterventionStatus(str, Enum):
    STABLE = "STABLE"         # Window > 3 days
    WARNING = "WARNING"       # 0 <= Window <= 3 days
    BREACHED = "BREACHED"     # Window < 0 days (Shutdown unavoidable)
```

### 4.2 `models/disruption.py` (New Domain Entity)
```python
@dataclass
class DisruptionEvent:
    """Represents an injected real-world disruption."""
    target_node_id: str
    disruption_type: DisruptionType
    severity_pct: float = 100.0        # 0.0 to 100.0%
    start_day: int = 0
    duration_days: int = 14            # Duration of vendor failure
    description: str = ""

    def __post_init__(self) -> None:
        if not (0.0 <= self.severity_pct <= 100.0):
            raise ModelValidationError("severity_pct must be between 0 and 100")
        if self.duration_days <= 0:
            raise ModelValidationError("duration_days must be strictly positive")
```

### 4.3 `models/simulation.py` (New Domain Aggregate)
```python
@dataclass
class DailyPartInventory:
    day: int
    part_id: str
    stock_on_hand: int
    daily_consumption: int
    is_stocked_out: bool

@dataclass
class PartInterventionWindow:
    part_id: str
    stockout_day: Optional[int]
    recovery_lead_time_days: int
    intervention_window_days: Optional[float]
    status: InterventionStatus

@dataclass
class SimulationResult:
    scenario_id: str
    horizon_days: int
    disrupted_nodes: List[str]
    timeline: Dict[int, List[DailyPartInventory]]  # Day -> Part Snapshots
    stockout_summary: Dict[str, Optional[int]]     # Part ID -> Stockout Day
    intervention_windows: List[PartInterventionWindow]
    impacted_customer_orders: List[Dict[str, Any]] # Orders missing deadline
    execution_time_ms: float
```

### 4.4 `schemas/simulation.py` (Pydantic API Data Contracts)
```python
class DisruptionInjectionSchema(BaseModel):
    node_id: str = Field(..., description="Target node identifier to disrupt (e.g. 'SUP-01')")
    disruption_type: str = Field(default="SUPPLIER_SHUTDOWN")
    severity_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    duration_days: int = Field(default=14, ge=1, le=90)
    start_day: int = Field(default=0, ge=0)

class SimulationRequestSchema(BaseModel):
    horizon_days: int = Field(default=30, ge=7, le=90)
    disruptions: List[DisruptionInjectionSchema] = Field(default_factory=list)

class InterventionWindowItemSchema(BaseModel):
    part_id: str
    part_name: str
    days_of_supply_initial: float
    stockout_day: Optional[int]
    intervention_window_days: Optional[float]
    status: str  # 'STABLE', 'WARNING', 'BREACHED'

class SimulationResponseSchema(BaseModel):
    success: bool
    horizon_days: int
    disruption_count: int
    stockout_parts_count: int
    delayed_orders_count: int
    intervention_windows: List[InterventionWindowItemSchema]
    daily_stock_timeline: Dict[str, List[int]]  # Part ID -> [stock_day_0, stock_day_1...]
    delayed_orders: List[Dict[str, Any]]
    execution_time_ms: float
```

---

## 5. Team PHOTON 12-Member Work Allocation (Sprint 2)

| Member | Sprint 2 Role | Primary Responsibility in Sprint 2 | Owned Files for Sprint 2 |
|---|---|---|---|
| **1. MISHTI** | **Sprint Lead & Integration** | Sprint 2 milestone tracking, PR integration reviews, demo script coordination | `docs/sprint-2-review.md` |
| **2. DEEP** | **Domain Models & Schemas** | Disruption & simulation domain models, Pydantic request/response contracts | `models/disruption.py`, `models/simulation.py`, `schemas/simulation.py`, `core/constants.py` |
| **3. ANUSHKA** | **Scenario Data Extensions** | Enriching `scenario_dataset.json` with safety stock, alternate lead times & production run rates | `backend/app/data/datasets/scenario_dataset.json` |
| **4. ANSH** | **Simulation Engine Core** | Time-stepped discrete execution engine ($t = 0 \dots 30$) and daily state transitions | `backend/app/simulation/engine.py` |
| **5. AADEE** | **Data Loader Adaptation** | Loading new temporal fields (safety stock, lead times) and feeding simulation models | `backend/app/data/loader.py` |
| **6. PREETAM** | **Inventory & Intervention Algorithms** | Daily inventory consumption formula & Intervention Window calculator | `backend/app/simulation/inventory.py`, `intervention.py` |
| **7. SONAL** | **Mathematical Verification** | Auditing daily inventory formulas against Excel ground truth; validating stockout calculations | `docs/simulation-verification.md` |
| **8. SOUMYA** | **Simulation Rule Validators** | Validating disruption inputs (preventing invalid node disruption, non-negative bounds) | `backend/app/validation/simulation_rules.py` |
| **9. DIVYANSHU** | **Edge Cases & Horizon Bounds** | Testing extreme scenarios (0 consumption, infinite horizon, simultaneous multi-node failure) | `backend/tests/unit/test_sim_edge_cases.py` |
| **10. SHANU** | **Regression & Simulation Tests** | Writing 30+ Pytest tests for simulation APIs, depletion accuracy, and deterministic outcomes | `backend/tests/unit/test_simulation.py`, `backend/tests/integration/test_sim_api.py` |
| **11. KANAK** | **Simulation Benchmarking** | Benchmarking 30-day simulation execution against the $25.0\text{ ms}$ SLA target | `backend/benchmarks/benchmark_simulation.py` |
| **12. SUMIT** | **Frontend Timeline UI & Docs** | D3.js timeline scrubber UI, stock depletion graphs, and Sprint 2 API documentation | `backend/app/static/sprint-2-demo.html`, `docs/api-reference.md` |

---

## 6. End-to-End Execution Sequence for Sprint 2 API

```
User (Browser / UI)
      │
      │ 1. POST /api/simulation/run { node_id: "SUP-01", duration_days: 14 }
      ▼
Flask API Blueprint (`api/routes/simulation.py`)
      │
      │ 2. Validate payload via Deep's `SimulationRequestSchema`
      ▼
Simulation Service (`services/simulation_service.py`)
      │
      │ 3. Fetch in-memory `SupplyChainGraph` from cache
      ▼
Simulation Engine (`simulation/engine.py`)
      │
      │ 4. Loop Days t = 0 to 30:
      │    - Decrement daily consumption from on-hand stock
      │    - Set SUP-01 inflow = 0 for days [0..14]
      │    - Record daily snapshots
      │    - Detect stockout days
      ▼
Intervention Calculator (`simulation/intervention.py`)
      │
      │ 5. Compute W_intervention = T_stockout - T_curr - RecoveryLeadTime
      │    - Classify: STABLE, WARNING, BREACHED
      ▼
Pydantic Serializer (`schemas/simulation.py`)
      │
      │ 6. Pack into `SimulationResponseSchema`
      ▼
Flask HTTP 200 Response
      │
      │ 7. Return complete timeline JSON (< 25ms SLA)
      ▼
Frontend D3.js Dashboard (`sprint-2-demo.html`)
      - Interactive slider scrub: Watch parts turn from Green to Amber to Red
      - Depletion line graph: Stock plummeting to zero on Day 7
      - Intervention Countdown Badge: "⚠️ 2 Days Remaining to Intervene!"
```

---

## 7. Sprint 2 Acceptance Criteria (ACs) for Quality Sign-Off

- **AC-S2-01 (Deterministic Depletion):** For any BOM Part with on-hand stock $S$ and daily consumption $C$, inventory on Day $t$ without inflow must equal $\max(0, S - C \times t)$.
- **AC-S2-02 (Stockout Timing Accuracy):** Part stockout day must match the theoretical floor value $\lfloor S / C \rfloor$ under zero inflow conditions.
- **AC-S2-03 (Intervention Window Precision):** Calculated $W_{\text{intervention}}$ must be mathematically consistent with $T_{\text{stockout}} - T_{\text{current}} - \text{LeadTime}_{\text{alt}}$.
- **AC-S2-04 (Performance SLA):** Complete 30-day discrete simulation across the canonical graph must execute in under **$25.0\text{ ms}$** on standard host environments.
- **AC-S2-05 (Zero Regression):** All 130 Sprint 1 baseline tests must continue to pass with $100\%$ green status.
- **AC-S2-06 (No Database Dependency):** Simulation must execute purely in RAM using domain state snapshots without adding relational or external database overhead.

---
*End of Sprint 2 Implementation Plan — Prepared for Team PHOTON Review*

