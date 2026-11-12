# RE:Flow — Team PHOTON
# Complete System Architecture & Codebase Understanding
### Simple Hinglish Documentation | EPAM Project

---

## 1. Project Introduction — Humne Kya Build Kiya Hai?

RE:Flow ek Supply Chain Decision Intelligence System hai.

Simple language mein samjho:

Ek company apne products manufacture karti hai. Uske liye different suppliers se raw materials aur components aate hain. Ye components finished products banane mein use hote hain. Finally, products customers ke orders fulfil karte hain.

Ab maan lo kisi supplier ke yahan delay ho gaya.

Toh company ko ye samajhna hota hai:

- Kaunsa supplier affected hai?
- Us supplier se kaun-kaun se parts connected hain?
- Kaunse finished products impact honge?
- Kaunse customer orders affect ho sakte hain?
- Supply chain mein impact kitna downstream ja sakta hai?

RE:Flow ka objective supply chain ke relationships ko graph ke form mein represent karna aur un relationships ko analyze karna hai.

**Current Sprint 1 implementation:** Supply Chain Graph & Scenario Generator.

Abhi system ka primary focus graph creation, graph validation, downstream dependency tracing aur visualization hai.

Disruption simulation, optimization aur recovery intelligence future sprint capabilities hain. Inhe current implemented features nahi samajhna hai.

---

## 2. Technology Stack — Kis Technology Ka Kya Kaam Hai?

| Technology | Project mein responsibility |
|---|---|
| Python | Backend programming language |
| Flask | Backend application aur API server |
| NetworkX | Supply chain graph create aur analyze karna |
| HTML | Frontend page structure |
| CSS | Frontend styling |
| JavaScript | Frontend interaction aur API communication |
| D3.js | Graph visualization |
| JSON | Synthetic supply chain dataset |
| Pytest | Automated testing |
| Ruff | Python code quality checks |
| Render | Application deployment |

### Simple understanding

- Flask application ko run karta hai.
- NetworkX graph ke nodes aur relationships manage karta hai.
- JSON initial supply chain data provide karta hai.
- JavaScript backend se data fetch karta hai.
- D3.js graph ko browser mein visually show karta hai.
- Pytest verify karta hai ki application expected behaviour de rahi hai.
- Render application ko online host karta hai.

---

## 3. Complete Project Folder Structure

Current repository reports ke according project ka relevant structure:

```text
EPAM-SPRINTS/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── render.yaml
│
├── docs/
│   ├── README.md
│   ├── team-guide.md
│   ├── architecture.md
│   ├── project-structure.md
│   ├── installation-and-setup.md
│   ├── running-locally.md
│   ├── configuration.md
│   ├── graph-model.md
│   ├── validation.md
│   ├── api-reference.md
│   ├── frontend.md
│   ├── testing.md
│   ├── benchmarking.md
│   └── troubleshooting.md
│
├── scripts/
│   ├── run_local.py
│   ├── validate_graph.py
│   └── run_benchmarks.py
│
└── backend/
    │
    ├── pytest.ini
    ├── reports/
    │   ├── graph_benchmark_report.json
    │   └── graph_validation_report.json
    │
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   │
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── routes/
    │   │       ├── __init__.py
    │   │       ├── benchmarks.py
    │   │       ├── graph.py
    │   │       ├── health.py
    │   │       ├── traversal.py
    │   │       └── validation.py
    │   │
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── constants.py
    │   │   └── exceptions.py
    │   │
    │   ├── data/
    │   │   ├── __init__.py
    │   │   ├── loader.py
    │   │   ├── datasets/
    │   │   │   └── scenario_dataset.json
    │   │   └── schemas/
    │   │       └── graph_schema.json
    │   │
    │   ├── graph/
    │   │   ├── __init__.py
    │   │   ├── builder.py
    │   │   ├── operations.py
    │   │   └── traversal.py
    │   │
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── edges.py
    │   │   ├── graph.py
    │   │   └── nodes.py
    │   │
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── graph.py
    │   │   ├── traversal.py
    │   │   └── validation.py
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── benchmark_service.py
    │   │   ├── graph_service.py
    │   │   └── validation_service.py
    │   │
    │   ├── static/
    │   │   ├── sprint-1-demo.html
    │   │   ├── css/
    │   │   │   └── sprint-1-demo.css
    │   │   └── js/
    │   │       └── sprint-1-demo.js
    │   │
    │   └── validation/
    │       ├── __init__.py
    │       ├── models.py
    │       ├── cycles.py
    │       ├── nodes.py
    │       ├── edges.py
    │       ├── validator.py
    │       └── reporting.py
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── fixtures/
        │   └── sample_scenario.json
        ├── integration/
        │   ├── __init__.py
        │   └── test_api.py
        └── unit/
            ├── __init__.py
            ├── test_api_schemas.py
            ├── test_domain_models.py
            ├── test_edge_cases.py
            ├── test_graph.py
            ├── test_traversal.py
            └── test_validation.py
```

