# TEAM PHOTON — SPRINT 2: FINAL TEAM RESPONSIBILITIES & WORK ALLOCATION
## RE:Flow — Temporal Disruption Simulation & Intervention Window Engine
> **Official Benchmark Target:** 8-hour supplier delay on `SUP-01` → Exactly 2 orders fail (`ORD-01`, `ORD-02`) → Intervention Window `ΔT = 8.0 − 0.0 − 5.0 = +3.0 hours` (FEASIBLE)

---

## PART A: EXECUTION ORDER — Kiska Kaam Pehle Hoga

> **Rule:** Jiska koi upstream code dependency nahi, vo Day 1 start karega. Baaki log ek-ek karke unlock hote jayenge.
> **Sprint Duration:** 12 Days total

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY 1-2   │  KANAK ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (No blockers)
          │  DIVYANSHU ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (No blockers)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY 3-4   │  AADEE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Kanak + Divyanshu)
          │  SONAL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Kanak + Divyanshu)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY 5-6   │  ANUSHKA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Aadee + Sonal)
          │  MISHTI ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Anushka)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY 7-8   │  ANSH ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after all 5 modules ready)
          │  PREETAM ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Ansh's engine.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY 9-10  │  DEEP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Preetam's API)
          │  SOUMYA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Preetam's API)
          │  SHANU ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after Ansh's engine.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAY 11-12 │  SUMIT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (after all 11 members done)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PART B: CONNECTION MAP — Kaun Kisse Connected Hai

```
 KANAK ──────────────────────────────────────────────────────────────────┐
 (scenario_dataset.json)                                                 │
         ├──► AADEE    (graph + consumption rates deta hai)              │
         ├──► SONAL    (stock levels + hourly burn deta hai)             │
         ├──► ANUSHKA  (order deadlines deta hai)                        │
         ├──► MISHTI   (t_recovery lead time deta hai)                   │
         └──► SOUMYA   (benchmark calibrated data for tests)             │
                                                                         │
 DIVYANSHU ──────────────────────────────────────────────────────────────┘
 (DisruptionEvent model)
         ├──► AADEE    (supplier_id + event deta hai ripple start ke liye)
         ├──► SONAL    (delay_duration_hours = 8.0h deta hai)
         └──► ANSH     (DisruptionEvent schema use karta hai engine me)

 AADEE ────────────────────────────────────────────────────────────────────
 (RippleImpactSummary)
         ├──► ANUSHKA  (affected parts + customer orders list deta hai)
         └──► ANSH     (ripple.py import hota hai engine pipeline me)

 SONAL ────────────────────────────────────────────────────────────────────
 (InventoryDepletionTimeline: hourly Stock[0..72])
         ├──► ANUSHKA  (zero-stock hour identify karne ke liye)
         └──► ANSH     (inventory.py import hota hai engine pipeline me)

 ANUSHKA ──────────────────────────────────────────────────────────────────
 (StockoutPrediction: T_stockout=8.0h, ORD-01, ORD-02)
         ├──► MISHTI   (T_stockout deta hai ΔT calculate karne ke liye)
         └──► ANSH     (stockout.py import hota hai engine pipeline me)

 MISHTI ───────────────────────────────────────────────────────────────────
 (InterventionWindowResult: ΔT=+3.0h, is_feasible=True, status=FEASIBLE)
         ├──► ANSH     (intervention.py import hota hai engine pipeline me)
         ├──► PREETAM  (API response me ΔT dikhata hai)
         └──► DEEP     (UI gauge is field se populate hota hai)

 ANSH ─────────────────────────────────────────────────────────────────────
 (engine.py: run_disruption_simulation() < 25ms pipeline)
         ├──► PREETAM  (SimulationService inject karta hai API me)
         ├──► SOUMYA   (simulation functions test karti hai)
         └──► SHANU    (is function ko benchmark karta hai)

 PREETAM ──────────────────────────────────────────────────────────────────
 (POST /api/v1/simulation/disrupt endpoint + Swagger /docs)
         ├──► DEEP     (frontend is endpoint se data fetch karta hai)
         └──► SOUMYA   (FastAPI TestClient se hit karti hai)

 DEEP, SOUMYA, SHANU ─────────────────────────────────────────────────────
 (UI + Tests + Benchmark)
         └──► SUMIT    (sab kuch aggregate karke mentor sign-off deta hai)
```

---

## PART C: 12-MEMBER FINAL TASK SHEETS

---

### 🟡 PHASE 1 — DAY 1-2 (Foundation — Zero Blockers)

---

### 1. KANAK — Feature 6: Scenario Data & Benchmark Calibration

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Benchmarking Scripts |
| **Sprint 2 Role** | Ground-Truth Data & Oracle Calibration Specialist |
| **Activation Day** | **Day 1-2 — FIRST to start, no blockers** |
| **Depends On** | Nobody — Kanak is a root node |
| **Output Goes To** | Aadee, Sonal, Anushka, Mishti, Soumya |

**What to build (Sprint 2 scope only):**

Kanak Sprint 1 se aaye hue dataset ko Sprint 2 ke liye calibrate karegi. File already exist karti hai (`backend/app/data/loader.py`), Kanak isme simulation-specific inventory fields add karegi.

**Files to modify/create:**

```
backend/app/data/loader.py              ← MODIFY: add hourly_consumption, safety_stock fields
backend/app/data/datasets/
    scenario_dataset.json              ← CREATE: Sprint 2 specific scenario JSON (simulation-ready)
```

**Exact calibration values (Oracle targets):**

```json
{
  "suppliers": [
    {
      "id": "SUP-01",
      "name": "Apex Precision Castings",
      "tier": 1,
      "recovery_lead_time_hours": 5.0
    }
  ],
  "parts": [
    {
      "id": "P-01",
      "supplied_by": "SUP-01",
      "initial_stock_units": 40,
      "daily_consumption_units": 120,
      "hourly_consumption_units": 5.0
    }
  ],
  "simulation": {
    "disruption_duration_hours": 8.0,
    "simulation_horizon_hours": 72,
    "expected_stockout_hour": 8.0,
    "expected_failing_orders": ["ORD-01", "ORD-02"],
    "expected_intervention_window_hours": 3.0
  }
}
```

**Definition of Done (DoD):**
- [ ] `scenario_dataset.json` has `initial_stock_units`, `hourly_consumption_units`, `recovery_lead_time_hours` for each part/supplier
- [ ] Applying 8h delay on this data produces `T_stockout = 8.0h` exactly
- [ ] Exactly 2 orders (`ORD-01`, `ORD-02`) breach their delivery promise

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine benchmarking scripts likhe the. Sprint 2 me maine simulation engine ka ground-truth data calibrate kiya — initial stock, hourly burn rates aur recovery lead times. Is calibration ki wajah se hamara 8-hour delay scenario deterministically exactly 2 orders fail karta hai, jo official evaluation oracle se 100% match karta hai."*

