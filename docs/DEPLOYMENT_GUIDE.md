# Team Photon — Production Deployment Guide

> **Project:** Proactive Supply-Chain Decision, Ripple & Recovery Intelligence System  
> **Team:** LNCT Photon  
> **Component:** Sprint 1 — Directed Graph Visualization, Validation & Tracing Engine  
> **Technology Stack:** Python 3.12+, Flask 3.1.1, NetworkX 3.4.2, D3.js v7, pytest 9.2.0

---

## 1. Deployment Overview

### 1.1 Architecture & Deployment Model
The Team Photon Sprint 1 application is a **full-stack Python web application** combining:
- A **Flask 3.1.1** backend that exposes REST API endpoints for graph data, downstream traversal, cascading deletion, undo history, structural validation, and high-resolution latency benchmarking.
- An in-memory **NetworkX 3.4.2** directed acyclic graph (`nx.DiGraph`) initialized on startup from `photon_sprint1_graph_data.json`.
- A dynamic **D3.js (v7)** single-page frontend served by Flask from the `static/` directory.

```
+-------------------------------------------------------------------------+
|                          Web Browser Client                             |
|        D3.js v7 Interactive Visualization (static/index.html)           |
+-----------------------------------+-------------------------------------+
                                    | HTTPS / REST Calls
                                    v
+-------------------------------------------------------------------------+
|                  Hosting Platform (e.g. Render / PaaS)                  |
|  +-------------------------------------------------------------------+  |
|  |                 WSGI Server: Gunicorn (1 Worker)                  |  |
|  |             Binds to 0.0.0.0:$PORT (Platform Injected)            |  |
|  +-----------------------------------+-------------------------------+  |
|                                      |                                   |
|                                      v                                   |
|  +-------------------------------------------------------------------+  |
|  |                     Flask Application (app.py)                    |  |
|  |  - REST Router (/api/*)           - In-Memory GRAPH (19V / 21E)   |  |
|  |  - Static File Server (/)         - In-Memory UNDO_STACK          |  |
|  |  - graph_validation Engine        - Startup Integrity Auditor     |  |
|  +-----------------------------------+-------------------------------+  |
|                                      | Reads at Startup                  |
|                                      v                                   |
|  +-------------------------------------------------------------------+  |
|  |         Canonical Dataset: photon_sprint1_graph_data.json         |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

> [!IMPORTANT]
> **Static Hosting Incompatibility**: This project **cannot** be deployed to static web hosts (such as GitHub Pages, Vercel Static, or AWS S3). The D3 frontend requires active Python backend routes (`/api/graph`, `/api/downstream/<id>`, `/api/validation`, etc.) powered by NetworkX. A Python-compatible hosting environment is strictly required.

---

### 1.2 Recommended Hosting Platform: Render
For Team Photon Sprint 1, **[Render](https://render.com)** is the **primary recommended platform** for the following reasons:
1. **Native Python & WSGI Support**: First-class support for Python 3.10–3.12 with automatic dependency resolution via `requirements.txt`.
2. **Zero-Configuration HTTPS & Port Binding**: Automatically provisions free SSL certificates and injects the dynamic `$PORT` environment variable.
3. **Automated Git Integration**: Continuous deployment triggers automatically on every push to your GitHub repository.
4. **Accessible Free Tier**: Provides free web service hosting suitable for academic demonstrations, sprint reviews, and technical evaluation.

#### Alternative Hosting Platforms
- **Railway ([railway.app](https://railway.app))**: Excellent alternative with auto-detected Python environments and instant deployments.
- **Fly.io ([fly.io](https://fly.io))**: Docker-based deployment close to the user; requires CLI-based configuration.
- **Self-Hosted Linux VPS (Ubuntu + Nginx + Gunicorn + systemd)**: Recommended for enterprise production where persistent state, custom domain routing, and hardware isolation are required.

---

### 1.3 Local Development vs. Production Differences

| Characteristic | Local Development | Cloud Production (e.g. Render) |
|---|---|---|
| **Server** | Werkzeug Development Server (`app.run()`) | Production WSGI Server (`gunicorn`) |
| **Host & Port** | `127.0.0.1:5000` | `0.0.0.0:$PORT` (dynamically assigned) |
| **Debug Mode** | `debug=True` (auto-reloader, debug stack) | `debug=False` / `FLASK_DEBUG=0` (secure) |
| **Process Model** | Single process, interactive console | Multi-threaded single-worker process |
| **File Persistence** | Local hard drive | Ephemeral container filesystem |
| **Process Lifetime** | Runs until terminated manually in terminal | Managed process; sleeps after inactivity on free tiers |

---

## 2. Pre-Deployment Checks

Before deploying, verify that all prerequisites, configurations, and files are in order.

### 2.1 Repository Structure Checklist
Confirm the following essential files and directories exist in your project root:

```
EPAM-SPRINTS/
├── backend/                              # Flask application & validation package
│   ├── app.py                            # Flask application entry point
│   ├── requirements.txt                  # Python dependencies
│   ├── static/
│   │   └── index.html                    # D3.js visualization frontend
│   ├── data/                             # Canonical graph dataset
│   │   └── photon_sprint1_graph_data.json
│   ├── graph_validation/                 # Core validation & benchmarking package
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── validator.py
│   │   ├── tracing.py
│   │   └── reporting.py
│   ├── benchmarks/                       # Statistical benchmark engine
│   │   ├── __init__.py
│   │   ├── benchmark_tracing.py
│   │   └── README.md
│   └── tests/                            # Automated test suite (73 tests)
├── docs/                                 # Documentation guides
├── reports/                              # Generated report artifacts
├── README.md                             # Repository overview
├── pytest.ini                            # Pytest root configuration
├── pyproject.toml                        # Tooling & Ruff configuration
└── requirements.txt                      # Root requirements manifest
```

### 2.2 Dependency & Python Compatibility
- **Verified Python Version**: CPython **3.12.14** (Python 3.10, 3.11, and 3.12 are fully compatible).
- **Core Dependencies**:
  - `flask==3.1.1`
  - `networkx==3.4.2`
- **Required Production Addition**: To run under a production WSGI server on Linux cloud platforms, add `gunicorn` to `requirements.txt`:
  ```text
  flask==3.1.1
  networkx==3.4.2
  gunicorn>=23.0.0
  ```

### 2.3 Path Resolution Verification
In `backend/app.py`, file paths are derived using absolute resolution relative to `__file__`:
```python
BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "photon_sprint1_graph_data.json"
app = Flask(__name__, static_folder="static", static_url_path="/static")
```
This guarantees that static assets (`static/index.html`) and the JSON dataset are located accurately, regardless of what working directory the hosting platform uses to launch the process.

### 2.4 Git & Repository Hygiene (`.gitignore`)
Ensure your repository contains a `.gitignore` file to prevent committing local virtual environments, Python bytecode, test caches, and OS artifacts:

```gitignore
# Virtual environments
.venv/
venv/
ENV/
.python/

