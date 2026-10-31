# Installation and Setup

## Prerequisites

- **Python**: Version 3.9 or higher (Python 3.9, 3.10, 3.11, or 3.12).
- **Git**: For version control.
- **Operating System**: macOS, Linux, or Windows (WSL recommended for Windows).

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EPAM-SPRINTS
```

### 2. Install Project Dependencies

Install the project and its dependencies directly using editable mode:

```bash
pip install -e .
```

This installs `flask`, `networkx`, and `pydantic` as configured in [`pyproject.toml`](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/pyproject.toml).

### 3. Configure Environment Variables (Optional)

Copy the sample environment file:

```bash
cp .env.example .env
```

Default settings in `.env.example` are pre-configured for local execution. See [Configuration](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/configuration.md) for available settings.

---

## Verification

Confirm that your environment is properly configured by running the test suite and linter:

```bash
# 1. Run full test suite (all 130 tests should pass)
python3 -m pytest backend/tests/ -v

# 2. Run Ruff code quality checks (0 errors)
python3 -m ruff check backend/ scripts/

# 3. Run standalone graph validation CLI
python3 scripts/validate_graph.py
```

If all three commands exit with code `0`, your environment is fully operational and ready for development.