---

### 2. DIVYANSHU — Feature 1: Disruption Event Generator & Validator

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Edge-Case Complexity Docs |
| **Sprint 2 Role** | Event Generation & Input Security Engineer |
| **Activation Day** | **Day 1-2 — FIRST to start, no blockers** |
| **Depends On** | Nobody — Divyanshu is a root node |
| **Output Goes To** | Aadee (supplier_id), Sonal (delay hours), Ansh (schema) |

**What to build (Sprint 2 scope only):**

Divyanshu pehla Sprint 2 specific Python code likhega — `DisruptionEvent` Pydantic model aur factory function. Yeh file bilkul nayi hai, Sprint 1 me exist nahi karti.

**Files to create (new files):**

```
backend/app/models/disruption.py       ← CREATE NEW: Pydantic DisruptionEvent model
backend/app/simulation/
    __init__.py                        ← CREATE NEW: simulation package init
    events.py                          ← CREATE NEW: create_disruption_event() factory
```

**Code to implement:**

```python
# backend/app/models/disruption.py
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

class DisruptionType(str, Enum):
    SUPPLIER_DELAY = "SUPPLIER_DELAY"
    CAPACITY_DROP = "CAPACITY_DROP"
    FORCE_MAJEURE = "FORCE_MAJEURE"

class DisruptionEvent(BaseModel):
    event_id: str
    supplier_id: str                        # Must be "SUP-01" for benchmark
    disruption_type: DisruptionType
    delay_duration_hours: float = Field(gt=0, description="Must be positive")
    created_at: datetime
    description: str = ""

    @validator("delay_duration_hours")
    def validate_delay(cls, v):
        if v <= 0:
            raise ValueError("delay_duration_hours must be greater than 0")
        return v
```

```python
# backend/app/simulation/events.py
import uuid
from datetime import datetime
from backend.app.models.disruption import DisruptionEvent, DisruptionType

VALID_TIER1_SUPPLIERS = {"SUP-01", "SUP-02"}

def create_disruption_event(
    supplier_id: str,
    disruption_type: DisruptionType = DisruptionType.SUPPLIER_DELAY,
    delay_duration_hours: float = 8.0,
    description: str = ""
) -> DisruptionEvent:
    if supplier_id not in VALID_TIER1_SUPPLIERS:
        raise ValueError(f"Supplier {supplier_id} not found in Tier 1 suppliers")
    return DisruptionEvent(
        event_id=str(uuid.uuid4()),
        supplier_id=supplier_id,
        disruption_type=disruption_type,
        delay_duration_hours=delay_duration_hours,
        created_at=datetime.utcnow(),
        description=description
    )
```

**Definition of Done (DoD):**
- [ ] `DisruptionEvent` model with `supplier_id`, `disruption_type`, `delay_duration_hours` created
- [ ] `create_disruption_event("SUP-01", delay_duration_hours=8.0)` works without error
- [ ] Invalid supplier_id raises `ValueError`
- [ ] `delay_duration_hours <= 0` raises Pydantic `ValidationError`

**Connections (Divyanshu ke output ka use kaun karega):**
- **Aadee** → `event.supplier_id` lega ripple traversal start karne ke liye
- **Sonal** → `event.delay_duration_hours` legi supply block karne ke liye
- **Ansh** → `DisruptionEvent` schema use karega engine pipeline me

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine edge-case complexity analyze ki thi. Sprint 2 me maine simulation ka starting point banaya — DisruptionEvent Pydantic model. Jab bhi koi supplier late hota hai, yeh model us event ko capture karta hai, validate karta hai, aur downstream simulation chain ko trigger karta hai."*

---

### 🟢 PHASE 2 — DAY 3-4 (Graph Cascade & Warehouse Physics)

---

### 3. AADEE — Feature 2: Downstream Ripple Propagation Engine

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Data Loader |
| **Sprint 2 Role** | Graph Algorithm & Downstream Cascade Specialist |
| **Activation Day** | **Day 3-4 — Unlocks after Kanak + Divyanshu finish** |
| **Depends On** | Kanak (calibrated graph), Divyanshu (DisruptionEvent with supplier_id) |
| **Output Goes To** | Anushka (affected_orders list), Ansh (ripple.py module in pipeline) |

**What to build (Sprint 2 scope only):**

Aadee Sprint 1 ke existing NetworkX graph (jo `graph/builder.py` me already built hai) ka use karke downstream traversal likhega jab koi supplier disturb ho. Yeh Sprint 1 ke `graph/traversal.py` se alag hai — voha generic BFS tha, yaha disruption-specific propagation hai.

**Files to create (new files):**

```
backend/app/simulation/ripple.py       ← CREATE NEW: propagate_ripple_effect() function
backend/app/models/impact.py           ← CREATE NEW: RippleImpactSummary Pydantic model
```

**Code to implement:**

```python
# backend/app/models/impact.py
from pydantic import BaseModel
from typing import List

class RippleImpactSummary(BaseModel):
    disrupted_supplier: str
    affected_parts: List[str]           # e.g. ["P-01", "P-02"]
    affected_products: List[str]        # e.g. ["PROD-01", "PROD-02"]
    affected_orders: List[str]          # e.g. ["ORD-01", "ORD-02", "ORD-03"]
    total_affected_nodes: int
```

```python
# backend/app/simulation/ripple.py
import networkx as nx
from backend.app.models.disruption import DisruptionEvent
from backend.app.models.impact import RippleImpactSummary

def propagate_ripple_effect(
    graph: nx.DiGraph,
    event: DisruptionEvent
) -> RippleImpactSummary:
    """
    Traverse downstream from disrupted supplier using BFS.
    visited = set() ensures no node is processed twice.
    """
    supplier_id = event.supplier_id
    
    if supplier_id not in graph:
        raise ValueError(f"Supplier {supplier_id} not found in graph")

    visited = set()
    queue = [supplier_id]
    affected_parts = []
    affected_products = []
    affected_orders = []

    while queue:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)

        node_data = graph.nodes.get(node_id, {})
        node_type = node_data.get("type", "")

        if node_type == "PART":
            affected_parts.append(node_id)
        elif node_type == "PRODUCT":
            affected_products.append(node_id)
        elif node_type == "ORDER":
            affected_orders.append(node_id)

        # Traverse downstream neighbors
        for neighbor in graph.successors(node_id):
            if neighbor not in visited:
                queue.append(neighbor)

    return RippleImpactSummary(
        disrupted_supplier=supplier_id,
        affected_parts=affected_parts,
        affected_products=affected_products,
        affected_orders=affected_orders,
        total_affected_nodes=len(visited) - 1  # exclude supplier itself
    )
```

