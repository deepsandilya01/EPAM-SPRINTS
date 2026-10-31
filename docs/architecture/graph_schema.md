# Graph Schema Specification

> **Sprint 1 Ownership & Task Assignment**
> - **Primary Owner**: Deep
> - **Role**: Graph Domain Models and Data Contracts
> - **File**: `docs/architecture/graph_schema.md`
> - **Status**: NOT STARTED

### File Purpose
Defines the topological schema, node classifications, edge relationship semantics, and validation constraints for the RE:Flow supply chain dependency network.

### Primary Responsibilities
- Formalize canonical node attributes and data types across all 4 tiers.
- Formalize edge relationship semantics (SUPPLIES, USED_IN, FULFILLS).
- Document tier ordering rules and DAG acyclicity constraints.
- Coordinate model contracts with Ansh, Aadee, Preetam, and Soumya.

### Dependencies
- Mishti: Baseline scenario requirements.
- Anushka: Approved scenario dataset structure.

### Expected Deliverables
- Canonical graph schema reference documentation.

---

## Purpose
Defines the topological schema, node classifications, edge relationship semantics, and validation constraints for the RE:Flow supply chain dependency network.

## Schema Definition
- **Node Tiers**:
  - Suppliers
  - BOM Parts
  - Finished Products
  - Customer Orders
- **Relationship Constraints**:
  - `SUPPLIES`: Supplier -> BOM Part
  - `USED_IN`: BOM Part -> Finished Product
  - `FULFILLS`: Finished Product -> Customer Order

## TODO
- [ ] Formalize node attribute dictionaries and required fields.
- [ ] Specify edge weight and metadata schemas.
- [ ] Document cycle prevention and DAG validation rules.
