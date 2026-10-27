# IntelliTwin — Supply Chain Graph & Scenario Generator
### Team PHOTON • Sprint 1 Delivery

IntelliTwin is a production-grade enterprise digital twin and supply chain graph visualization application. It provides interactive multi-tier dependency tracing, BFS graph traversal, impact propagation analysis, and scenario simulation for complex manufacturing networks.

![IntelliTwin Graph Explorer Architecture](https://img.shields.io/badge/Architecture-Clean%20Hexagonal-blue)
![React](https://img.shields.io/badge/React-19.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-6.0-blue)
![Vite](https://img.shields.io/badge/Vite-8.3-purple)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-teal)
![XYFlow](https://img.shields.io/badge/@xyflow/react-12.12-orange)
![Tests](https://img.shields.io/badge/Tests-27%20Passing-brightgreen)

---

## 📸 Overview & Key Capabilities

- **Dynamic Supply Chain Graph Generator**:
  - Configure quantity of **Suppliers (1–20)**, **BOM Parts (1–50)**, **Finished Products (1–20)**, and **Customer Orders (1–100)** via sidebar inputs.
  - Generates realistic, unique entity IDs (`SUP-XX`, `PART-XX`, `PROD-XX`, `ORD-XX`) and valid directed relationships (`SUPPLIES`, `USED_IN`, `FULFILLS`).
  - Automatic non-overlapping vertical column layout calculation.
  - Validates positive integers and prevents empty/negative/decimal inputs.
- **Interactive Direction-Aware Hover Path Highlighting**:
  - Hovering on any node triggers real-time graph traversal discovering its entire upstream and downstream supply-chain connections.
  - Animates connected edges with flowing dashes (`@keyframes edge-flow`) in relationship category colors.
  - Dims unrelated nodes and edges to 25% opacity.
  - Displays contextual floating tooltips with direct and total upstream/downstream connection counts without overwriting selected node details.
  - Respects user accessibility preferences (`prefers-reduced-motion`).
- **Left Sidebar (275px fixed)**:
  - Input parameters: Supplier selector (`SUP-01`...`SUP-N`), Trace Type (Downstream / Upstream), Highlight Depth (`All Levels`, `Direct Parts`, `Parts + Products`), Node Filter chips, Unaffected Nodes toggle switch.
  - Primary **Generate Graph** action triggering reactive updates across the canvas, metrics, summary, and order reachability.
  - Quick Actions: **Reset View**, **Fit to Screen**, **Download Graph (PNG)**, **Export Data (CSV)**.
- **Top Header**:
  - Breadcrumb (`Supply Chain > Graph Explorer > Downstream Trace`).
  - Date selector (`Feb 5, 2025`).
  - **Run Simulation** trigger with local propagation feedback.
  - User avatar.
- **Summary Cards**:
  - 4 Pastel KPI cards: **Suppliers (2)**, **BOM Parts (5)**, **Finished Products (2)**, **Customer Orders (10)**.
- **Main Graph Visualization (`@xyflow/react`)**:
  - 4-column horizontal dependency layout:
    - **Column 1: Suppliers** (`SUP-01`, `SUP-02`)
    - **Column 2: BOM Parts** (`PART-01` to `PART-05`)
    - **Column 3: Finished Products** (`PROD-01`, `PROD-02`)
    - **Column 4: Customer Orders** (`ORD-01` to `ORD-10`)
  - 19 nodes, 21 directed edges (6 `SUPPLIES`, 5 `USED_IN`, 10 `FULFILLS`).
  - Category-specific pastel and active badge styling with glow rings and relationship-colored cubic bezier curves.
  - Floating graph controls toolbar: search filter, zoom in/out, percentage display, fit view, and fullscreen toggle.
- **Right Sidebar (300px)**:
  - **Node Details**: Displays dynamic, type-discriminated attributes (Suppliers, BOM parts, Finished products, Customer orders).
  - **Traversal Summary**: Displays source supplier, total entities reached, BOM parts reached, products reached, and customer orders reached.
  - **Legend**: Color-coded category markers and arrow relationship guide.
- **Bottom Traversal & Benchmark Panels**:
  - **Traversal Performance**: Total Traversal Time (measured in ms via `performance.now()`), Visited Nodes, Traversed Edges, Algorithm (`BFS`, $O(V + E)$).
  - **Step-wise Traversal Timing Table**: Step, From Node, To Node, Relation, Traversal Time (ms), Cumulative Time (ms) for the path to `ORD-01`.
  - **Reachable Customer Orders**: Color-coded active blue pills (`ORD-01`–`ORD-06` for `SUP-01`; `ORD-01`–`ORD-10` for `SUP-02`) and inactive grey pills.

---

## 🛠️ Mandatory Technology Stack

| Layer | Library | Purpose |
|---|---|---|
| **Core Framework** | React 19 + TypeScript | Type-safe UI architecture |
| **Build Tooling** | Vite | Ultra-fast HMR and bundling |
| **Styling** | Tailwind CSS | Utility-first design system matching screenshot palette |
| **Graph Engine** | `@xyflow/react` (React Flow) | Horizontal DAG layout, custom nodes, bezier edges |
| **Client UI State** | Redux Toolkit (`@reduxjs/toolkit`) | Filter states, depth, selections, and viewport triggers |
| **Server State** | TanStack Query (`@tanstack/react-query`) | Asynchronous data fetching cache & future API hydration |
| **HTTP Client** | Axios | Configured client ready for FastAPI integration |
| **Routing** | React Router v7 | Seamless page routing (`/`, `/graph-explorer`, `/validation`, `/performance`) |
| **Charts** | Recharts | Traversal latency & benchmark distribution charts |
| **Icons** | Lucide React | Consistent enterprise icons |
| **Testing** | Vitest + React Testing Library | 19 automated tests verifying scenario oracles and UI |

---

## 🗂️ Application Structure

```text
frontend/
├── src/
│   ├── api/                     # Decoupled repository layer ready for FastAPI
│   │   ├── client.ts            # Axios instance with VITE_DATA_MODE & interceptors
│   │   ├── graph.api.ts         # Graph data query hooks
│   │   ├── traversal.api.ts     # Traversal execution query hooks
│   │   ├── validation.api.ts    # Graph integrity audit hooks
│   │   └── benchmark.api.ts    # Algorithmic benchmark query hooks
│   ├── components/
│   │   ├── dashboard/           # Summary cards, performance metrics, tables, pills
│   │   ├── graph/               # React Flow custom nodes, custom edges, canvas toolbar
│   │   └── layout/              # Sidebar, Header, Right details panel
│   ├── mocks/                   # Canonical scenario datasets and algorithms
│   │   ├── scenario.ts          # 19 nodes, 21 directed edges, entity attributes
│   │   ├── graph.ts             # Deterministic coordinates and graph topology
│   │   ├── validation.ts        # Invariant checks: DAG cycles, endpoints, IDs
│   │   └── benchmark.ts         # Empirical latency profiler (BFS vs DFS)
│   ├── pages/                   # Application routes
│   │   ├── GraphExplorerPage.tsx # Primary screenshot recreation
│   │   ├── OverviewPage.tsx     # System overview and entry portal
│   │   ├── ValidationPage.tsx   # Integrity audit findings
│   │   └── PerformancePage.tsx  # Benchmark latency charts & complexity
│   ├── services/
│   │   ├── traversal.service.ts # Pure BFS traversal with depth & filters
│   │   └── export.service.ts    # CSV data export & PNG canvas download
│   ├── store/                   # Redux Toolkit store and slices
│   │   ├── slices/graphUiSlice.ts   # Active supplier, filters, depth, direction
│   │   ├── slices/graphViewSlice.ts # Zoom, search, fullscreen, reset triggers
│   │   └── index.ts
│   ├── test/                    # Automated Vitest test suite
│   │   ├── scenario.test.ts     # Edge/node count and direction verification
│   │   ├── traversal.test.ts    # Oracle reachability (SUP-01 & SUP-02)
│   │   ├── validation.test.ts   # Integrity checks and cycle detection
│   │   ├── export.test.ts       # CSV and PNG export handling
│   │   └── components.test.tsx  # React component and Redux store tests
│   └── types/                   # Unified domain & graph TypeScript definitions
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18.0.0 or higher (v24+ tested)
- **npm**: v9.0.0 or higher

### Installation

Clone the repository and install dependencies:

```bash
cd frontend
npm install
```

Or from the workspace root:

```bash
npm install --prefix frontend
```

### Running Locally (Development Mode)

Start the local Vite development server:

```bash
npm run dev
```

Open [http://localhost:5173/graph-explorer](http://localhost:5173/graph-explorer) (or the port indicated in the terminal) in your browser.

---

## 🧪 Running Automated Tests

Run the Vitest test suite:

```bash
npm test
```

To run in watch mode:
```bash
npm run test:watch
```

### Verified Scenario Test Matrix

All 19 automated tests execute cleanly against the canonical scenario:
- ✅ **19 Nodes Total**: 2 Suppliers, 5 BOM Parts, 2 Finished Products, 10 Customer Orders.
- ✅ **21 Directed Edges Total**: 6 `SUPPLIES`, 5 `USED_IN`, 10 `FULFILLS`.
- ✅ **SUP-01 Reachability Oracle**:
  - 3 BOM Parts (`PART-01`, `PART-02`, `PART-05`).
  - 1 Finished Product (`PROD-01`).
  - 6 Customer Orders (`ORD-01` through `ORD-06`).
  - 10 Total Reached Entities.
- ✅ **SUP-02 Reachability Oracle**:
  - 3 BOM Parts (`PART-03`, `PART-04`, `PART-05`).
  - 2 Finished Products (`PROD-01`, `PROD-02`).
  - 10 Customer Orders (`ORD-01` through `ORD-10`).
  - 15 Total Reached Target Entities.
- ✅ **Deduplication**: 0 duplicate entities in BFS traversal results.
- ✅ **Highlight Depth**: Accurately bounds exploration to Level 1 (Direct Parts) and Level 2 (Parts + Products).
- ✅ **Upstream Traversal**: Traverses backwards from order to products, parts, and suppliers.
- ✅ **Topology Invariants**: Validates DAG acyclic property, flags missing endpoints, and verifies identifier uniqueness.

---

## 🏗️ Production Build & Verification

To create an optimized production build:

```bash
npm run build
```

This compiles TypeScript with strict type checking and bundles assets with Vite into `frontend/dist/`.

To preview the production bundle locally:

```bash
npm run preview
```

---

## 🔌 Future FastAPI Backend Integration

The frontend is architected for drop-in FastAPI integration:

1. Data fetching is isolated in `src/api/*` behind TanStack Query hooks.
2. An environment variable controls the operational mode in `.env`:
   ```bash
   VITE_DATA_MODE=mock      # Options: 'mock' | 'live'
   VITE_API_BASE_URL=http://localhost:8000
   ```
3. In `live` mode, all calls route through the configured `Axios` client (`src/api/client.ts`). Real network and status errors are propagated directly without synthetic fallback masking.