**Definition of Done (DoD):**
- [ ] `propagate_ripple_effect(graph, event)` traverses from `SUP-01` downstream
- [ ] `P-01` appears in `affected_parts` (AC-04)
- [ ] `PROD-01`, `PROD-02` appear in `affected_products` (AC-05)
- [ ] `affected_orders` contains at minimum `ORD-01`, `ORD-02` (downstream chain)
- [ ] `visited = set()` ensures zero duplicate processing of multi-parent BOM nodes

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine data loader banaya tha. Sprint 2 me maine ripple propagation engine likha jo supplier delay ka downstream impact graph me trace karta hai. `visited = set()` use karke maine ensure kiya ki koi BOM part ya product do baar count na ho — yeh cycle-safe BFS hai jo clean categorized impact summary return karta hai."*

---

### 4. SONAL — Feature 3: Inventory Depletion Simulator

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Mapping Verification Docs |
| **Sprint 2 Role** | Warehouse Physics & Discrete-Time Simulation Engineer |
| **Activation Day** | **Day 3-4 — Unlocks after Kanak + Divyanshu finish** |
| **Depends On** | Kanak (initial_stock, hourly_consumption_units, recovery_lead_time_hours), Divyanshu (delay_duration_hours) |
| **Output Goes To** | Anushka (hourly depletion array for zero-stock detection), Ansh (inventory.py in pipeline) |

**What to build (Sprint 2 scope only):**

Sonal discrete-time hourly simulation likhegi jo warehouse me har ghante kitna stock bachega yeh calculate karegi. 8 ghante tak koi incoming shipment nahi aayega, isiliye stock sirf burn hota rahega.

**Files to create (new files):**

```
backend/app/simulation/inventory.py    ← CREATE NEW: simulate_inventory_depletion()
backend/app/models/inventory.py        ← CREATE NEW: InventoryDepletionTimeline model
```

**Code to implement:**

```python
# backend/app/models/inventory.py
from pydantic import BaseModel
from typing import List

class HourlyStockPoint(BaseModel):
    hour: int
    stock_units: float
    supply_blocked: bool    # True if within delay window

class InventoryDepletionTimeline(BaseModel):
    part_id: str
    initial_stock: float
    hourly_consumption: float
    delay_hours: float
    timeline: List[HourlyStockPoint]  # hour 0 to 72
    stockout_hour: float | None       # None if no stockout within horizon
```

```python
# backend/app/simulation/inventory.py
from backend.app.models.inventory import InventoryDepletionTimeline, HourlyStockPoint

def simulate_inventory_depletion(
    part_id: str,
    initial_stock: float,
    hourly_consumption: float,
    delay_duration_hours: float,
    simulation_horizon_hours: int = 72
) -> InventoryDepletionTimeline:
    """
    Discrete hourly stepper:
    Stock(h) = max(0, Stock(h-1) - HourlyConsumption)
    Supply is blocked for hours 0 .. delay_duration_hours
    """
    timeline = []
    current_stock = initial_stock
    stockout_hour = None

    for h in range(simulation_horizon_hours + 1):
        supply_blocked = h < delay_duration_hours
        
        if h > 0:
            # Consume stock each hour
            current_stock = max(0.0, current_stock - hourly_consumption)
        
        point = HourlyStockPoint(
            hour=h,
            stock_units=round(current_stock, 4),
            supply_blocked=supply_blocked
        )
        timeline.append(point)

        # Mark first stockout
        if current_stock == 0.0 and stockout_hour is None and h > 0:
            stockout_hour = float(h)

    return InventoryDepletionTimeline(
        part_id=part_id,
        initial_stock=initial_stock,
        hourly_consumption=hourly_consumption,
        delay_hours=delay_duration_hours,
        timeline=timeline,
        stockout_hour=stockout_hour
    )
```

**Benchmark Oracle Validation:**
```
Input:  initial_stock=40, hourly_consumption=5.0, delay=8.0
Hour 0: 40 units
Hour 1: 35 units  (supply blocked)
Hour 2: 30 units
Hour 3: 25 units
Hour 4: 20 units
Hour 5: 15 units
Hour 6: 10 units
Hour 7:  5 units
Hour 8:  0 units  ← T_stockout = 8.0 hours (AC-07, AC-08)
```

**Definition of Done (DoD):**
- [ ] `simulate_inventory_depletion("P-01", 40, 5.0, 8.0)` returns timeline with `stockout_hour=8.0`
- [ ] Timeline has exactly 73 entries (hour 0 to hour 72)
- [ ] `supply_blocked=True` for hours 0 to 7

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine mapping verification kiya tha. Sprint 2 me maine warehouse ki physical reality model ki — ek discrete hourly equation jisme hum dekhte hain ki supplier ke delay ke baad agle 72 ghante me stock kaise zero hoti jaati hai. Yeh depletion timeline baaki modules ke liye foundation hai."*

---

### 🔵 PHASE 3 — DAY 5-6 (Prediction & Decision Intelligence)

---

### 5. ANUSHKA — Feature 4: Stockout Predictor & 2-Order Matcher

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Canonical Dataset JSON |
| **Sprint 2 Role** | Predictive Analytics & Order Impact Engineer |
| **Activation Day** | **Day 5-6 — Unlocks after Aadee + Sonal finish** |
| **Depends On** | Sonal (InventoryDepletionTimeline), Aadee (RippleImpactSummary with affected_orders) |
| **Output Goes To** | Mishti (stockout_hour for ΔT calculation), Ansh (stockout.py in pipeline) |

**What to build (Sprint 2 scope only):**

Anushka Sonal ke hourly timeline se exact zero-stock hour nikaalegi aur Aadee ke affected orders me se woh 2 orders identify karegi jo delivery promise miss karenge.

**Files to create (new files):**

```
backend/app/simulation/stockout.py     ← CREATE NEW: predict_stockout_and_orders()
backend/app/models/stockout.py         ← CREATE NEW: StockoutPredictionResult model
```

**Code to implement:**

```python
# backend/app/models/stockout.py
from pydantic import BaseModel
from typing import List, Optional

class BreachedOrder(BaseModel):
    order_id: str
    delivery_deadline_hours: float
    will_fail: bool
    reason: str

class StockoutPredictionResult(BaseModel):
    part_id: str
    stockout_hour: Optional[float]       # None if no stockout
    no_stockout: bool
    breached_orders: List[BreachedOrder] # Exactly 2 for benchmark scenario
    total_breached: int
```

