# Environment Setup & Execution Guide

> **Document:** `docs/SETUP.md`  
> **Project:** Team Photon — Supply-Chain Decision, Ripple & Recovery Intelligence System  
> **Evaluation Phase:** EPAM Final Submission (Sprint 1)

This guide provides reproducible, step-by-step instructions to set up, configure, and execute the backend application and test suite from a fresh git clone across macOS, Linux, and Windows.

---

## 1. System Prerequisites

The project is tested and verified across Python versions **3.9 through 3.13**.

| Component | Minimum Version | Verified Production Version | Purpose |
|---|---|---|---|
| **Python** | 3.9+ | **3.9.6 / 3.12.14 / 3.13.7** | Core runtime |
| **pip** | 22.0+ | **24.0+** | Package management |
| **Operating System** | macOS 12+, Ubuntu 20.04+, Windows 10/11 | **macOS Sonoma, Windows 11 AMD64** | Host environment |
| **Git** | 2.30+ | **2.40+** | Source control |

---

## 2. macOS & Linux Setup (Bash / Zsh)

### Step 1: Clone and Navigate
```bash
git clone <repository-url> EPAM-SPRINTS
cd EPAM-SPRINTS
```

### Step 2: Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installed Packages
```bash
python3 -c "import flask, networkx, pytest; print(f'Environment Verified: Flask {flask.__version__}, NetworkX {networkx.__version__}, Pytest {pytest.__version__}')"
```

---

## 3. Windows Setup (PowerShell / Command Prompt)

### Step 1: Open Terminal in Repository Root
```powershell
cd C:\path\to\EPAM-SPRINTS
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate in PowerShell:
.\.venv\Scripts\Activate.ps1

# Or activate in classic Command Prompt (cmd.exe):
.\.venv\Scripts\activate.bat
```

> **PowerShell ExecutionPolicy Note**: If you encounter `File .venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled`, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

### Step 3: Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Environment
```powershell
python -c "import flask, networkx, pytest; print('Environment Verified OK')"
```

---

## 4. Running the Application

### Option A: Running from Repository Root (Recommended)
```bash
python -m backend.app
```

### Option B: Running from the `backend/` Directory
```bash
cd backend
python app.py
```

### Expected Startup Output
```text
Loaded 19 nodes, 21 edges from backend/data/photon_sprint1_graph_data.json
Baseline validation passed: True (0 errors)
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Accessing the Web Visualizer
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser. You will see:
- 4-Tier Interactive Supply Chain Graph (Suppliers $\to$ Parts $\to$ Products $\to$ Orders).
- Downstream ripple effect highlighting upon clicking any node.
- Live validation panel and execution latency benchmark drawer.
- Cascading deletion simulation with snapshot-based Undo (`Ctrl+Z`).

---

## 5. Running Tests & Benchmarks

With your virtual environment activated:

### 1. Execute All 73 Automated Tests
```bash
# From repository root:
pytest

# Verbose output:
pytest -v
```
*Expected: 73 passed in ~0.15 seconds with 0 failures.*

### 2. Measure Code Coverage
```bash
pytest --cov=backend.graph_validation --cov-report=term-missing
```
*Expected: ~91% coverage across the core validation engine.*

### 3. Run the Traversal Latency Benchmark
```bash
python -m backend.benchmarks.benchmark_tracing
```
*Expected: Overall Status: [PASS], 95th Percentile Latency ~0.005 ms (SLA Target: < 10.0 ms).*  
The benchmark also automatically updates `backend/reports/graph_benchmark_report.json`.

### 4. Run Code Style & Linter Checks
```bash
ruff check .
```
*Expected: All checks passed! (0 errors, 0 warnings).*

---

## 6. Verifying API Endpoints via Curl

With the server running on `http://127.0.0.1:5000`:

```bash
# 1. Fetch graph state
curl -s http://127.0.0.1:5000/api/graph | head -n 20

# 2. Run graph validation audit
curl -s http://127.0.0.1:5000/api/validation

# 3. Execute downstream reachability for Supplier SUP-01
curl -s http://127.0.0.1:5000/api/downstream/SUP-01

# 4. Preview cascading deletion impact for Part PART-01
curl -s http://127.0.0.1:5000/api/impact/PART-01

# 5. Execute 1,000-iteration traversal benchmark
curl -s http://127.0.0.1:5000/api/benchmark/tracing
```

---

## 7. Troubleshooting Guide

| Issue | Root Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'graph_validation'` | Python path does not include workspace root | Ensure `.venv` is activated. Execute using `python -m backend.app` or verify `pytest.ini` defines `pythonpath = backend .`. |
| `FileNotFoundError: photon_sprint1_graph_data.json` | Running from an unexpected working directory | The codebase automatically inspects candidate paths (`backend/data/`, `data/`, current working directory). Run from root or `backend/`. |
| `Address already in use: 5000` | Another process is bound to port 5000 (e.g. macOS AirPlay receiver or previous Flask instance) | Turn off AirPlay Receiver in macOS System Settings $\to$ Sharing, or specify an alternative port: `python -c "from backend.app import app; app.run(port=5050)"`. |
| `Activate.ps1 cannot be loaded` | PowerShell execution policy restriction on Windows | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window. |
| `networkx install error on Python 3.9` | `networkx 3.4.2` requires Python $\ge 3.10$ | `requirements.txt` specifies `networkx>=3.2.0`, which automatically resolves to `3.2.1` on Python 3.9 and `3.4.2` on Python 3.12+. Run `pip install -r requirements.txt`. |

