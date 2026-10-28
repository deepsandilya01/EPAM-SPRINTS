# Frontend Validation Guide
The existing D3 page adds a **Graph Validation** button and panel. It fetches `/api/validation`, displays baseline and current-graph status separately, and lists actual errors. Traversal performance remains a separate API concern at `/api/trace/<node_id>`; no timing result is used as a validation pass.