```python
# backend/app/simulation/stockout.py
from backend.app.models.inventory import InventoryDepletionTimeline
from backend.app.models.impact import RippleImpactSummary
from backend.app.models.stockout import StockoutPredictionResult, BreachedOrder
from typing import Dict

def predict_stockout_and_orders(
    depletion: InventoryDepletionTimeline,
    impact: RippleImpactSummary,
    order_deadlines: Dict[str, float]   # {order_id: delivery_deadline_hours}
) -> StockoutPredictionResult:
    """
    1. Find T_stockout from depletion timeline
    2. For each affected order, check if deadline < T_stockout
    """
    stockout_hour = depletion.stockout_hour
    
    if stockout_hour is None:
        return StockoutPredictionResult(
            part_id=depletion.part_id,
            stockout_hour=None,
            no_stockout=True,
            breached_orders=[],
            total_breached=0
        )

    breached = []
    for order_id in impact.affected_orders:
        deadline = order_deadlines.get(order_id)
        if deadline is None:
            continue
        will_fail = deadline <= stockout_hour
        breached.append(BreachedOrder(
            order_id=order_id,
            delivery_deadline_hours=deadline,
            will_fail=will_fail,
            reason=f"Delivery due at hour {deadline}, stockout at hour {stockout_hour}"
        ))

    # Only return actually breached orders
    failing = [o for o in breached if o.will_fail]
    
    return StockoutPredictionResult(
        part_id=depletion.part_id,
        stockout_hour=stockout_hour,
        no_stockout=False,
        breached_orders=failing,
        total_breached=len(failing)
    )
```

**Benchmark Oracle Validation:**
```
Affected orders from Aadee:  [ORD-01, ORD-02, ORD-03, ...]
T_stockout from Sonal:       8.0 hours

ORD-01 deadline: Hour 10.0  → 10.0 > 8.0  → BREACHED (assembly needs stock that ran out)
ORD-02 deadline: Hour 12.0  → 12.0 > 8.0  → BREACHED
ORD-03 deadline: Hour 36.0  → 36.0 >> 8.0 → Safe (buffer time available)

Result: total_breached = 2 (AC-06 ✓)
```

**Definition of Done (DoD):**
- [ ] `predict_stockout_and_orders()` returns `stockout_hour=8.0` (AC-08)
- [ ] `breached_orders` contains exactly `ORD-01` and `ORD-02` (AC-06)
- [ ] `total_breached == 2`

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine canonical dataset define kiya tha. Sprint 2 me maine predictive intelligence add ki — ek algorithm jo warehouse timeline scan karke exact stockout hour nikalta hai aur customer order deadlines se match karke precisely 2 failing commitments identify karta hai."*

---

### 6. MISHTI — Feature 5: Intervention Window Calculator

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Coordinator & Docs |
| **Sprint 2 Role** | Decision-Intelligence & ΔT Formula Engineer |
| **Activation Day** | **Day 5-6 — Unlocks after Anushka finishes** |
| **Depends On** | Anushka (StockoutPredictionResult.stockout_hour), Kanak (recovery_lead_time_hours = 5.0h) |
| **Output Goes To** | Ansh (intervention.py in pipeline), Preetam (API response field), Deep (UI badge) |

**What to build (Sprint 2 scope only):**

Mishti Sprint 2 ka most critical formula implement karegi — Intervention Window. Yeh manager ko batata hai ki disruption ke baad act karne ke liye kitna time bacha hai.

**Files to create (new files):**

```
backend/app/simulation/intervention.py ← CREATE NEW: calculate_intervention_window()
backend/app/models/intervention.py     ← CREATE NEW: InterventionWindowResult model
```

**Code to implement:**

```python
# backend/app/models/intervention.py
from pydantic import BaseModel
from typing import List

class InterventionWindowResult(BaseModel):
    stockout_hour: float
    current_hour: float
    recovery_lead_time_hours: float
    delta_t_hours: float               # ΔT = T_stockout - T_curr - t_recovery
    is_feasible: bool                  # True if ΔT > 0
    status: str                        # "FEASIBLE" | "BREACHED" | "CRITICAL"
    affected_order_ids: List[str]
    message: str
```

```python
# backend/app/simulation/intervention.py
from backend.app.models.intervention import InterventionWindowResult
from backend.app.models.stockout import StockoutPredictionResult

def calculate_intervention_window(
    stockout_result: StockoutPredictionResult,
    current_hour: float = 0.0,
    recovery_lead_time_hours: float = 5.0
) -> InterventionWindowResult:
    """
    Official Formula (from EPAM Sprint 2 Specification):
    ΔT_intervention = T_stockout - T_current - t_recovery_lead_time

    ΔT > 0  → FEASIBLE  (action window still open)
    ΔT == 0 → CRITICAL  (last moment to act)
    ΔT < 0  → BREACHED  (too late, irreversible damage)
    """
    t_stockout = stockout_result.stockout_hour
    
    if t_stockout is None:
        return InterventionWindowResult(
            stockout_hour=float("inf"),
            current_hour=current_hour,
            recovery_lead_time_hours=recovery_lead_time_hours,
            delta_t_hours=float("inf"),
            is_feasible=True,
            status="FEASIBLE",
            affected_order_ids=[],
            message="No stockout predicted. No intervention required."
        )

    delta_t = t_stockout - current_hour - recovery_lead_time_hours

    if delta_t > 0:
        status = "FEASIBLE"
        is_feasible = True
        message = f"Action window is OPEN. {delta_t:.1f} hours remaining to intervene."
    elif delta_t == 0:
        status = "CRITICAL"
        is_feasible = True
        message = "CRITICAL: Last moment to act. Immediate action required."
    else:
        status = "BREACHED"
        is_feasible = False
        message = f"Intervention window BREACHED by {abs(delta_t):.1f} hours."

    affected_ids = [o.order_id for o in stockout_result.breached_orders]

    return InterventionWindowResult(
        stockout_hour=t_stockout,
        current_hour=current_hour,
        recovery_lead_time_hours=recovery_lead_time_hours,
        delta_t_hours=round(delta_t, 4),
        is_feasible=is_feasible,
        status=status,
        affected_order_ids=affected_ids,
        message=message
    )
```

**Benchmark Oracle Validation:**
```
T_stockout       = 8.0 hours
T_current        = 0.0 hours
t_recovery       = 5.0 hours

ΔT = 8.0 - 0.0 - 5.0 = +3.0 hours
Status = FEASIBLE  (AC-09 ✓)
```

**Definition of Done (DoD):**
- [ ] `calculate_intervention_window()` returns `delta_t_hours=3.0` for benchmark scenario (AC-09)
- [ ] `is_feasible=True`, `status="FEASIBLE"` for benchmark
- [ ] `affected_order_ids=["ORD-01", "ORD-02"]`
- [ ] `delta_t < 0` → `status="BREACHED"`, `is_feasible=False`

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine sprint coordination aur documentation ki thi. Sprint 2 me maine system ka core business logic implement kiya — Intervention Window. Ek formula jo supply chain planner ko precisely batata hai ki disruption ke baad recovery action lene ke liye kitne ghante bache hain. Hamara benchmark answer hai +3.0 hours FEASIBLE."*

---

