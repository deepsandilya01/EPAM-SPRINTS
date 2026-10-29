# Team Photon — Environment Setup & Installation Guide

> **Team:** LNCT Photon  
> **Project:** Proactive Supply-Chain Decision, Ripple & Recovery Intelligence System  
> **Component:** Sprint 1 — Environment Provisioning, Dependency Setup & Execution

---

## 1. Supported Prerequisites & Verified Software Versions

This application has been verified on the following operating systems and software environments:

| Component | Minimum Version | Verified Production Version | Purpose |
|---|---|---|---|
| **Python** | 3.10+ | **3.12.14 / 3.13.7** | Core runtime |
| **Flask** | 3.0.0 | **3.1.1** | Web API backend |
| **NetworkX** | 3.2.0 | **3.4.2** | Directed graph algorithms |
| **pytest** | 8.0.0 | **9.2.0** | Automated test runner |
| **pytest-cov** | 5.0.0 | **7.1.0** | Code coverage measurement |
| **Ruff** | 0.8.0 | **0.17.3** | Code quality & static analysis |
| **Operating System** | Windows 10/11, Ubuntu 22.04+, macOS 13+ | **Windows 11 (AMD64)** | Host platform |

---

## 2. Windows Installation (PowerShell)

Follow these step-by-step instructions in Windows PowerShell:

### Step 1: Open the Project Directory

```powershell
cd "d:\EPAM MVP-1\EPAM-SPRINTS-main\DynamicGraph"
```

### Step 2: Create a Virtual Environment

```powershell
# Using standard Python
python -m venv .venv

# Or using uv (high-speed package manager)
uv venv .venv
```

### Step 3: Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

> **Troubleshooting ExecutionPolicy**: If PowerShell displays `File .venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system`, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

### Step 4: Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Verify Python & Package Versions

```powershell
python -c "import flask, networkx, pytest; print(f'Verified: Flask {flask.__version__}, NetworkX {networkx.__version__}, Pytest {pytest.__version__}')"
```

Expected output:
```text
Verified: Flask 3.1.1, NetworkX 3.4.2, Pytest 9.2.0
```

---

## 3. Linux / macOS Installation (Bash / Zsh)

```bash
# 1. Navigate to directory
cd /path/to/DynamicGraph

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate
source .venv/bin/activate

# 4. Upgrade pip and install packages
pip install --upgrade pip
pip install -r requirements.txt

# 5. Verify installation
python3 -c "import flask, networkx, pytest; print('Environment Verified OK')"
```

---

## 4. Configuration & Dataset Paths

The application relies on canonical JSON data:

- **Dataset Location**: `photon_sprint1_graph_data.json` (at workspace root).
- **Static Assets**: `static/index.html` (served by Flask at `/`).
- **Generated Reports Directory**: `reports/` (stores validation and benchmark artifacts).
- **Test Suite**: `tests/` (configured in `pytest.ini`).

The application automatically resolves paths relative to `app.py`:
```python
BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "photon_sprint1_graph_data.json"
```

---

## 5. Running the Application

Start the Flask development server:

```powershell
python app.py
```

Console output confirms startup and pre-construction validation:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Access the application in your browser:
- **Local URL**: [http://127.0.0.1:5000](http://127.0.0.1:5000) or [http://localhost:5000](http://localhost:5000)

---

## 6. Verification Checklist

Run these four commands to verify that your environment is fully operational:

1. **Test Suite Verification**:
   ```powershell
   pytest -v
   ```
   *Expected: 73 passed in < 1 second.*

2. **Coverage Verification**:
   ```powershell
   pytest --cov=graph_validation --cov-report=term-missing
   ```
   *Expected: 91% code coverage across `graph_validation`.*

3. **Benchmarking Verification**:
   ```powershell
   python -m benchmarks.benchmark_tracing
   ```
   *Expected: Overall Status: [PASS], 95th Percentile Latency < 0.1 ms (Target: < 10.0 ms).*

4. **Linting Verification**:
   ```powershell
   ruff check .
   ```
   *Expected: All checks passed!*

---

## 7. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| `Activate.ps1 cannot be loaded` | PowerShell script restriction | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before activating. |
| `Address already in use` (Port 5000) | Another service or Flask process is bound to port 5000 | Kill occupying process or change port in `app.py`: `app.run(port=5050)`. |
| `ModuleNotFoundError: graph_validation` | Python cannot locate workspace root | Ensure `.venv` is active and run commands using `python -m ...`. Verify `pytest.ini` defines `pythonpath = .`. |
| `FileNotFoundError: photon_sprint1_graph_data.json` | Command executed from outside the project root | `cd` into the project directory before executing `python app.py`. |