# Python bytecode & caches
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/

# Logs & temp files
*.log
scratch/
.system_generated/

# OS-specific
.DS_Store
Thumbs.db
```

### 2.5 Pre-Deployment Local Test Execution
Run the complete automated test suite locally to ensure 100% pass status prior to pushing to Git:

```bash
# From repository root:
pytest -v

# Or within backend:
cd backend
pytest -v
```
*Expected Output:* **`73 passed`**

---

## 3. Step-by-Step Deployment to Render (Recommended Platform)

Follow these numbered steps to deploy the application from your local machine to the cloud.

### Step 1: Add Production WSGI Dependency
Open `requirements.txt` and ensure `gunicorn` is listed:

```text
flask==3.1.1
networkx==3.4.2
gunicorn>=23.0.0
```

Install it in your local virtual environment to verify compatibility:
```powershell
pip install gunicorn
```
*(Note: Gunicorn runs natively on Linux/macOS. On Windows, Gunicorn is for export to the Linux container; local Windows testing can use `python app.py` or `waitress`.)*

---

### Step 2: Initialize Git Repository
If Git is not already initialized in your project folder, initialize it and commit the clean source tree:

```powershell
# Initialize git
git init

# Verify .gitignore is in place
git status

# Stage all project files
git add .

# Create initial commit
git commit -m "feat: complete Team Photon Sprint 1 supply-chain graph application"
```

---

### Step 3: Create GitHub Repository & Push
1. Log in to [GitHub](https://github.com).
2. Click **New Repository**.
3. Name the repository (e.g., `team-photon-supply-chain-graph`).
4. Keep it Public or Private, and do not initialize with README (it already exists).
5. Link your local project and push to the `main` branch:

```powershell
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/team-photon-supply-chain-graph.git
git branch -M main
git push -u origin main
```

---

### Step 4: Create a New Web Service on Render
1. Navigate to [dashboard.render.com](https://dashboard.render.com) and sign in.
2. Click **New +** in the top navigation bar and select **Web Service**.
3. Select **Build and deploy from a Git repository**.
4. Connect your GitHub account and select your `team-photon-supply-chain-graph` repository.
5. Click **Connect**.

---

### Step 5: Configure Build & Runtime Settings
Configure the service settings on the Render creation screen:

| Setting | Value | Explanation |
|---|---|---|
| **Name** | `photon-supply-chain` (or custom name) | Subdomain identifier for your application URL. |
| **Region** | Select closest region (e.g., `Singapore`, `Frankfurt`, `Oregon`) | Minimizes network round-trip latency. |
| **Branch** | `main` | Branch to monitor for automatic deployments. |
| **Root Directory** | *(Leave blank)* | Uses the root of the repository. |
| **Runtime** | `Python 3` | Informs Render to provision a Python runtime environment. |
| **Build Command** | `pip install -r requirements.txt` | Installs Flask, NetworkX, and Gunicorn. |
| **Start Command** | `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT` | Launches production WSGI server with single-worker process model. |
| **Instance Type** | `Free` | Sufficient for Sprint 1 demonstrations and testing. |

> [!CAUTION]
> **Why `--workers 1` is Mandatory**: Because Team Photon Sprint 1 holds the dynamic graph state (`GRAPH`) and undo history (`UNDO_STACK`) in server memory, running multiple worker processes (e.g., `--workers 4`) would cause state fragmentation (Worker A deletes a node, but a subsequent request hits Worker B which still has the node). Using `--workers 1 --threads 4` guarantees a single synchronized in-memory state while handling concurrent I/O.

---

### Step 6: Configure Environment Variables
Under the **Environment Variables** section on Render, add:

| Key | Value | Purpose |
|---|---|---|
| `PYTHON_VERSION` | `3.12.14` | Specifies the exact tested CPython runtime. |
| `FLASK_DEBUG` | `0` | Ensures Flask debug reloader and stack trace exposer are disabled. |

---

### Step 7: Trigger Deployment & Inspect Build Logs
1. Click **Create Web Service**.
2. Render will allocate a build container, clone your Git repository, and execute the build pipeline:
   - Python 3.12 environment provisioned.
   - `pip install -r requirements.txt` executed.
   - Startup validation runs via `validate_raw_graph_data(RAW)`.
3. In the **Logs** tab, verify successful startup output:
   ```text
   ==> Uploading build...
   ==> Build successful 🎉
   ==> Deploying...
   ==> Starting service with 'gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:10000'
   [2026-10-29 00:00:00 +0000] [1] [INFO] Starting gunicorn 23.0.0
   [2026-10-29 00:00:00 +0000] [1] [INFO] Listening at: http://0.0.0.0:10000 (1)
   [2026-10-29 00:00:00 +0000] [1] [INFO] Using worker: gthread
   ==> Your service is live 🎉 at https://photon-supply-chain.onrender.com
   ```

---

### Step 8: Verify Live Deployment
Click on your application's public URL (e.g., `https://photon-supply-chain.onrender.com`):
1. **Frontend Loading**: Verify that the dark-themed UI loads, showing header "Photon Sprint 1 — Supply-Chain Graph".
2. **Graph Rendering**: Confirm the 4-column tier layout renders **19 nodes** (2 suppliers, 5 parts, 2 products, 10 orders) and **21 edges**.
3. **Interactive Downstream Tracing**: Click `SUP-01` (Apex Components) — verify downstream highlighting on 10 nodes and impact preview rendering in the bottom dock.
4. **Cascading Deletion**: Delete `PART-05` — verify node and downstream cascade removal, followed by 5-second undo toast.
5. **Undo**: Click `Undo` within 5 seconds — verify complete restoration of `PART-05`.
6. **Reset**: Click `Reset` — verify graph resets cleanly to 19 nodes.