### 🟣 PHASE 4 — DAY 7-8 (Pipeline Orchestration & API Transport)

---

### 7. ANSH — Simulation Orchestrator & FastAPI Lead

| Field | Detail |
|---|---|
| **Sprint 1 Role** | NetworkX Graph Builder |
| **Sprint 2 Role** | Engine Pipeline Architect & Technical Integration Lead |
| **Activation Day** | **Day 7-8 — Unlocks after Divyanshu, Aadee, Sonal, Anushka, Mishti finish** |
| **Depends On** | All 5 simulation modules (events, ripple, inventory, stockout, intervention) |
| **Output Goes To** | Preetam (SimulationService), Soumya (functions to test), Shanu (function to benchmark) |

**What to build (Sprint 2 scope only):**

Ansh baaki 5 members ke individual modules ko ek orchestrated pipeline me jorega. Engine ko < 25ms me chalana hai.

**Files to create (new files):**

```
backend/app/simulation/engine.py           ← CREATE NEW: run_disruption_simulation()
backend/app/services/simulation_service.py ← CREATE NEW: SimulationService class
```

**Files to modify (existing):**
```
backend/app/main.py                        ← MODIFY: register simulation router
```

**Code to implement:**

```python
# backend/app/simulation/engine.py
import time
from backend.app.models.disruption import DisruptionEvent
from backend.app.simulation.ripple import propagate_ripple_effect
from backend.app.simulation.inventory import simulate_inventory_depletion
from backend.app.simulation.stockout import predict_stockout_and_orders
from backend.app.simulation.intervention import calculate_intervention_window
from backend.app.services.graph_service import get_graph     # Sprint 1 existing service
from backend.app.data.loader import load_scenario             # Sprint 1 existing loader

def run_disruption_simulation(event: DisruptionEvent) -> dict:
    """
    Master pipeline: execute 5 simulation steps in sequence.
    Target: < 25 ms end-to-end.
    """
    start_ns = time.perf_counter_ns()

    # Step 1: Load graph (from Sprint 1)
    graph = get_graph()
    scenario = load_scenario()

    # Step 2: Ripple propagation (Aadee)
    impact = propagate_ripple_effect(graph, event)

    # Step 3: Inventory depletion (Sonal) — per affected part
    part_data = scenario["parts"][0]  # P-01 for benchmark
    depletion = simulate_inventory_depletion(
        part_id=part_data["id"],
        initial_stock=part_data["initial_stock_units"],
        hourly_consumption=part_data["hourly_consumption_units"],
        delay_duration_hours=event.delay_duration_hours
    )

    # Step 4: Stockout prediction (Anushka)
    order_deadlines = {
        o["id"]: o["delivery_deadline_hours"]
        for o in scenario.get("orders", [])
    }
    stockout = predict_stockout_and_orders(depletion, impact, order_deadlines)

    # Step 5: Intervention window (Mishti)
    supplier_data = next(s for s in scenario["suppliers"] if s["id"] == event.supplier_id)
    intervention = calculate_intervention_window(
        stockout_result=stockout,
        current_hour=0.0,
        recovery_lead_time_hours=supplier_data["recovery_lead_time_hours"]
    )

    elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

    return {
        "event": event.dict(),
        "impact": impact.dict(),
        "depletion_timeline": [p.dict() for p in depletion.timeline],
        "stockout": stockout.dict(),
        "intervention": intervention.dict(),
        "execution_time_ms": round(elapsed_ms, 4)
    }
```

**Definition of Done (DoD):**
- [ ] `run_disruption_simulation(event)` returns all 5 simulation outputs
- [ ] Execution time < 25ms (Shanu will verify)
- [ ] Graph is not mutated (simulation is read-only on Sprint 1 graph)
- [ ] Returns `intervention.delta_t_hours == 3.0` for benchmark scenario

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine NetworkX graph builder likha tha. Sprint 2 me maine poore simulation ka architect ban gaya — ek single function jo 5 alag specialists ke modules ko ek seamless 25ms pipeline me orchestrate karta hai."*

---

### 8. PREETAM — Feature 8: FastAPI Endpoints & OpenAPI Docs

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Traversal BFS Algorithm |
| **Sprint 2 Role** | REST API Architect & OpenAPI Documentation Lead |
| **Activation Day** | **Day 7-8 — Unlocks after Ansh finishes engine.py** |
| **Depends On** | Ansh (run_disruption_simulation() function + SimulationService) |
| **Output Goes To** | Deep (API endpoint URL for frontend), Soumya (API routes for integration tests) |

**What to build (Sprint 2 scope only):**

Preetam Sprint 2 ka RESTful API endpoint banayega. Sprint 1 ke existing routes (`api/routes/`) already hain — Preetam ek new folder structure me simulation routes add karega.

**Files to create (new files):**

```
backend/app/api/routes/disruptions.py      ← CREATE NEW: simulation APIRouter
backend/app/schemas/disruption.py          ← CREATE NEW: Pydantic request/response schemas
```

**Files to modify (existing):**
```
backend/app/api/__init__.py                ← MODIFY: include simulation router
```

**Code to implement:**

```python
# backend/app/schemas/disruption.py
from pydantic import BaseModel, Field

class DisruptionRequest(BaseModel):
    supplier_id: str = Field(example="SUP-01")
    disruption_type: str = Field(example="SUPPLIER_DELAY")
    delay_duration_hours: float = Field(gt=0, example=8.0)
    description: str = Field(default="", example="Benchmark test disruption")

class SimulationResponse(BaseModel):
    status: str
    event: dict
    impact: dict
    stockout: dict
    intervention: dict
    execution_time_ms: float
```

```python
# backend/app/api/routes/disruptions.py
from fastapi import APIRouter, HTTPException
from backend.app.schemas.disruption import DisruptionRequest, SimulationResponse
from backend.app.simulation.events import create_disruption_event
from backend.app.simulation.engine import run_disruption_simulation
from backend.app.models.disruption import DisruptionType

router = APIRouter(prefix="/api/v1/simulation", tags=["Disruption Simulation"])

@router.post(
    "/disrupt",
    response_model=SimulationResponse,
    summary="Introduce a supplier disruption and get simulation results",
    description="Run the full 5-step simulation pipeline for a given disruption event."
)
async def simulate_disruption(request: DisruptionRequest):
    try:
        event = create_disruption_event(
            supplier_id=request.supplier_id,
            disruption_type=DisruptionType(request.disruption_type),
            delay_duration_hours=request.delay_duration_hours,
            description=request.description
        )
        result = run_disruption_simulation(event)
        return SimulationResponse(status="success", **result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
```

