# Team Photon — Sprint 2 | Preetam's Feature 8

## Feature
**FastAPI REST API & Swagger / OpenAPI Documentation Lead** — Exposing the end-to-end 5-stage temporal disruption simulation engine through high-performance RESTful endpoints with Pydantic request validation, automated Swagger UI documentation, and CORS enablement for frontend consumption.

## Acceptance Criteria Ownership
- **AC-10**: Simulation results accessible via FastAPI endpoint (`POST /api/v1/simulation/disrupt` returns HTTP 200 with full simulation payload in <25ms).

---

## Files in this Contribution
- `backend/app/schemas/disruption.py` — `DisruptionRequest` and `SimulationResponse` Pydantic models with field-level boundary validations and schema examples.
- `backend/app/api/routes/disruptions.py` — FastAPI `APIRouter` defining:
  - `POST /api/v1/simulation/disrupt` (and alias `/disruptions`): Core simulation execution endpoint.
  - `GET /api/v1/simulation/benchmark` (and alias `/disruptions/benchmark`): Instant canonical 8h benchmark evaluation endpoint.
- `backend/app/api/__init__.py` — Router mounting onto `api_router` under the `/api` prefix.

---

## Official Benchmark API Contract

### Request:
```http
POST /api/v1/simulation/disrupt HTTP/1.1
Host: localhost:5001
Content-Type: application/json

{
  "supplier_id": "SUP-01",
  "disruption_type": "SUPPLIER_DELAY",
  "delay_duration_hours": 8.0,
  "description": "Canonical 8-hour supplier delay scenario"
}
```

### Expected Response (`200 OK`):
```json
{
  "status": "success",
  "event": {
    "supplier_id": "SUP-01",
    "disruption_type": "SUPPLIER_DELAY",
    "delay_duration_hours": 8.0
  },
  "impact": {
    "disrupted_supplier": "SUP-01",
    "affected_parts": ["P-01"],
    "affected_products": ["PROD-01", "PROD-02"],
    "affected_orders": ["ORD-01", "ORD-02", "ORD-03"]
  },
  "depletion_timeline": [ ... ],
  "stockout": {
    "stockout_hour": 8.0,
    "total_breached": 2,
    "breached_orders": [
      {"order_id": "ORD-01", "delivery_deadline_hours": 10.0, "will_fail": true},
      {"order_id": "ORD-02", "delivery_deadline_hours": 12.0, "will_fail": true}
    ]
  },
  "intervention": {
    "stockout_hour": 8.0,
    "current_hour": 0.0,
    "recovery_lead_time_hours": 5.0,
    "delta_t_hours": 3.0,
    "is_feasible": true,
    "status": "FEASIBLE",
    "affected_order_ids": ["ORD-01", "ORD-02"]
  },
  "execution_time_ms": 12.4
}
```

---

## Error Handling Specifications
- **HTTP 422 Unprocessable Entity**: Triggered when validation fails (e.g. `delay_duration_hours <= 0` or unrecognized `supplier_id`).
- **HTTP 500 Internal Server Error**: Handled gracefully if simulation pipeline encounters internal failures.

---

## Interactive Swagger Documentation
Interactive API docs are served natively via FastAPI at:
- **Swagger UI:** `http://localhost:5001/docs` (Tag: `Disruption Simulation`)
- **ReDoc:** `http://localhost:5001/redoc`
- **OpenAPI JSON:** `http://localhost:5001/openapi.json`

---

## Run Verification Tests
Run from the collaboration repository root:

```bash
pytest -q backend/tests/unit/test_simulation_engine.py -k "test_ac10"
```

---

## Integration Contract
- **Inputs Consumed**:
  - **Ansh (Feature 7)**: Consumes `simulation_service.simulate_from_params()` / `run_disruption_simulation()` master pipeline.
  - **Divyanshu (Feature 1)**: Consumes `DisruptionType` and validation models.
- **Outputs Produced**:
  - **Deep (Feature 10)**: Provides `POST /api/v1/simulation/disrupt` with enabled CORS (`allow_origins=["*"]`) for frontend D3 chart and timeline scrubber.
  - **Soumya (Feature 9)**: Provides target endpoint for automated FastAPI `TestClient` verification.
  - **Sumit (Feature 12)**: Provides API contract specifications for final `docs/api-reference.md` compilation.