---

### Step 9: Updating & Redeploying
Whenever you make updates to the codebase:
1. Run local tests: `pytest tests/`
2. Commit and push to GitHub:
   ```powershell
   git add .
   git commit -m "fix: refine downstream tracing edge styling"
   git push origin main
   ```
3. Render detects the push and triggers an automatic zero-downtime redeployment.

---

## 4. Production Configuration & Best Practices

### 4.1 Production WSGI Server (Gunicorn)
Flask's built-in server (`app.run()`) is explicitly designed for local development only. In production, requests must be served through a robust WSGI HTTP server:
- **Command**: `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT`
- **`app:app`**: The first `app` refers to the Python module (`app.py`), and the second `app` refers to the Flask instance (`app = Flask(...)`).
- **`--workers 1`**: Keeps in-memory graph state unified.
- **`--threads 4`**: Enables concurrent processing of incoming HTTP requests without blocking the event loop.
- **`--bind 0.0.0.0:$PORT`**: Listens on all network interfaces using the port assigned by the hosting provider.

### 4.2 Disabling Debug Mode
Never run production applications with `debug=True`. In [`backend/app.py`](../backend/app.py):
```python

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    app.run(host="0.0.0.0", port=port, debug=debug)
```
When started via Gunicorn, the `if __name__ == "__main__":` block is bypassed entirely, which inherently prevents debug mode from activating.

