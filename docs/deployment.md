# Production Deployment Guide (Render)

## Overview

RE:Flow is configured for automated cloud deployment on **Render** using a native Infrastructure-as-Code manifest ([`render.yaml`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/render.yaml)). The deployment requires zero external databases (no SQL, no MongoDB, no Redis) and bundles both the Flask API backend and D3.js visualization frontend into a single web service. Render is the sole supported deployment target.

---

## Render Manifest Configuration

The deployment specification in [`render.yaml`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/render.yaml):

```yaml
services:
  - type: web
    name: reflow
    env: python
    buildCommand: "pip install -e ."
    startCommand: "python backend/app/main.py"
    envVars:
      - key: PORT
        value: 10000
      - key: FLASK_ENV
        value: production
```

---

## Deployment Steps

### 1. Connect Repository to Render
1. Log in to the [Render Dashboard](https://dashboard.render.com/).
2. Select **"New +"** → **"Blueprint"**.
3. Connect your repository (`EPAM-SPRINTS`).
4. Render automatically parses `render.yaml` and provisions the `reflow` Web Service.

### 2. Manual Web Service Creation (Alternative)
If not using the Blueprint workflow, configure the Web Service manually:
- **Environment**: `Python 3`
- **Build Command**: `pip install -e .`
- **Start Command**: `python backend/app/main.py`
- **Health Check Path**: `/api/health`

---

## Application Entrypoint

The Flask application in [`backend/app/main.py`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/backend/app/main.py) provides both a callable application object and an application factory:

- **Direct Execution**: `python backend/app/main.py` (reads `PORT` from environment, defaulting to `5050` locally or `10000` on Render).
- **Application Factory**: `create_app()` for WSGI test harnesses and fixtures.

---

## In-Memory Runtime Characteristics

1. **Zero Database Footprint**: The application does not require any database infrastructure. All scenario datasets are loaded from immutable JSON files at startup.
2. **Stateless Restarts**: In-memory mutations (such as simulating a node disruption via `DELETE /api/node/<id>`) are maintained in process memory. Service restarts or redeployments automatically reset the graph to the canonical 19-node baseline.
3. **Reset Endpoint**: The `/api/reset` endpoint allows instantaneous state restoration to the canonical baseline without restarting the process.