Note: Ye latest available project reports se reconstructed structure hai. Final sharing se pehle current Git working tree se tree match kar lena.

---

# 4. Root-Level Files — Project Ki Main Configuration

## `.env.example`

Is file mein environment variables ke example/default configuration placeholders rakhe jaate hain.

Purpose:
- Developer ko required configuration samjhana.
- Local setup mein environment variables ka reference dena.
- Sensitive values ko actual source code mein hardcode karne se bachana.

Actual secrets ya passwords is file mein nahi hone chahiye.

## `.gitignore`

Git ko batata hai ki kaun-si files repository mein track nahi karni hain.

Examples:
- Python cache files.
- Local environment files.
- Temporary generated files.

## `pyproject.toml`

Ye Python project ki main configuration file hai.

Ismein:
- Project metadata.
- Python dependencies.
- Build configuration.
- Development tooling configuration.

Project dependencies install karne ka documented mechanism:

```bash
pip install -e .
```

## `README.md`

Project ka main introduction.

Koi developer repository open kare, toh use sabse pehle README se samajh aana chahiye:
- Project kya hai?
- Kaunsi technology use hui hai?
- Project kaise run karna hai?
- Documentation kahan available hai?

## `render.yaml`

Render deployment configuration.

Ismein current deployment ke liye build aur start commands define hain.

Reported configuration:

```yaml
buildCommand: pip install -e .
startCommand: python backend/app/main.py
```

Actual values ko `render.yaml` se verify karna chahiye.

---

# 5. `docs/` — Complete Documentation Folder

Ye folder code execute nahi karta. Iska purpose developers ko project samjhana hai.

| File | Kya explain karti hai? |
|---|---|
| `README.md` | Documentation ka starting point |
| `team-guide.md` | Complete architecture & codebase guide (Hinglish) |
| `architecture.md` | System architecture aur component flow |
| `project-structure.md` | Har folder aur file ki responsibility |
| `installation-and-setup.md` | Dependencies aur setup |
| `running-locally.md` | Local application execution |
| `configuration.md` | Environment variables aur settings |
| `graph-model.md` | Nodes, edges aur graph relationships |
| `validation.md` | Graph validation ka complete process |
| `api-reference.md` | Backend API endpoints |
| `frontend.md` | HTML, CSS, JavaScript aur D3.js |
| `testing.md` | Test suite aur execution commands |
| `benchmarking.md` | Performance measurement |
| `troubleshooting.md` | Common errors aur solutions |

**Team ke liye:** Naye developer ko sabse pehle `docs/README.md`, `team-guide.md`, `architecture.md` aur `project-structure.md` padhna chahiye.

---

# 6. `scripts/` — Developer Utility Scripts

Is folder mein manually run kiye jaane wale helper scripts hain.

## `run_local.py`

Purpose: Local development ke liye application run karne mein help karna.

Developer ko baar-baar long startup commands yaad rakhne ki zaroorat nahi hoti.

## `validate_graph.py`

Purpose: Dataset aur graph validation execute karna.

Example:

```bash
python3 scripts/validate_graph.py
```

Ye check karne ke kaam aata hai ki graph defined structural rules follow karta hai ya nahi.

## `run_benchmarks.py`

Purpose: Graph traversal performance measure karna.

Example:

```bash
python3 scripts/run_benchmarks.py --iterations 1000
```

Isse downstream tracing ka execution time measure hota hai.

Important: Ye scripts application ke main business logic ka replacement nahi hain. Ye developer aur verification utilities hain.