### 4.3 Static File Serving in Production
- Flask serves files from the `static/` directory using `send_from_directory()`.
- For low-to-medium traffic applications, Flask is fully capable of serving `static/index.html` and assets.
- For high-traffic enterprise environments, static assets should be offloaded to a CDN (e.g. Cloudflare) or served directly through Nginx reverse proxy.

---

## 5. Data & Runtime Architecture Limitations

### 5.1 In-Memory Ephemeral State
Understanding how the Sprint 1 system manages state is critical for operational expectations:

1. **Source of Truth is Read-Only**: The JSON file `photon_sprint1_graph_data.json` is read once on startup into Python memory. **The server never modifies the source JSON on disk**.
2. **In-Memory Mutations**: Deleting nodes (`DELETE /api/node/<id>`) mutates the runtime `GRAPH` object in memory. Undo snapshots are stored in the memory-resident `UNDO_STACK`.
3. **Reset Behavior**: Invoking `POST /api/reset` discards the current `GRAPH` and rebuilds it in memory from the pristine `RAW` JSON.
4. **Container Restarts & Sleep**:
   - On Render Free tier, services spin down after 15 minutes of inactivity.
   - When a new request arrives, the container boots afresh, reloading `photon_sprint1_graph_data.json`.
   - **Any deletions performed prior to container sleep or redeployment will be reset to the canonical 19-node graph**.

### 5.2 Transition Path to Persistent Shared State (Sprint 2+)
If future sprints require persistent mutations across container restarts and horizontal multi-worker scaling:
1. **Database Backend**: Migrate graph persistence to a database (e.g., PostgreSQL or SQLite for relational storage; Neo4j or Amazon Neptune for native graph storage).
2. **Distributed Cache / Undo**: Store undo snapshots in Redis with session identifiers (`session_id`) rather than a single global Python list.
3. **Optimistic Locking**: Implement concurrency tokens (ETags) to prevent conflicting edits between multiple simultaneous users.

---

## 6. Deployment Verification & Smoke Testing Checklist

After deploying to production, execute the following verification steps using `curl` or your browser:

### 6.1 Automated HTTP Smoke Tests
Replace `https://<YOUR_APP_URL>` with your actual deployment URL:

```bash
# 1. Verify Root HTML Delivery
curl -I https://<YOUR_APP_URL>/
# Expected: HTTP/2 200 OK, content-type: text/html

# 2. Verify Canonical Graph Payload
curl -s https://<YOUR_APP_URL>/api/graph | grep -o '"id"' | wc -l
# Expected: 19

# 3. Verify Downstream Reachability (SUP-01 = 10 descendants)
curl -s https://<YOUR_APP_URL>/api/downstream/SUP-01
# Expected: JSON containing "root":"SUP-01" and 10 downstream IDs

# 4. Verify Structure Validation Report
curl -s https://<YOUR_APP_URL>/api/validation
# Expected: JSON containing "valid":true, "mode":"baseline", and 8 PASS checks

# 5. Verify Traversal Latency Benchmark (< 10 ms SLA)
curl -s https://<YOUR_APP_URL>/api/benchmark/tracing?node_id=SUP-01
# Expected: JSON containing "status":"PASS", "under_threshold":true, elapsed_ms < 1.0
```

### 6.2 Interactive UI Verification Checklist

