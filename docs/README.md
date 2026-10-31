# RE:Flow — Documentation Hub

Welcome to the comprehensive documentation for **RE:Flow** (Team Photon's Proactive Supply-Chain Decision, Ripple & Recovery Intelligence System), developed for **Sprint 1: Supply Chain Graph & Scenario Generator**.

---

## System Overview

RE:Flow is a lightweight, high-performance supply chain dependency graph platform built using **Python**, **Flask**, and **NetworkX**. It models end-to-end multi-tier supply chain networks as a strict Directed Acyclic Graph (DAG) and provides real-time downstream reachability tracing, cascading disruption simulation, structural validation, and interactive D3.js visualization.

```
Supplier (Tier 1) ──[SUPPLIES]──> Part (Tier 2) ──[USED_IN]──> Product (Tier 3) ──[FULFILLS]──> Customer Order (Tier 4)
```

---

## Key Technical Highlights

- **Pure DAG Topological Model**: Enforces strict acyclic dependencies across 4 discrete tiers (2 Suppliers, 5 Parts, 2 Products, 10 Orders = 19 nodes, 21 edges).
- **Sub-Millisecond Downstream Tracing**: Breadth-First Search (BFS) traversal executes in under 0.005 ms (p95), outperforming the 10.0 ms SLA by over 2,500x.
- **Modular Validation Engine**: Independent, single-responsibility modules (`models.py`, `cycles.py`, `nodes.py`, `edges.py`, `validator.py`, `reporting.py`) supporting both baseline dataset verification and live mutation integrity auditing.
- **Cascading Disruption & Recovery**: Interactive node removal cascades downstream across dependent parts, products, and customer orders, backed by full undo/reset recovery.
- **Zero-Dependency Frontend**: Pure HTML5, CSS3, and D3.js v7 bundled and served directly by Flask.

---

## Documentation Index

| Document | Description |
| :--- | :--- |
| [Architecture](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/architecture.md) | System layers, data flow, component interactions, and Mermaid architecture diagram |
| [Project Structure](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/project-structure.md) | Complete directory and module inventory with exact responsibilities |
| [Installation & Setup](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/installation-and-setup.md) | Prerequisites, repository setup, and dependency installation |
| [Running Locally](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/running-locally.md) | Starting the local development server, environment variables, and CLI tools |
| [Configuration](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/configuration.md) | Configuration settings, environment variables, and defaults |
| [Graph Model](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/graph-model.md) | 4-tier DAG specification, node attributes, edge direction rules, and schemas |
| [Validation](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/validation.md) | Modular validation architecture, dual-mode auditing, and error codes |
| [API Reference](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/api-reference.md) | Exhaustive REST API reference for all 11 registered route endpoints |
| [Frontend](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/frontend.md) | D3.js visualization layout, node styling, interactivity, and control panels |
| [Testing](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/testing.md) | Pytest test suite architecture (130 tests), execution instructions, and coverage |
| [Benchmarking](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/benchmarking.md) | Latency benchmarking methodology, 10ms SLA verification, and CLI scripts |
| [Deployment](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/deployment.md) | Render PaaS configuration, WSGI entrypoints, and runtime considerations |
| [Troubleshooting](file:///Users/deepsandilya01/Projects/EPAM-SPRINTS/docs/troubleshooting.md) | Common errors, port conflicts, environment verification, and recovery steps |

