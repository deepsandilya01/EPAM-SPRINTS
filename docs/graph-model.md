# Supply Chain Graph Model

## Overview

RE:Flow models a multi-tier supply chain network as a **Directed Acyclic Graph (DAG)** using `networkx.DiGraph`. Dependencies strictly flow downstream from raw material suppliers to customer order fulfillments across four distinct tiers.

---

## 4-Tier Topological Hierarchy

```
[Tier 1: Suppliers] ──(SUPPLIES)──> [Tier 2: BOM Parts] ──(USED_IN)──> [Tier 3: Finished Products] ──(FULFILLS)──> [Tier 4: Customer Orders]
    (2 nodes)                           (5 nodes)                               (2 nodes)                              (10 nodes)
```

### Canonical Entity Counts (19 Nodes, 21 Edges)

| Entity / Relation | Tier / Transition | Canonical Count | Description |
| :--- | :--- | :--- | :--- |
| **Suppliers** | Tier 1 | **2** | Primary vendors providing raw materials and sub-components (`SUP-01`, `SUP-02`) |
| **BOM Parts** | Tier 2 | **5** | Discrete bill-of-materials components tracked by inventory (`PART-01` to `PART-05`) |
| **Finished Products** | Tier 3 | **2** | Assembled finished goods ready for customer dispatch (`PROD-01`, `PROD-02`) |
| **Customer Orders** | Tier 4 | **10** | Committed client purchase orders with delivery deadlines (`ORD-001` to `ORD-010`) |
| **`SUPPLIES`** | Tier 1 → Tier 2 | **6** | Component procurement relationship from Supplier to Part |
| **`USED_IN`** | Tier 2 → Tier 3 | **5** | Manufacturing consumption relationship from Part into Finished Product |
| **`FULFILLS`** | Tier 3 → Tier 4 | **10** | Order dispatch allocation from Finished Product to Customer Order |

---

## Structural Invariants & Rules

1. **Strict DAG Acyclicity**: The graph must be completely free of directed cycles. Cycles represent impossible circular dependencies in manufacturing (e.g. an assembly depending on its own output).
2. **Strict Tier Transitions**:
   - `SUPPLIES` edges must connect a `supplier` node to a `part` node.
   - `USED_IN` edges must connect a `part` node to a `product` node.
   - `FULFILLS` edges must connect a `product` node to an `order` node.
3. **No Skip-Level Jumps**: A supplier cannot directly fulfill an order or connect to a product. Every relationship must traverse adjacent tiers.
4. **No Backwards Edges**: Downstream entities cannot supply or consume upstream entities.
5. **No Dangling References**: Every edge endpoint (`source` and `target`) must exist as a registered node in the dataset.

---

## Domain Node Models

### Supplier Node (`Tier 1`)
- `id` (`str`): Unique identifier (e.g. `"SUP-01"`)
- `label` (`str`): Display name (e.g. `"Apex Microelectronics"`)
- `supplier_id` (`str`): Identifier matching `id`
- `location` (`str`): Facility location (e.g. `"Taipei, TW"`)
- `reliability_score` (`float`): Historical vendor delivery reliability ($0.0 \le score \le 1.0$)

### BOM Part Node (`Tier 2`)
- `id` (`str`): Unique identifier (e.g. `"PART-01"`)
- `label` (`str`): Component name (e.g. `"Microcontroller Unit (MCU)"`)
- `part_id` (`str`): Identifier matching `id`
- `stock_on_hand` (`int` | `float`): Current physical inventory units
- `daily_consumption` (`int` | `float`): Average daily burn rate
- `days_of_supply` (`float`): Calculated inventory coverage ($stock \div consumption$)
- `criticality` (`str`): Operational priority (`"HIGH"`, `"MEDIUM"`, `"LOW"`)

### Finished Product Node (`Tier 3`)
- `id` (`str`): Unique identifier (e.g. `"PROD-01"`)
- `label` (`str`): Assembled unit name (e.g. `"Industrial Controller Alpha"`)
- `product_id` (`str`): Identifier matching `id`
- `lead_time_days` (`int`): Manufacturing assembly cycle duration in days

### Customer Order Node (`Tier 4`)
- `id` (`str`): Unique identifier (e.g. `"ORD-001"`)
- `label` (`str`): Purchase order label (e.g. `"Acme Robotics Order #1"`)
- `order_id` (`str`): Identifier matching `id`
- `quantity` (`int`): Required shipment units ($quantity > 0$)
- `deadline` (`str`): Committed shipment target date (ISO-8601 or date string)
- `revenue_impact` (`float`): Financial value in USD