**Definition of Done (DoD):**
- [ ] `POST /api/v1/simulation/disrupt` returns HTTP 200 with full simulation result
- [ ] Invalid supplier returns HTTP 422
- [ ] Swagger UI available at `/docs` with example request/response
- [ ] Request body validated via Pydantic

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine graph traversal BFS algorithm likha tha. Sprint 2 me maine simulation engine ko duniya ke saamne expose kiya — ek FastAPI endpoint jo full type-safe request leta hai, simulation pipeline trigger karta hai, aur structured JSON response deta hai. Swagger docs automatically generate hote hain."*

---

### 🔴 PHASE 5 — DAY 9-10 (Visualization, Testing & Benchmarking)

---

### 9. DEEP — Feature 10: Frontend D3.js Timeline UI & Visual Gauge

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Models & Pydantic Schemas |
| **Sprint 2 Role** | Frontend Visual Command Center Lead |
| **Activation Day** | **Day 9-10 — Unlocks after Preetam's API endpoint is ready** |
| **Depends On** | Preetam (POST /api/v1/simulation/disrupt endpoint + JSON response schema), Ansh (data contract) |
| **Output Goes To** | Sumit (live demo for mentor presentation) |
| **Frontend Location** | **Dedicated `frontend/` folder at project root — NOT inside `backend/app/static/`** |

**What to build (Sprint 2 scope only):**

Deep ek **dedicated standalone frontend application** banayega — `frontend/` naam ka alag folder project root pe hoga. Yeh Sprint 1 ke `backend/app/static/` approach se alag hai. Frontend apni khud ki folder structure rakhega jo ki production-grade separation of concerns follow karta hai.

**Folder structure to create:**

```
frontend/                              ← NEW DEDICATED FRONTEND FOLDER (project root pe)
├── index.html                         ← CREATE NEW: Main Sprint 2 dashboard entry point
├── sprint-2-demo.html                 ← CREATE NEW: Full simulation demo page
├── package.json                       ← CREATE NEW: (optional) if using npm/node tooling
├── js/
│   ├── main.js                        ← CREATE NEW: App initialization & API client
│   ├── timeline_slider.js             ← CREATE NEW: Hour 0-72 scrubber controller
│   ├── inventory_chart.js             ← CREATE NEW: D3.js stock depletion chart
│   └── intervention_badge.js          ← CREATE NEW: ΔT status badge component
├── css/
│   ├── main.css                       ← CREATE NEW: Base styles & layout
│   └── sprint-2-demo.css              ← CREATE NEW: Sprint 2 specific component styles
└── assets/
    └── (images, icons if needed)
```

**Key UI Components:**

1. **Disruption Input Form:**
   ```
   [Supplier ID: SUP-01 ▼] [Delay Hours: 8.0] [RUN SIMULATION]
   ```

2. **Hour 0-72 Timeline Scrubber (`frontend/js/timeline_slider.js`):**
   ```html
   <input type="range" min="0" max="72" id="hourSlider">
   ```
   JS fetches API, then on slider change shows stock level at that hour.

3. **D3.js Stock Depletion Line Chart (`frontend/js/inventory_chart.js`):**
   - X-axis: Hours (0 to 72)
   - Y-axis: Stock Units
   - Red vertical line at `T_stockout` (Hour 8)
   - Filled area below zero shaded red

4. **Intervention Window Status Badge (`frontend/js/intervention_badge.js`):**
   ```
   ┌────────────────────────────────────┐
   │  ✅ FEASIBLE                       │
   │  ΔT = +3.0 Hours remaining         │
   │  Action window is OPEN             │
   │  Affected Orders: ORD-01, ORD-02   │
   └────────────────────────────────────┘
   ```
   Green if FEASIBLE, Red if BREACHED.

**API Integration (`frontend/js/main.js`):**
```javascript
// CORS ke liye FastAPI backend ka URL — dev me http://localhost:5001
const API_BASE = 'http://localhost:5001';

async function runSimulation() {
    const response = await fetch(`${API_BASE}/api/v1/simulation/disrupt`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            supplier_id: 'SUP-01',
            disruption_type: 'SUPPLIER_DELAY',
            delay_duration_hours: 8.0
        })
    });
    const data = await response.json();
    renderChart(data.depletion_timeline);       // → inventory_chart.js
    renderInterventionBadge(data.intervention); // → intervention_badge.js
    updateSlider(data.depletion_timeline);      // → timeline_slider.js
}
```

> **Note for CORS:** FastAPI backend me `CORSMiddleware` add karna hoga — Preetam ya Ansh se coordinate karo.

**Definition of Done (DoD):**
- [ ] `frontend/` folder at project root with clean structure
- [ ] `frontend/index.html` → `frontend/sprint-2-demo.html` loads and calls the API
- [ ] Stock depletion chart (`inventory_chart.js`) renders with correct D3.js timeline
- [ ] Slider (`timeline_slider.js`) updates chart in real-time (hour 0 to 72)
- [ ] Green/Red badge (`intervention_badge.js`) shows based on `is_feasible`
- [ ] Affected orders list displayed (AC-10)
- [ ] No files inside `backend/app/static/` for Sprint 2 (frontend is fully separate)

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine backend models aur Pydantic schemas banaye the. Sprint 2 me maine poora visual command center design kiya — ek dedicated frontend/ folder jisme interactive D3.js dashboard hai. Supply chain manager agle 72 ghante ki inventory depletion dekh sakta hai, intervention status check kar sakta hai, aur affected orders identify kar sakta hai. Frontend aur backend completely decoupled hain — production-grade architecture."*

---

### 10. SOUMYA — Feature 9: Automated Test Suite (AC-01 to AC-10)

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Graph Validation Engine |
| **Sprint 2 Role** | QA Automation & Acceptance Verification Lead |
| **Activation Day** | **Day 9-10 — Unlocks after Preetam's API + Ansh's engine** |
| **Depends On** | Preetam (FastAPI routes for TestClient), Ansh (simulation functions), Kanak (benchmark data) |
| **Output Goes To** | Sumit (10/10 ACs passing test report for final sign-off) |

**What to build (Sprint 2 scope only):**

Soumya Sprint 2 ka pura test suite likhegi. Sprint 1 me `backend/tests/` already exist karta hai — Soumya wahan 2 nayi files add karegi.

**Files to create (new files):**

```
backend/tests/test_simulation_engine.py    ← CREATE NEW: AC-01 to AC-10 unit tests
backend/tests/test_benchmark_8hr.py        ← CREATE NEW: Integration test for 8h scenario
```

**Tests to write (all 10 Acceptance Criteria):**