| # | Inspection Item | Verification Action | Expected Behavior | Status |
|---|---|---|---|:---:|
| 1 | **Page Load** | Navigate to `https://<YOUR_APP_URL>/` | Loads dark theme canvas with header and dock within 2 seconds. | [ ] |
| 2 | **Entity Columns** | Inspect SVG visual canvas | 4 distinct tier columns: Suppliers (pink), Parts (orange), Products (teal), Orders (blue). | [ ] |
| 3 | **Hover Tooltip** | Hover cursor over `PART-01` | Displays floating card with Stock on Hand (120), Daily Consumption (20), Days of Supply (6.0). | [ ] |
| 4 | **Downstream Tracing** | Click node `SUP-02` | Downstream nodes illuminate; non-connected entities dim; bottom dock shows 15 affected nodes. | [ ] |
| 5 | **Impact Analysis** | Click node `PROD-01` | Bottom dock shows 6 customer orders (`ORD-01` to `ORD-06`) and $\mathcal{O}(V + E)$ complexity. | [ ] |
| 6 | **Deletion Flow** | Click "Delete Node" on `PART-02` | Confirmation modal appears; on confirm, node and downstream cascade are removed. | [ ] |
| 7 | **Undo Mechanism** | Click "Undo" button | Restores `PART-02` and connected dependencies; 5-second timing modal displays restoration metrics. | [ ] |
| 8 | **Reset Button** | Delete multiple nodes, click "Reset" | Graph instantly re-initializes to 19 nodes and 21 edges; undo button disables. | [ ] |

---

## 7. Troubleshooting Guide

| Symptom | Probable Cause | Actionable Solution |
|---|---|---|
| **Build Fails: `ModuleNotFoundError: No module named 'gunicorn'`** | `gunicorn` is missing from `requirements.txt`. | Add `gunicorn>=23.0.0` to `requirements.txt`, commit, and push. |
| **Startup Fails: `Port scan timeout` / `Service failed to bind to port`** | Gunicorn bound to hardcoded port instead of `$PORT`. | Ensure Start Command uses `--bind 0.0.0.0:$PORT` (literal `$PORT`, not `5000`). |
| **Python Version Error during build** | Host defaulted to Python 3.8 or 3.9 which lacks modern type syntax. | Add environment variable `PYTHON_VERSION = 3.12.14` in Render Dashboard. |
| **Blank White Screen / 404 on Root (`/`)** | Static directory structure misconfigured or `index.html` misplaced. | Verify file is at `static/index.html`. Check `app.py` has `static_folder="static"`. |
| **State Discrepancies (Deletions disappear or re-appear)** | Multiple Gunicorn workers running (`--workers 4`). | Change Start Command to `--workers 1 --threads 4` to keep state unified. |
| **Initial Request Takes 30–50 Seconds to Respond** | Normal cold start on Render free tier after 15 min idle. | Wait 30 seconds for container to boot. For zero cold starts, upgrade to Render Starter tier ($7/mo). |
| **`GET /api/validation` returns HTTP 422 after deletion** | User requested validation with `strict=true` while nodes are deleted. | Expected behavior: deleted graph has $< 19$ nodes. Request `mode=integrity` to validate non-baseline states. |
| **Terminal Warning: `[VALIDATION WARNING] Baseline graph validation failed on startup`** | JSON file was corrupted or modified with invalid references. | Restore canonical `photon_sprint1_graph_data.json` from git repository. |

---

## 8. Security, Maintenance & Operational Hygiene

### 8.1 Security Safeguards
1. **Never Commit Secrets**: Do not commit API keys, private tokens, or passwords to Git. Use environment variables for sensitive settings.
2. **Disable Debug Mode**: Ensure `FLASK_DEBUG=0` in production. Debug mode allows arbitrary code execution via the browser debugger console.
3. **CORS & Domain Restrictions**: If exposing the API to external domains in future sprints, install `flask-cors` and restrict origins to trusted domains.
4. **Input Sanitization**: Node IDs passed in URL parameters (`/api/downstream/<node_id>`) are sanitized by Flask's URL routing and validated against `GRAPH` membership before traversal.

### 8.2 Maintenance & Monitoring
- **Live Logs**: Inspect application logs in real time via the Render Dashboard **Logs** tab.
- **Health Checks**: The `GET /api/validation` endpoint can serve as a synthetic health check probe for uptime monitoring tools (e.g., UptimeRobot, BetterUptime).

### 8.3 Rollback Procedures
If a newly deployed commit introduces defects:
1. **Render Instant Rollback**: In the Render Dashboard, go to **Deploys** $\to$ select the previous successful deploy $\to$ click **Rollback**.
2. **Git Revert**: Revert the commit locally and push:
   ```powershell
   git revert HEAD
   git push origin main
   ```
This immediately triggers a rebuild of the known-good revision.