---

# 7. `backend/` — Main Backend Application

Ye project ka backend area hai.

Backend ki responsibility:
1. Dataset load karna.
2. Graph construct karna.
3. Graph operations execute karna.
4. Graph validate karna.
5. APIs ke through frontend ko data dena.

## `backend/app/main.py`

**Backend application ka main entry point.**

Is file ko application ka starting point samjho.

Responsibilities:
- Flask application initialize karna.
- Configuration load karna.
- API routes register karna.
- Static frontend serving configure karna.
- Application startup manage karna.

Jab application start hoti hai, execution isi entry point se hota hai.

Example:

```bash
python backend/app/main.py
```

Exact startup behaviour current implementation ke according follow hota hai.

---

# 8. `backend/app/api/` — API Layer

API layer frontend aur backend ke beech communication handle karti hai.

Simple example:

Frontend ko graph chahiye.

Frontend request bhejta hai:

```http
GET /api/graph
```

Flask request ko appropriate route handler tak bhejta hai.

## `api/__init__.py`

API blueprints aur route registration ko organize karta hai.

## `api/routes/`

Is folder mein individual API route handlers hain.

### `health.py`

Health endpoint.

```http
GET /api/health
```

Purpose:
- Application running status.
- Basic service health information.

### `graph.py`

Graph-related endpoints.

```http
GET /api/graph
DELETE /api/node/<node_id>
POST /api/undo
POST /api/reset
```

Purpose:
- Graph data frontend ko provide karna.
- Node-related graph operations.
- Undo aur reset actions handle karna.

### `traversal.py`

Downstream traversal requests handle karta hai.

Example:

```http
GET /api/downstream/<node_id>
POST /api/traversal
```

Purpose:
- Given node se downstream connected nodes identify karna.
- Traversal result API response mein dena.

### `validation.py`

Graph validation endpoint.

```http
GET /api/validation
```

Purpose:
- Graph validation execute karna.
- Validation result aur errors return karna.

### `benchmarks.py`

Benchmark-related API endpoints.

Example:

```http
GET /api/benchmark/tracing
GET /api/benchmarks
```

Purpose:
- Graph traversal benchmark information provide karna.

Note: Ye routes current reported API map par based hain. Exact request/response details `docs/api-reference.md` aur actual route handlers se verify karni chahiye.

---

# 9. `backend/app/core/` — Shared Application Configuration

Core folder mein application-wide common configuration aur definitions hain.

## `config.py`

Application settings manage karta hai.

Example responsibilities:
- Port/configuration values.
- Environment-based settings.
- Dataset/report paths.

## `constants.py`

Common constants aur fixed definitions rakhta hai.

Isse same values ko multiple files mein baar-baar define nahi karna padta.

## `exceptions.py`

Application-specific exception definitions.

Purpose:
- Errors ko clearly represent karna.
- Common error handling ko consistent rakhna.

Core folder ka purpose business logic ko store karna nahi, balki common application-level support provide karna hai.

---

# 10. `backend/app/data/` — Dataset Management

Ye folder initial supply chain data aur usse related loading/schema files manage karta hai.

## `data/loader.py`

JSON dataset read/load karne ka responsibility.

Simple flow:

1. Dataset file locate hoti hai.
2. JSON data read hota hai.
3. Loaded data graph builder ko provide kiya jaata hai.

## `data/datasets/scenario_dataset.json`

Ye current synthetic supply chain dataset hai.

Current Sprint 1 dataset:

- 2 Suppliers
- 5 BOM Parts
- 2 Finished Products
- 10 Customer Orders

Total:

**19 Nodes**

## `data/schemas/graph_schema.json`

Graph dataset ke expected structure ko describe karta hai.

Purpose:
- Expected fields ka reference.
- Node aur relationship structure define karna.

Important difference:

`graph_schema.json` dataset structure define karta hai, jabki `validation/` ka Python code actual validation logic execute karta hai.

---

# 11. `backend/app/graph/` — Graph Engine Integration

Ye project ka core graph-processing area hai.

NetworkX ka use supply chain relationships represent aur analyze karne ke liye hota hai.

## `builder.py`

Purpose: Raw dataset ko NetworkX graph mein convert karna.

Input:

```text
Supplier
BOM Part
Finished Product
Customer Order
```

Output: Connected graph structure.

## `operations.py`

Purpose: Graph par operations execute karna.

Examples:
- Node add/delete.
- Edge-related operations.
- Graph mutation.
- Graph state operations.

Exact supported operations source code se defined hote hain.

## `traversal.py`

Purpose: Graph traversal aur downstream dependency tracing.

Example:

```text
SUP-01
  |
  v
PART-01
  |
  v
PROD-01
  |
  v
ORD-01
```

Agar `SUP-01` affected hai, toh traversal connected downstream entities identify kar sakta hai.

**Simple understanding:** `builder.py` graph banata hai, `operations.py` graph ko modify karta hai aur `traversal.py` graph mein connected entities find karta hai.

---

# 12. `backend/app/models/` — Domain Models

Models project ke main domain entities ko represent karte hain.

## `nodes.py`

Node-related definitions.

Examples:
- Supplier
- BOM Part
- Finished Product
- Customer Order

## `edges.py`

Relationships ya connections ki definitions.

Examples:
- SUPPLIES
- USED_IN
- FULFILLS

## `graph.py`

Graph-related domain model definitions.

Purpose:
- Graph structure ko represent karna.
- Graph-related model responsibilities ko organize karna.

Difference samjho:

`models/` mein domain representation hoti hai.

`graph/` mein graph construct aur operate hota hai.

---

# 13. `backend/app/schemas/` — Data Structure Contracts

Schema ka purpose hai input/output data ka expected format define karna.

## `graph.py`

Graph-related request/response structure.

## `traversal.py`

Traversal-related request/response structure.

## `validation.py`

Validation-related request/response structure.

### Models vs Schemas

| Models | Schemas |
|---|---|
| Domain entities represent karte hain | Data structure contracts define karte hain |
| Supplier, Part, Product | API input/output format |
| Graph relationships | Traversal request structure |
| Business-level representation | Data validation/serialization structure |

In dono folders ka purpose alag hai.

---

# 14. `backend/app/services/` — Application-Level Business Coordination

Services API routes aur lower-level functionality ke beech coordination karte hain.

## `graph_service.py`

Graph-related operations ko coordinate karta hai.

Examples:
- Graph data provide karna.
- Graph traversal coordinate karna.
- Graph mutations handle karna.

## `validation_service.py`

Validation subsystem ko application services ke saath integrate karta hai.

Purpose:
- Graph validation execute karwana.
- Validation results ko API/reporting layer tak pahunchana.

## `benchmark_service.py`

Benchmark execution aur result coordination.

Purpose:
- Traversal timing measurements.
- Benchmark results prepare karna.

### API vs Services vs Graph

Example:

```text
Frontend
   |
   v
API Route
   |
   v
Service
   |
   v
Graph Engine / Validation
   |
   v
Result
   |
   v
Service
   |
   v
API Response
   |
   v
Frontend
```

API request receive karta hai.

Service actual application-level work coordinate karta hai.

Graph/Validation module specific processing execute karta hai.

---

# 15. `backend/app/validation/` — Graph Validation Subsystem

Ye subsystem ensure karta hai ki graph expected rules follow kare.

Pehle validation kaafi bada implementation ek hi file mein tha.

Ab responsibilities separate modules mein divide ki gayi hain.

## `models.py`

Validation-related data models aur enums.

Examples:
- ValidationReport
- ValidationError
- ValidationCheck
- ValidationPolicy
- CheckStatus
- Severity

Ye validation results ko structured form mein represent karne mein help karta hai.

## `nodes.py`

Node validation.

Checks:
- Node category.
- Required node information.
- Unique node IDs.
- Tier-specific attributes.

## `edges.py`

Relationship validation.

Checks:
- Edge endpoints.
- Missing references.
- Relationship names.
- Valid tier progression.
- Edge direction rules.

## `cycles.py`

Cycle detection aur DAG validation.

Purpose:
- Graph mein cycle check karna.
- Graph acyclic hai ya nahi verify karna.

DAG ka full form Directed Acyclic Graph hai.

Simple meaning: Directed graph jisme directed cycle nahi hoti.

## `validator.py`

Ye high-level validation orchestrator hai.