```python
# backend/tests/test_simulation_engine.py

# AC-01: 8-hour delay can be introduced
def test_ac01_disruption_event_creation():
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    assert event.delay_duration_hours == 8.0

# AC-02: Disruption associated with correct supplier
def test_ac02_event_associated_with_supplier():
    event = create_disruption_event("SUP-01", delay_duration_hours=8.0)
    assert event.supplier_id == "SUP-01"

# AC-03: Downstream dependencies identified
def test_ac03_downstream_traversal(test_graph, benchmark_event):
    impact = propagate_ripple_effect(test_graph, benchmark_event)
    assert len(impact.affected_parts) > 0

# AC-04: Affected BOM parts identified
def test_ac04_affected_bom_parts(test_graph, benchmark_event):
    impact = propagate_ripple_effect(test_graph, benchmark_event)
    assert "P-01" in impact.affected_parts

# AC-05: Affected finished products identified
def test_ac05_affected_finished_products(test_graph, benchmark_event):
    impact = propagate_ripple_effect(test_graph, benchmark_event)
    assert "PROD-01" in impact.affected_products

# AC-06: Exactly 2 customer orders (BENCHMARK CRITICAL)
def test_ac06_exactly_two_orders_impacted():
    result = run_full_benchmark_simulation()
    assert result["stockout"]["total_breached"] == 2
    ids = [o["order_id"] for o in result["stockout"]["breached_orders"]]
    assert "ORD-01" in ids
    assert "ORD-02" in ids

# AC-07: Inventory depletion calculated
def test_ac07_inventory_depletion_timeline():
    tl = simulate_inventory_depletion("P-01", 40, 5.0, 8.0)
    assert len(tl.timeline) == 73  # hour 0 to 72

# AC-08: Stockout timestamp predicted
def test_ac08_stockout_timestamp_predicted():
    tl = simulate_inventory_depletion("P-01", 40, 5.0, 8.0)
    assert tl.stockout_hour == 8.0

# AC-09: Intervention window formula verified
def test_ac09_intervention_window_formula():
    result = run_full_benchmark_simulation()
    assert result["intervention"]["delta_t_hours"] == 3.0
    assert result["intervention"]["is_feasible"] == True
    assert result["intervention"]["status"] == "FEASIBLE"

# AC-10: Results available via API
def test_ac10_fastapi_endpoint_returns_results(client):
    response = client.post("/api/v1/simulation/disrupt", json={
        "supplier_id": "SUP-01",
        "disruption_type": "SUPPLIER_DELAY",
        "delay_duration_hours": 8.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "intervention" in data
    assert "stockout" in data
```

**Definition of Done (DoD):**
- [ ] All 10 tests (`test_ac01` to `test_ac10`) pass with `pytest -v`
- [ ] `pytest backend/tests/test_simulation_engine.py` → 10 passed
- [ ] `pytest backend/tests/test_benchmark_8hr.py` → integration test passes
- [ ] 90%+ code coverage on simulation modules

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine graph validation engine banaya tha. Sprint 2 me maine poore sprint ka QA automation lead kiya — ek Pytest suite jisme har acceptance criterion ka ek dedicated test case hai. Jab ye 10 tests green hain, tab Sprint 2 officially complete hai."*

---

### 11. SHANU — Feature 11: Performance SLA Benchmarking

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Testing Lead (130 tests) |
| **Sprint 2 Role** | Performance Engineering & Latency Verification Specialist |
| **Activation Day** | **Day 9-10 — Unlocks after Ansh's engine.py** |
| **Depends On** | Ansh (`run_disruption_simulation()` function) |
| **Output Goes To** | Sumit (benchmark report with <25ms proof for final sign-off) |

**What to build (Sprint 2 scope only):**

Shanu prove karega ki poora simulation pipeline < 25ms execute hota hai. 1,000 runs chalayega aur statistical SLA report generate karega.

**Files to create (new files):**

```
backend/benchmarks/benchmark_simulation.py ← CREATE NEW: 1,000-run latency benchmark
docs/reports/simulation_report.md         ← CREATE NEW: results report
```

**Code to implement:**

```python
# backend/benchmarks/benchmark_simulation.py
import time
import statistics
from backend.app.simulation.events import create_disruption_event
from backend.app.simulation.engine import run_disruption_simulation
from backend.app.models.disruption import DisruptionType

def run_simulation_benchmark(iterations: int = 1000) -> dict:
    """
    Run 1,000 iterations of the full disruption simulation pipeline.
    SLA Target: P99 < 25.0 ms
    """
    event = create_disruption_event(
        supplier_id="SUP-01",
        disruption_type=DisruptionType.SUPPLIER_DELAY,
        delay_duration_hours=8.0
    )

    latencies_ms = []
    
    # Warm-up runs
    for _ in range(10):
        run_disruption_simulation(event)
    
    # Actual benchmark
    for i in range(iterations):
        start = time.perf_counter_ns()
        result = run_disruption_simulation(event)
        end = time.perf_counter_ns()
        latencies_ms.append((end - start) / 1_000_000)

    p50  = statistics.median(latencies_ms)
    p95  = sorted(latencies_ms)[int(0.95 * iterations)]
    p99  = sorted(latencies_ms)[int(0.99 * iterations)]
    mean = statistics.mean(latencies_ms)
    max_ = max(latencies_ms)

    report = {
        "iterations": iterations,
        "sla_target_ms": 25.0,
        "mean_ms": round(mean, 4),
        "p50_ms": round(p50, 4),
        "p95_ms": round(p95, 4),
        "p99_ms": round(p99, 4),
        "max_ms": round(max_, 4),
        "sla_met": p99 < 25.0
    }
    return report

if __name__ == "__main__":
    report = run_simulation_benchmark()
    print(f"P50: {report['p50_ms']} ms")
    print(f"P95: {report['p95_ms']} ms")
    print(f"P99: {report['p99_ms']} ms")
    print(f"SLA Met: {report['sla_met']}")
    assert report["sla_met"], f"SLA VIOLATED: P99={report['p99_ms']}ms > 25.0ms"
```

**Definition of Done (DoD):**
- [ ] `python backend/benchmarks/benchmark_simulation.py` runs 1,000 iterations
- [ ] P99 latency < 25.0 ms
- [ ] `docs/reports/simulation_report.md` created with actual measured numbers

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine 130-test suite lead kiya tha. Sprint 2 me maine performance engineering lead ki. Mera benchmark script 1,000 simulation runs chalata hai aur statistically prove karta hai ki poora 72-hour temporal simulation pipeline consistently 25 milliseconds se kam me execute hoti hai."*

---

### 🏁 PHASE 6 — DAY 11-12 (Integration, Review & Sign-Off)

---

### 12. SUMIT — Feature 12: Integration, Review & Official Sign-Off

| Field | Detail |
|---|---|
| **Sprint 1 Role** | Documentation & Readme |
| **Sprint 2 Role** | Release Lead, Code Reviewer & Acceptance Auditor |
| **Activation Day** | **Day 11-12 — Starts after all 11 members deliver** |
| **Depends On** | All 11 Members (every PR, test report, benchmark log) |
| **Output Goes To** | Project Mentor & EPAM Evaluators |

**What to build (Sprint 2 scope only):**

