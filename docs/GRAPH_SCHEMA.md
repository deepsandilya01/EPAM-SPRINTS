# Team Photon — Graph Data Schema & Specification

## 1. Domain Model & Dependency Flow

The Team Photon supply-chain architecture models physical and contractual dependencies as a **Directed Acyclic Graph (DAG)**. Physical materials and assembly steps move strictly left-to-right across four discrete tiers:

$$\text{Tier 0: Supplier} \xrightarrow{\text{supplies}} \text{Tier 1: Part} \xrightarrow{\text{used\_in}} \text{Tier 2: Product} \xrightarrow{\text{fulfills}} \text{Tier 3: Customer Order}$$

### 1.1 Structural Invariants
1. **Unidirectional Flow**: Edges strictly connect lower tiers to higher tiers. No feedback loops, reverse flows, or intra-tier connections are permitted in the canonical model.
2. **Acyclicity**: The canonical graph must contain zero directed cycles ($\text{DAG} = \text{True}$).
3. **Multi-Sourcing & Multi-Assembly**:
   - `PART-05` (Fastener Kit) is multi-sourced from both `SUP-01` and `SUP-02`.
   - `PROD-01` depends on multiple parts (`PART-01`, `PART-02`, `PART-05`).
   - Multiple customer orders can be fulfilled by a single product line.

---

## 2. Canonical Baseline Metrics

The canonical dataset ([`photon_sprint1_graph_data.json`](../backend/data/photon_sprint1_graph_data.json)) defines the following verified baseline counts:

### Node Counts by Entity Type
| Entity Category | Node Kind | Key in JSON | Baseline Count | ID Prefix / Pattern |
|---|---|---|---:|---|
| **Suppliers** | `supplier` | `nodes.suppliers` | **2** | `SUP-XX` (e.g., `SUP-01`, `SUP-02`) |
| **Parts** | `part` | `nodes.parts` | **5** | `PART-XX` (e.g., `PART-01` to `PART-05`) |
| **Finished Products** | `product` | `nodes.products` | **2** | `PROD-XX` (e.g., `PROD-01`, `PROD-02`) |
| **Customer Orders** | `order` | `nodes.orders` | **10** | `ORD-XX` (e.g., `ORD-01` to `ORD-10`) |
| **Total Nodes** | — | — | **19** | — |

### Edge Counts by Relationship Type
| Relationship Name | JSON Key | Source Kind | Target Kind | Baseline Count | Relation Attribute |
|---|---|---|---|---:|---|
| `supplies` | `edges.supplies` | `supplier` | `part` | **6** | `"SUPPLIES"` |
| `used_in` | `edges.used_in` | `part` | `product` | **5** | `"USED_IN"` |
| `fulfills` | `edges.fulfills` | `product` | `order` | **10** | `"FULFILLS"` |
| **Total Edges** | — | — | — | **21** | — |

---

## 3. Node Schema Specification

Every node across all categories must provide three universal fields:
- `id` (`string`, non-empty): Unique identifier across the entire graph.
- `kind` (`string`): Entity classification (`"supplier"`, `"part"`, `"product"`, or `"order"`).
- `label` (`string`, non-empty): Human-readable display label.

### 3.1 Supplier Nodes
Vendors supplying parts or raw materials.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `id` | string | Yes | Unique node identifier | `"SUP-01"` |
| `kind` | string | Yes | Must be `"supplier"` | `"supplier"` |
| `label` | string | Yes | Display title | `"Apex Components"` |
| `supplier_id` | string | Yes | Entity business ID | `"SUP-01"` |
| `name` | string | Yes | Vendor legal name | `"Apex Components"` |
| `location` | string | Yes | Geographic location / city | `"Pune"` |
| `note` | string | No | Operational notes | `"Primary supplier, electronics"` |

```json
{
  "id": "SUP-01",
  "kind": "supplier",
  "label": "Apex Components",
  "supplier_id": "SUP-01",
  "name": "Apex Components",
  "location": "Pune",
  "note": "Primary supplier, electronics"
}
```

