# System Architecture - RE:Flow

> **Sprint 1 Ownership & Task Assignment**
> - **Primary Owner**: Sumit
> - **Role**: Documentation and Demo Guide
> - **File**: `docs/architecture/system_architecture.md`
> - **Status**: NOT STARTED

### File Purpose
This document provides an overview of the RE:Flow system architecture, detailing the design of the single Python backend service, graph representation engine, and static demo deployment.

### Primary Responsibilities
- Document overall system architecture diagram and component interactions.
- Document single Python backend design pattern using Flask.
- Document static HTML/CSS/JS bundling and serving strategy.
- Document Render unified deployment architecture.
- Coordinate architectural documentation across the development team.

### Architecture Attribution & Dependencies
RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.
- Deployment configuration in render.yaml (Team Maintained).

### Expected Deliverables
- Comprehensive system architecture document with component boundaries.

---

## Purpose
This document provides an overview of the RE:Flow system architecture, detailing the design of the single Python backend service, graph representation engine, and static demo deployment.

## Architecture Overview

RE:Flow's overall system architecture and repository structure were collaboratively designed and discussed by the entire project team. Deep and Divyanshu contributed to architecture coordination and review, while the final architectural decisions reflect collective team discussions and requirements.

- **Backend Service**: Single Python backend application hosting REST APIs and serving static assets.
- **Graph Representation**: Directed Graph (DiGraph) managed via NetworkX.
- **Data Persistence**: JSON-based scenario datasets loaded into memory.
- **Frontend Visualization**: Static HTML, CSS, and Vanilla JavaScript demo served directly by the backend.
- **Deployment Platform**: Render unified web service hosting both API and static demo.

## TODO
- [ ] Document component interaction diagrams.
- [ ] Detail memory and scaling characteristics.
- [ ] Define deployment topology and Render build lifecycle.