Iska kaam different validation modules ko coordinate karna hai.

Example:

```text
validate_graph()
      |
      ├── Node Validation
      |
      ├── Edge Validation
      |
      ├── Cycle Validation
      |
      └── Validation Result
```

## `reporting.py`

Validation result ko readable format mein present aur persist karne ka kaam.

Examples:
- Terminal report formatting.
- JSON validation report output.

## `__init__.py`

Public imports/re-exports provide karta hai.

Isse existing modules validation functions ko consistent package interface se import kar sakte hain.

---

# 16. `backend/app/static/` — Frontend Application

Important: Is project mein frontend separately hosted React application nahi hai.

Flask existing static frontend files serve karta hai.

## `sprint-1-demo.html`

Frontend ka main HTML page.

Responsibilities:
- Page structure.
- Graph container.
- Dashboard sections.
- Controls aur visual elements.

## `static/css/sprint-1-demo.css`

Frontend styling.

Responsibilities:
- Layout.
- Colors.
- Typography.
- Graph presentation.
- Responsive styling.

## `static/js/sprint-1-demo.js`

Frontend interaction aur API communication.

Responsibilities:
- API requests.
- Graph data receive karna.
- D3.js visualization.
- User interaction.
- Graph updates ko screen par reflect karna.

### D3.js ka role

D3.js graph data ko visual representation mein convert karta hai.

Example:

Backend se:

```json
{
  "nodes": [],
  "edges": []
}
```

Frontend mein:
- Nodes circles/cards ke form mein show ho sakte hain.
- Edges connecting lines ke form mein show hote hain.
- Node relationships visually understandable bante hain.

Simple difference:

- HTML structure deta hai.
- CSS design deta hai.
- JavaScript behaviour deta hai.
- D3.js graph visualization deta hai.

---

# 17. `backend/tests/` — Automated Testing

Testing folder verify karta hai ki project ka code expected behaviour follow kar raha hai.

## `conftest.py`

Pytest fixtures aur common test setup.

## `fixtures/sample_scenario.json`

Tests ke liye sample graph dataset.

## `integration/test_api.py`

Different backend components aur API behaviour ko integration level par test karta hai.

## `unit/test_api_schemas.py`

API schema validation tests.

## `unit/test_domain_models.py`

Domain model tests.

## `unit/test_edge_cases.py`

Boundary conditions aur unusual scenarios test karta hai.

## `unit/test_graph.py`

Graph construction aur operations test karta hai.

## `unit/test_traversal.py`

Downstream traversal behaviour test karta hai.

## `unit/test_validation.py`

Validation rules aur validation results test karta hai.

### Testing ka simple example

Agar `SUP-01` se downstream traversal karte hain, toh test check karta hai ki expected downstream nodes return hue ya nahi.

Reported latest test result:

```text
130 passed
```

---

# 18. `backend/reports/` — Generated Reports

Is folder mein generated verification reports rakhe jaate hain.

## `graph_validation_report.json`

Graph validation ka generated output.

Purpose:
- Validation result.
- Graph structure checks.
- Validation status.

## `graph_benchmark_report.json`

Performance benchmark ka generated output.

Purpose:
- Traversal performance measurements.
- Timing statistics.
- Benchmark result.

Ye source dataset nahi hain. Ye generated reports hain.

---

# 19. Complete End-to-End Application Workflow

Ab samjho ki application start hone ke baad actual flow kaise work karta hai.

## Step 1 — Application Startup

```text
python backend/app/main.py
          |
          v
    Flask Application
          |
          v
   Configuration Load
          |
          v
    API Registration
          |
          v
   Dataset Initialization
```

Application startup par Flask initialize hota hai aur configured routes register hote hain.

## Step 2 — Dataset Loading

```text
scenario_dataset.json
          |
          v
       loader.py
          |
          v
      Raw JSON Data
```

Dataset load hokar graph construction process ko diya jaata hai.

## Step 3 — Graph Construction

```text
Raw JSON Dataset
        |
        v
    builder.py
        |
        v
 NetworkX DiGraph
        |
        v
   19 Nodes / 21 Edges
```

Graph mein nodes aur relationships construct hote hain.

## Step 4 — Graph Validation