### 3.2 Part Nodes
Bill of Materials (BOM) components with operational inventory metrics.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `id` | string | Yes | Unique node identifier | `"PART-01"` |
| `kind` | string | Yes | Must be `"part"` | `"part"` |
| `label` | string | Yes | Display title | `"Control Board"` |
| `part_id` | string | Yes | Component part number | `"PART-01"` |
| `name` | string | Yes | Component name | `"Control Board"` |
| `stock_on_hand` | integer / float | Yes | Current warehouse inventory ($\ge 0$) | `120` |
| `daily_consumption` | integer / float | Yes | Rate of daily usage ($\ge 0$) | `20` |
| `days_of_supply` | float | Yes | Buffer days ($\text{stock} / \text{consumption}$) | `6.0` |

```json
{
  "id": "PART-01",
  "kind": "part",
  "label": "Control Board",
  "part_id": "PART-01",
  "name": "Control Board",
  "stock_on_hand": 120,
  "daily_consumption": 20,
  "days_of_supply": 6.0
}
```

### 3.3 Finished Product Nodes
Manufactured assemblies ready for customer dispatch.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `id` | string | Yes | Unique node identifier | `"PROD-01"` |
| `kind` | string | Yes | Must be `"product"` | `"product"` |
| `label` | string | Yes | Display title | `"Autonomous Delivery Rover"` |
| `product_id` | string | Yes | Product catalog code | `"PROD-01"` |
| `name` | string | Yes | Product name | `"Autonomous Delivery Rover"` |
| `parts_needed` | list[string] | No | BOM list of part IDs | `["PART-01", "PART-02", "PART-05"]` |

```json
{
  "id": "PROD-01",
  "kind": "product",
  "label": "Autonomous Delivery Rover",
  "product_id": "PROD-01",
  "name": "Autonomous Delivery Rover",
  "parts_needed": ["PART-01", "PART-02", "PART-05"]
}
```

### 3.4 Customer Order Nodes
Committed customer orders with fulfillment deadlines.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `id` | string | Yes | Unique node identifier | `"ORD-01"` |
| `kind` | string | Yes | Must be `"order"` | `"order"` |
| `label` | string | Yes | Display title | `"Ord #1 - QuickLogistics"` |
| `order_id` | string | Yes | Order business code | `"ORD-01"` |
| `customer` | string | Yes | Client or company name | `"QuickLogistics"` |
| `product_id` | string | Yes | Target product required | `"PROD-01"` |
| `quantity` | integer | Yes | Order volume ($> 0$) | `5` |
| `deadline` | string | Yes | ISO 8601 target delivery date | `"2026-11-15"` |

```json
{
  "id": "ORD-01",
  "kind": "order",
  "label": "Ord #1 - QuickLogistics",
  "order_id": "ORD-01",
  "customer": "QuickLogistics",
  "product_id": "PROD-01",
  "quantity": 5,
  "deadline": "2026-11-15"
}
```

---

## 4. Edge Schema Specification

All edges require three core fields:
- `source` (`string`): Identifier of the origin node.
- `target` (`string`): Identifier of the destination node.
- `relation` (`string`): Relationship descriptor matching the agreed edge category.

### 4.1 Supplies Relationship (`edges.supplies`)
Connects a `supplier` node to a supplied `part` node.

| Attribute | Type | Permitted Value / Range | Description |
|---|---|---|---|
| `source` | string | Existing `supplier` ID | Originating vendor |
| `target` | string | Existing `part` ID | Component being supplied |
| `relation` | string | `"SUPPLIES"` | Upper-case relation descriptor |
| `lead_time_hours` | integer / float | $\ge 0$ | Transit lead time |
| `max_capacity_units_per_day` | integer / float | $\ge 0$ | Vendor throughput capacity |

```json
{
  "relation": "SUPPLIES",
  "source": "SUP-01",
  "target": "PART-01",
  "from_supplier": "SUP-01",
  "to_part": "PART-01",
  "lead_time_hours": 48,
  "max_capacity_units_per_day": 500
}
```

### 4.2 Used In Relationship (`edges.used_in`)
Connects a `part` node into a finished `product` assembly.

| Attribute | Type | Permitted Value / Range | Description |
|---|---|---|---|
| `source` | string | Existing `part` ID | Originating BOM part |
| `target` | string | Existing `product` ID | Assembly consuming the part |
| `relation` | string | `"USED_IN"` | Upper-case relation descriptor |
| `quantity_per_unit` | integer / float | $> 0$ | Units needed per finished product |
| `quantity_per_product` | integer / float | $> 0$ | Synonym for quantity_per_unit |

```json
{
  "relation": "USED_IN",
  "source": "PART-01",
  "target": "PROD-01",
  "from_part": "PART-01",
  "to_product": "PROD-01",
  "quantity_per_unit": 1,
  "quantity_per_product": 1
}
```

