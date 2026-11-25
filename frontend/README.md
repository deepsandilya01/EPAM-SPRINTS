# RE:Flow Frontend — Sprint 2 (Next.js + TypeScript + D3.js)

Independent Next.js App Router frontend for **RE:Flow — Temporal Disruption Simulation & Intervention Window Engine** (Team PHOTON Sprint 2, Feature 10).

## Technology Stack

- **Framework**: Next.js 15 (App Router) + React 19 + TypeScript (`strict: true`)
- **Styling**: Tailwind CSS (strict black-and-white enterprise palette with restrained status accents)
- **State Management**: Redux Toolkit + React Redux
- **Visualization**: D3.js v7 (TypeScript-based responsive SVG charts)
- **API Client**: Centralized Axios instance + feature-scoped API services
- **Forms & Validation**: React Hook Form + Zod
- **Icons**: Lucide React

## Feature-Based Folder Structure

```text
frontend/src/
├── AppRoutes.tsx                 # Central route-to-feature mapping (/, /dashboard, /simulation, /overview, /settings)
├── store.ts                      # Redux store & typed hooks
├── app/                          # Clean Next.js App Router shell (layout, globals, providers, page.tsx)
├── features/
│   ├── dashboard/                # Dashboard & Supply Chain Overview feature
│   │   ├── components/           # SupplyChainGraph (read-only 4-tier DAG)
│   │   ├── hooks/                # useBackendSync
│   │   ├── pages/                # DashboardPage, OverviewPage
│   │   ├── services/             # dashboardApi (/api/health, /api/graph, /api/downstream)
│   │   └── slices/               # dashboardSlice
│   ├── simulation/               # Sprint 2 Disruption Simulation & Intervention feature
│   │   ├── components/           # DisruptionForm, InventoryDepletionChart, TimelineScrubber, InterventionGauge, AffectedOrdersTable
│   │   ├── pages/                # SimulationPage
│   │   ├── services/             # simulationApi (/api/v1/simulation/disrupt)
│   │   ├── slices/               # simulationSlice, simulationSelectors
│   │   └── simulationSchema.ts   # Zod validation schema
│   ├── settings/
│   │   └── pages/                # SettingsPage
│   └── shared/                   # Shared layout shell, UI primitives, Axios client, types, utils
│       ├── components/           # AppShell, Sidebar, TopNav, Card, Badge, EmptyState, ErrorBoundary
│       ├── services/             # axiosInstance
│       ├── types/                # graph.ts, simulation.ts
│       └── utils/                # constants.ts, format.ts
└── store.ts                      # Redux store & typed hooks
```

## Environment Variables

Copy `.env.local.example` to `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5001
```

## Running Both Applications Independently

### 1. Start the Python FastAPI Backend

From the repository root:

```bash
python3 backend/app/main.py
```

### 2. Start the Next.js Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Render Cloud Deployment

The repository root `render.yaml` configures two independent Render Web Services:
1. **`reflow-backend`** (Python FastAPI): runs `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` with `healthCheckPath: /health` and receives `FRONTEND_HOST` for explicit CORS.
2. **`reflow-frontend`** (Next.js): builds inside `frontend/` (`npm ci && npm run build`), binds to `0.0.0.0:$PORT` via `npm run start`, and proxies `/api/*` through `src/app/api/[...path]/route.ts` to `BACKEND_HOST` (or direct `NEXT_PUBLIC_API_BASE_URL` if configured).