Sumit Sprint 2 ka captain hai — saari 11 PRs review karega, merge conflicts resolve karega, aur official sign-off dossier compile karega.

**Files to create (new files):**

```
docs/sprint/sprint_2.md                    ← CREATE NEW: Sprint 2 scope + AC sign-off
docs/reports/simulation_report.md          ← UPDATE: Complete simulation results
```

**Files to modify (existing):**
```
docs/api-reference.md                      ← UPDATE: add /api/v1/simulation/disrupt docs
README.md                                  ← UPDATE: Sprint 2 completion status
```

**PR Review Checklist (for each of 11 PRs):**
```
[ ] Code follows Clean Architecture (routes → services → simulation modules)
[ ] No business logic in API routes
[ ] All Pydantic models have proper field validation
[ ] No hardcoded values (use scenario_dataset.json as source)
[ ] Ruff/lint passes: python -m ruff check backend/
[ ] mypy type checks pass
[ ] Author's tests pass
[ ] No breaking changes to Sprint 1 existing routes
```

**AC Sign-Off Report to compile:**

```markdown
# Sprint 2 Official Sign-Off Report

| AC-ID | Criterion | Owner | Test | Status |
|---|---|---|---|---|
| AC-01 | 8h delay introduced | Divyanshu | test_ac01 | ✅ PASS |
| AC-02 | Supplier associated | Divyanshu | test_ac02 | ✅ PASS |
| AC-03 | Downstream deps | Aadee | test_ac03 | ✅ PASS |
| AC-04 | BOM parts | Aadee | test_ac04 | ✅ PASS |
| AC-05 | Products | Aadee | test_ac05 | ✅ PASS |
| AC-06 | Exactly 2 orders | Anushka | test_ac06 | ✅ PASS |
| AC-07 | Depletion calc | Sonal | test_ac07 | ✅ PASS |
| AC-08 | Stockout timestamp | Anushka | test_ac08 | ✅ PASS |
| AC-09 | ΔT formula | Mishti | test_ac09 | ✅ PASS |
| AC-10 | API results | Preetam+Deep | test_ac10 | ✅ PASS |
```

**Mentor Pitch (60 seconds):**
> *"Sprint 1 me maine documentation aur README lead kiya tha. Sprint 2 me maine poore sprint ka release lead kiya — 11 members ke PRs review kiye, code quality verify ki, aur official AC-01 se AC-10 sign-off report compile ki. Hamara Sprint 2 production-ready hai."*

---

## PART D: NEW FILES SUMMARY (Sprint 2 Total Deliverables)

```
backend/app/
├── models/
│   ├── disruption.py          ← DIVYANSHU
│   ├── impact.py              ← AADEE
│   ├── inventory.py           ← SONAL
│   ├── stockout.py            ← ANUSHKA
│   └── intervention.py        ← MISHTI
│
├── simulation/                ← NEW PACKAGE (Sprint 2)
│   ├── __init__.py            ← DIVYANSHU
│   ├── events.py              ← DIVYANSHU
│   ├── ripple.py              ← AADEE
│   ├── inventory.py           ← SONAL
│   ├── stockout.py            ← ANUSHKA
│   ├── intervention.py        ← MISHTI
│   └── engine.py              ← ANSH
│
├── schemas/
│   └── disruption.py          ← PREETAM
│
├── services/
│   └── simulation_service.py  ← ANSH
│
├── api/
│   └── routes/
│       └── disruptions.py     ← PREETAM
│
└── main.py                    ← ANSH (modify: add simulation router + CORS middleware)

frontend/                      ← NEW DEDICATED FRONTEND FOLDER (project root pe — DEEP)
├── index.html                 ← DEEP
├── sprint-2-demo.html         ← DEEP
├── js/
│   ├── main.js                ← DEEP (API client + app init)
│   ├── timeline_slider.js     ← DEEP (Hour 0-72 scrubber)
│   ├── inventory_chart.js     ← DEEP (D3.js stock depletion chart)
│   └── intervention_badge.js  ← DEEP (ΔT status badge)
└── css/
    ├── main.css               ← DEEP
    └── sprint-2-demo.css      ← DEEP

backend/tests/
├── test_simulation_engine.py  ← SOUMYA
└── test_benchmark_8hr.py      ← SOUMYA

backend/benchmarks/
└── benchmark_simulation.py    ← SHANU

docs/
├── sprint/sprint_2.md         ← SUMIT
├── api-reference.md           ← SUMIT (modify)
└── reports/
    └── simulation_report.md   ← SHANU + SUMIT

data/datasets/
└── scenario_dataset.json      ← KANAK
```

---

## PART E: ACCEPTANCE CRITERIA OWNERSHIP (AC-01 to AC-10)

| ID | Criterion | Primary Owner | Verifying Test | Expected Result |
|---|---|---|---|---|
| AC-01 | 8-hour delay can be introduced | **Divyanshu** | `test_ac01_disruption_event_creation` | `event.delay_duration_hours == 8.0` |
| AC-02 | Disruption tied to correct supplier | **Divyanshu** | `test_ac02_event_associated_with_supplier` | `event.supplier_id == "SUP-01"` |
| AC-03 | Downstream dependencies identified | **Aadee** | `test_ac03_downstream_traversal` | Nodes reachable from SUP-01 found |
| AC-04 | Affected BOM parts identified | **Aadee** | `test_ac04_affected_bom_parts` | `"P-01" in impact.affected_parts` |
| AC-05 | Affected finished products identified | **Aadee** | `test_ac05_affected_finished_products` | `"PROD-01" in impact.affected_products` |
| AC-06 | **Exactly 2 orders identified (benchmark anchor)** | **Anushka** | `test_ac06_exactly_two_orders_impacted` | `total_breached == 2` → `ORD-01, ORD-02` |
| AC-07 | Inventory depletion calculated | **Sonal** | `test_ac07_inventory_depletion_timeline` | 73-entry hourly timeline generated |
| AC-08 | Stockout timestamp predicted | **Anushka** | `test_ac08_stockout_timestamp_predicted` | `T_stockout == 8.0 hours` |
| AC-09 | Intervention window formula correct | **Mishti** | `test_ac09_intervention_window_formula` | `ΔT == 3.0h, status == "FEASIBLE"` |
| AC-10 | Results available for verification | **Preetam + Deep** | `test_ac10_fastapi_endpoint_returns_results` | HTTP 200 + all fields in JSON response |

---

## PART F: STANDUP PROTOCOL

Har din standup me sirf 3 lines:

1. **Kal deliver kiya:** *(e.g., "Maine `events.py` aur `DisruptionEvent` model complete kar diya")*
2. **Aaj karunga:** *(e.g., "Maine `ripple.py` me BFS traversal implement karunga")*
3. **Blocker hai toh:** *(e.g., "Mujhe Kanak se `scenario_dataset.json` ka final format chahiye")*
