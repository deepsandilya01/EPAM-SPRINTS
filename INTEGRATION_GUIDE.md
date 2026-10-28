# Integration Guide
`app.py` imports the reusable validators and exposes `GET /api/validation` and `GET /api/trace/<node_id>`. Existing graph, downstream, impact, delete, undo, and reset routes remain in place. Baseline validation reads immutable `RAW`; current structural validation examines `GRAPH` without requiring original counts.