```text
Constructed Graph
        |
        v
   validator.py
        |
        ├── nodes.py
        |
        ├── edges.py
        |
        └── cycles.py
        |
        v
  Validation Result
        |
        v
    reporting.py
```

Graph ko defined structural rules ke against check kiya jaata hai.

## Step 5 — Backend Service Layer

```text
API Request
     |
     v
Route Handler
     |
     v
Relevant Service
     |
     v
Graph / Validation Module
     |
     v
Result
```

## Step 6 — Frontend Request

```text
Browser
   |
   v
sprint-1-demo.html
   |
   v
sprint-1-demo.js
   |
   v
Flask API
   |
   v
JSON Response
   |
   v
D3.js
   |
   v
Graph Visualization
```

Frontend backend se graph information leta hai aur browser mein display karta hai.

---

# 20. Important API Workflow Examples

## Example A — Graph Load Karna

```text
User opens dashboard
        |
        v
JavaScript sends GET /api/graph
        |
        v
graph.py
        |
        v
graph_service.py
        |
        v
NetworkX Graph
        |
        v
JSON Response
        |
        v
D3.js renders graph
```

## Example B — Downstream Traversal

Suppose user `SUP-01` select karta hai.

```text
User selects SUP-01
        |
        v
GET /api/downstream/SUP-01
        |
        v
traversal.py
        |
        v
graph_service.py
        |
        v
graph/traversal.py
        |
        v
NetworkX downstream traversal
        |
        v
Affected connected nodes
        |
        v
Frontend highlights results
```

## Example C — Graph Validation

```text
GET /api/validation
        |
        v
validation.py
        |
        v
validation_service.py
        |
        v
validation/validator.py
        |
        ├── nodes.py
        ├── edges.py
        └── cycles.py
        |
        v
Validation Report
        |
        v
API JSON Response
```

---

# 21. Sprint 1 Graph Model — Team Ko Kya Samajhna Hai?

Current graph structure:

```text
Supplier
   |
   | SUPPLIES
   v
BOM Part
   |
   | USED_IN
   v
Finished Product
   |
   | FULFILLS
   v
Customer Order
```

Current dataset:

| Entity | Quantity |
|---|---:|
| Suppliers | 2 |
| BOM Parts | 5 |
| Finished Products | 2 |
| Customer Orders | 10 |
| Total Nodes | 19 |
| Total Edges | 21 |

### Relationship Meaning

**SUPPLIES**

Supplier component provide karta hai.

**USED_IN**

BOM Part finished product manufacture karne mein use hota hai.

**FULFILLS**

Finished Product customer order fulfil karta hai.

### Current Performance Result

Reported benchmark:

- SUP-01 downstream traversal mean: approximately 0.00325 ms.
- SUP-02 downstream traversal mean: approximately 0.00406 ms.
- Aggregate p95: approximately 0.00408 ms.

Ye results current 19-node/21-edge synthetic dataset aur tested environment ke liye hain. Enterprise-scale performance ka proof nahi hain.

---

# 22. Team Ownership — Kaun Kya Samjhayega?

Actual historical file-wise contributor mapping available nahi hai. Isliye neeche recommended ownership diya gaya hai.

Team members ko unke actual code contribution ke according assign karo.

| Recommended Owner | Folder / Files | Kya Explain Karna Hai |
|---|---|---|
| Member 1 — Backend Lead | `main.py`, `core/` | Application startup aur configuration |
| Member 2 — Data & Model Developer | `data/`, `models/`, `schemas/` | Dataset, nodes, edges aur data structure |
| Member 3 — Graph Developer | `graph/` | NetworkX, graph builder, operations aur traversal |
| Member 4 — Validation Developer | `validation/` | Node, edge, cycle checks aur validation flow |
| Member 5 — API Developer | `api/routes/` | Endpoints aur request-response flow |
| Member 6 — Service Developer | `services/` | Business coordination aur service integration |
| Member 7 — Frontend Developer | `static/` | HTML, CSS, JavaScript aur D3.js |
| Member 8 — Testing Developer | `tests/`, `scripts/` | Unit tests, integration tests, CLI aur benchmarks |
| Member 9 — DevOps / Documentation | `render.yaml`, `docs/`, root config | Setup, documentation aur Render deployment |

Agar team size 9 se different hai, toh related responsibilities combine kar sakte ho.