### 4.3 Fulfills Relationship (`edges.fulfills`)
Connects a finished `product` assembly to a customer purchase `order`.

| Attribute | Type | Permitted Value / Range | Description |
|---|---|---|---|
| `source` | string | Existing `product` ID | Finished assembly |
| `target` | string | Existing `order` ID | Customer purchase order |
| `relation` | string | `"FULFILLS"` | Upper-case relation descriptor |

```json
{
  "relation": "FULFILLS",
  "source": "PROD-01",
  "target": "ORD-01",
  "from_product": "PROD-01",
  "to_order": "ORD-01"
}
```

---

## 5. Validation Rules & Enforcement Architecture

### 5.1 Pre-Construction Duplicate Node ID Detection
> [!IMPORTANT]
> NetworkX's `nx.DiGraph.add_node(id, **attrs)` **silently overwrites** existing node attributes when called multiple times with the same identifier. Therefore, duplicate ID detection cannot be performed on a constructed `nx.DiGraph`. The validator inspects the raw JSON data upfront to guarantee uniqueness across all categories.

- **Check ID**: `NODE_DUPLICATES`
- **Error Code**: `ERR_DUPLICATE_NODE_ID`
- **Tested In**: [`tests/test_duplicate_ids.py::test_networkx_silent_collapse_proof`](../backend/tests/test_duplicate_ids.py)

### 5.2 Edge Reference & Direction Rules
- **Non-Existent Endpoints**: Every edge `source` and `target` must resolve to a valid node defined in `nodes`. Violations trigger `ERR_NONEXISTENT_SOURCE_NODE` or `ERR_NONEXISTENT_TARGET_NODE`.
- **Direction Invariants**:
  - `supplies` edges must flow strictly `supplier -> part`.
  - `used_in` edges must flow strictly `part -> product`.
  - `fulfills` edges must flow strictly `product -> order`.
  - Tier skipping (e.g. `supplier -> product` or `part -> order`) or reversed edges (e.g. `part -> supplier`) produce `ERR_INVALID_EDGE_DIRECTION`.

### 5.3 Supplier Reachability Ground Truth
Based on the canonical graph, downstream BFS reachability from suppliers is deterministic:

$$\text{Downstream}(\text{SUP-01}) = \{\text{PART-01}, \text{PART-02}, \text{PART-05}, \text{PROD-01}, \text{ORD-01}, \dots, \text{ORD-06}\} \quad (\mathbf{10} \text{ nodes})$$

$$\text{Downstream}(\text{SUP-02}) = \{\text{PART-03}, \text{PART-04}, \text{PART-05}, \text{PROD-01}, \text{PROD-02}, \text{ORD-01}, \dots, \text{ORD-10}\} \quad (\mathbf{15} \text{ nodes})$$

### 5.4 Cycle & DAG Policy
The validator implements three configurable acyclicity policies via [`AcyclicityPolicy`](../backend/graph_validation/schema.py#L13):
1. **`REQUIRE_DAG`** (Default): Graph must be strictly acyclic (`nx.is_directed_acyclic_graph(G) == True`). Any cycle raises `ERR_CYCLE_DETECTED`.
2. **`ALLOW_CYCLES`**: Cycles are permitted without error for scenarios modeling reverse logistics or recycling loops.
3. **`UNSPECIFIED`**: Emits a non-fatal warning (`WARN_ACYCLICITY_POLICY_UNDEFINED`) reminding operators that cycle enforcement is not explicitly configured.

---

## 6. Schema Gaps & Unresolved Design Decisions

1. **Circular Reverse Logistics / Recycling**:
   - If future sprints introduce return packaging or core exchanges (e.g., `ORD -> PART` recycling loops), the `REQUIRE_DAG` policy must be transitioned to `ALLOW_CYCLES` or scoped to forward-logistics subgraphs.
2. **Sub-Assembly Hierarchy**:
   - Currently, `used_in` only permits `part -> product`. Complex hierarchies where parts are assembled into sub-assemblies (`part -> subassembly -> product`) would require extending `direction_rules` in `ValidationPolicy`.
3. **Capacity Constraints Validation**:
   - The dataset provides `max_capacity_units_per_day` on `supplies` edges and `daily_consumption` on parts, but numerical consistency between capacity and consumption is currently not validated by `validate_raw_graph_data()`.

