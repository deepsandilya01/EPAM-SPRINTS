# Configuration

## Overview

Application configuration is managed via the type-safe `Settings` dataclass in `backend/app/core/config.py`. Values can be overridden at runtime using environment variables or a `.env` file in the repository root.

---

## Environment Variables

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `PORT` | `int` | `5050` | Port for the Flask HTTP server to listen on. Render automatically supplies this in production. |
| `HOST` | `str` | `127.0.0.1` | Network interface host to bind to (`0.0.0.0` in Docker / cloud environments). |
| `FLASK_ENV` | `str` | `development` | Runtime environment name (`development`, `testing`, `production`). |
| `FLASK_DEBUG` | `str` | `0` | Enable Flask debug mode (`1` for true, `0` for false). |
| `SECRET_KEY` | `str` | *(internal default)* | Session signing key used for cookie validation if session state is enabled. |

---

## Application Constants & File Paths

The `Settings` instance (`get_settings()`) provides centralized, immutable path resolution:

```python
from backend.app.core.config import get_settings

settings = get_settings()

# Canonical dataset location:
# backend/app/data/datasets/scenario_dataset.json
print(settings.dataset_path)

# Static assets location:
# backend/app/static/
print(settings.static_dir)

# Performance SLA threshold:
# 10.0 ms
print(settings.max_traversal_latency_ms)
```

---

## Sample `.env` File

A pre-configured template is provided in `.env.example`:

```bash
PORT=5050
HOST=127.0.0.1
FLASK_ENV=development
FLASK_DEBUG=1
```