### Presentation Rule

Har member ko apne assigned folder ke saath ye 5 questions answer karne aane chahiye:

1. Is folder ka purpose kya hai?
2. Is folder ki main files kaun-si hain?
3. Ye files ek doosre se kaise connected hain?
4. Iska input kya hai aur output kya hai?
5. Agar is folder mein error aaye toh kaunsi files inspect karni hongi?

### File Ownership vs Presentation Ownership

Ye dono same hona zaroori nahi hai.

- **Code Owner:** Jisne implementation mein contribution diya.
- **Module Explainer:** Jo team meeting mein us module ko explain karega.

Actual contributors ki mapping Git history, PRs aur team task records se verify karni hogi. Recommended presentation owner ko actual developer contribution ke roop mein present mat karna.

---

# 23. Team Members Ke Liye Folder-Wise Learning Order

Agar kisi member ko project samajhna hai, toh is order mein padhe:

1. `README.md` — Project overview.
2. `docs/team-guide.md` — Team onboarding & architecture guide.
3. `docs/architecture.md` — System architecture.
4. `backend/app/main.py` — Application startup.
5. `backend/app/data/` — Dataset loading.
6. `backend/app/models/` — Domain entities.
7. `backend/app/graph/` — Graph construction and operations.
8. `backend/app/validation/` — Graph validation.
9. `backend/app/services/` — Service coordination.
10. `backend/app/api/routes/` — API endpoints.
11. `backend/app/static/` — Frontend.
12. `backend/tests/` — Testing.
13. `scripts/` and `render.yaml` — Utilities and deployment.

Is sequence se project ko top-to-bottom samajhna easy hoga.

---

# 24. How to Run the Project

Repository root se:

### Install dependencies

```bash
pip install -e .
```

### Start application

```bash
python backend/app/main.py
```

### Run tests

```bash
python3 -m pytest backend/tests/ -v
```

### Run lint checks

```bash
python3 -m ruff check backend/ scripts/
```

### Validate graph

```bash
python3 scripts/validate_graph.py
```

### Run benchmark

```bash
python3 scripts/run_benchmarks.py --iterations 1000
```

Exact port aur configuration `config.py` aur `main.py` se check karein.

---

# 25. Current Implementation vs Future Development

Team ko ye difference clearly pata hona chahiye.

| Capability | Current Status |
|---|---|
| Synthetic supply chain dataset | Implemented |
| NetworkX graph construction | Implemented |
| Node and edge relationships | Implemented |
| Graph validation | Implemented |
| Cycle/DAG validation | Implemented |
| Downstream traversal | Implemented |
| Graph API | Implemented |
| Frontend graph visualization | Implemented |
| Benchmarking | Implemented |
| Disruption event simulation | Future sprint |
| Temporal ripple propagation | Future sprint |
| Stockout timestamp prediction | Future sprint |
| Intervention window calculation | Future sprint |
| OR-Tools recovery optimization | Future sprint |
| Human approval and audit workflow | Future sprint |

Important: Future capabilities ko demo ke time current working features ke roop mein claim nahi karna hai.

---

# 26. Final Architecture Summary

Poore project ko ek simple line mein samjho:

**Data → Graph Construction → Validation → Services → APIs → Frontend Visualization**

Aur developer responsibilities ko samjho:

- Data folder data provide karta hai.
- Models folder entities represent karta hai.
- Graph folder graph build aur process karta hai.
- Validation folder graph rules check karta hai.
- Services folder application operations coordinate karta hai.
- API folder frontend requests handle karta hai.
- Static folder UI display karta hai.
- Tests folder correctness verify karta hai.
- Scripts folder manual verification aur benchmarking support karta hai.
- Docs folder developers ko complete system samjhata hai.

## Team PHOTON — Shared Understanding

Har team member ko sirf apni file ka code nahi samajhna chahiye. Use ye bhi pata hona chahiye ki uski file se pehle kaunsa component data bhejta hai aur uske baad kaunsa component result consume karta hai.

Isi understanding se team ek individual-file-based development approach se end-to-end system development approach par move karti hai.

**Our goal:** Har developer ko apna module deeply samajh aaye aur saath hi poore RE:Flow system ka workflow bhi clear ho.

