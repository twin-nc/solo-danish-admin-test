# CLAUDE.md — Danish Tax Administration Platform

This file is the authoritative instruction set for Claude when working on this project.
Read it fully before starting any task.

---

## 1. Project Identity

This is a **web-based administration platform for Danish VAT (moms) filing** used by
SKAT tax officers, platform administrators, and taxpayer businesses. It enforces Danish
tax law automatically — deadlines, penalties, momstilsvar calculations — so that no
user needs to compute these manually.

Key documents to read before any task:

| Document | Purpose |
|---|---|
| `PROJECT_OVERVIEW.md` | Business context, user roles, module descriptions |
| `ARCHITECTURE.md` | Technical patterns (layered, DDD events, hexagonal) |
| `AGENT_ROLES.md` | Authoritative agent responsibilities and rules |
| `AGENT_ARCHITECT_SPEC.md` | System design: data models, API contracts, auth |
| `AGENT_RESEARCHER_SPEC.md` | Danish tax law domain knowledge |
| `AGENT_DESIGN_SPEC.md` | UI components, design tokens, user flows |
| `AGENT_REVIEWER_SPEC.md` | Phase 1 review verdicts and required actions |

---

## 2. Multi-Agent Workflow — Strict Mode

This project uses a **structured multi-agent build system** defined in `AGENT_ROLES.md`.
Claude must respect this structure at all times:

- **Each agent owns its output file exclusively.** Never modify another agent's output file.
- **Agent roles are not combined unless explicitly instructed by the user.** If acting as
  the Backend Coder, do not make design decisions — defer to the Architect spec. If acting
  as the Architect, do not write production code.
- **Phase 2 does not start until all Phase 1 Reviewer blockers are resolved.** Before
  writing any code, confirm that all items in `AGENT_REVIEWER_SPEC.md` Section 7
  (Required Actions) have been addressed in the spec files.
- **Testing is iterative, not end-loaded.** A dedicated Testing Agent runs in parallel
  with coding agents in Phase 2 and validates each feature slice at recurring checkpoints.
- **Execution mode is containerized-first.** Agents should run build/test/lint/format
  commands via `docker compose ...` by default. Local host execution is fallback-only and
  must include a short reason when used.
- **No module may call another module's service directly.** All cross-module communication
  goes through the `EventBus` abstraction. This rule has no exceptions.
- **Agents do not gold-plate.** Produce only what the current task scope requires.
  No extra features, no speculative abstractions, no unrequested refactoring.

### Current phase status

| Phase | Status |
|---|---|
| Phase 1 — Research, architecture, design | Complete |
| Phase 1 Review | Complete (historical snapshot in `AGENT_REVIEWER_SPEC.md`; enforce unresolved gap handling via Section 10 before relevant module work) |
| Phase 2 — Backend and frontend development | **Ready to start for Modules 1 and 2 in tandem, with mandatory Testing Agent checkpoints and evidence per Section 7** |
| Phase 3 — Final regression and documentation | Not started (Testing Agent already active during Phase 2) |

---

## 3. Module-First Development Strategy

**Modules 1 and 2 are built in tandem.** The quality gate does not need to pass on
Module 1 before Module 2 work begins. Both modules should reach production quality
together before Module 3 starts.

The modules in build order:

1. **Module 1 — Registration** (Party + PartyRole — partially exists, needs container/K8s wiring)
2. **Module 2 — Authentication and Access Control** (JWT, roles, middleware) — built in tandem with Module 1
3. **Module 3 — VAT Filing (Momsangivelse)**
4. **Module 4 — Tax Assessment**
5. **Module 5 — Admin Dashboard**

Modules 1 and 2 together are considered complete when both pass the **quality gate**
in Section 6. Do not start Module 3 until the combined Module 1 + 2 gate passes.

---

## 4. Tech Stack — Open Source Only

All dependencies must be open source with no commercial licence restrictions.
Do not introduce any library that requires a paid licence or a commercial-only licence.

### Backend

| Concern | Tool | Notes |
|---|---|---|
| Language | Python 3.12 | Pin to 3.12 in all Dockerfiles and CI |
| Web framework | FastAPI | Async, OpenAPI auto-docs, Pydantic-native |
| ORM | SQLAlchemy 2.0 | Typed mapped columns only |
| Migrations | Alembic | One migration per schema change |
| Database | PostgreSQL 16 | Relational; all financial fields use `Numeric` not `Float` |
| Validation | Pydantic v2 | Request/response schemas only; no business logic in schemas |
| Testing | pytest + pytest-asyncio + httpx + pytest-mock | See Section 7 |
| Linting | ruff | Zero violations required |
| Formatting | ruff format | Replaces black |
| Coverage | pytest-cov | 90% minimum threshold enforced at the gate |
| ASGI server | uvicorn | Dev: `--reload`; prod: no `--reload`, multiple workers |

### Frontend

| Concern | Tool |
|---|---|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript (strict mode) |
| Styling | Tailwind CSS |
| State | Zustand (auth state only) |
| HTTP client | Native fetch wrapped in typed functions in `lib/api-client.ts` |
| Linting | ESLint (Next.js default config) |
| Formatting | Prettier |

### Infrastructure

| Concern | Tool |
|---|---|
| Local dev | Docker Compose (backend + frontend + PostgreSQL) |
| Container runtime | Docker (OCI-compliant images) |
| Orchestration (staging/prod) | Kubernetes |
| Image registry | GitHub Container Registry (GHCR) |
| CI/CD | GitHub Actions |

---

## 5. Container and Kubernetes Rules

### Docker Compose (local development)

- All services must be runnable with a single `docker compose up` from the project root.
- The `docker-compose.yml` must define three services: `db` (PostgreSQL), `backend`
  (FastAPI), `frontend` (Next.js).
- Local Compose images should use the same Dockerfiles and startup commands as CI/CD and Kubernetes deployments to preserve production parity.
- Health checks must be defined for every service.
- The backend container must run Alembic migrations on startup (`alembic upgrade head`)
  before uvicorn starts.
- Environment variables are injected via `.env` files; never hardcode secrets in
  Dockerfiles or compose files.
- Use official base images from Docker Hub (e.g. `python:3.12-slim`, `node:20-alpine`,
  `postgres:16-alpine`).

### Dockerfiles

- Use multi-stage builds for the frontend to keep the production image small.
- Backend: copy `requirements.txt` and install dependencies before copying source code
  (layer-cache efficiency).
- No `root` user in production images — create and switch to a non-root user.
- `.dockerignore` must exclude `venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`,
  `.env*`.

### Kubernetes (staging/prod)

- Kubernetes manifests live in `k8s/` at the project root.
- Use `Deployment` + `Service` + `Ingress` pattern for each service.
- Secrets are managed via Kubernetes `Secret` objects — never ConfigMaps for sensitive values.
- Resource `requests` and `limits` must be set on every container.
- Liveness and readiness probes must use the `/health` endpoint on the backend.

---

## 6. Quality Gate — Module Completion Criteria

A module may not be considered done until all of the following pass:

| Gate | Requirement |
|---|---|
| **Iterative checkpoint evidence** | For each feature slice, show test updates and checkpoint results (A/B/C/D as applicable) |
| **Tests — unit** | All pytest unit tests pass (`tests/unit/`) |
| **Tests — integration** | All pytest integration tests pass (`tests/integration/`) |
| **Tests — API** | All pytest API/e2e tests pass (`tests/api/`) |
| **Coverage** | `pytest --cov=app --cov-fail-under=90` exits 0 |
| **Linting** | `ruff check .` exits 0 with zero violations |
| **Formatting** | `ruff format --check .` exits 0 |
| **Container build** | `docker build -f Dockerfile .` exits 0 |

Run the gate in this order — fix each failure before proceeding to the next check.
Do not declare a module complete if any gate item fails.
Do not defer all testing to the end of a module; test evidence must be produced throughout implementation.

---

## 7. Testing Strategy

Follow the testing pyramid:

```
        ▲
       / \
      / API \      ← Few: full HTTP stack via TestClient
     /────────\
    / Integration\ ← Some: repository layer against real test DB
   /──────────────\
  /  Unit Tests    \ ← Many: service + handler logic with fakes/mocks
 /──────────────────\
```

### Parallel Testing Agent cadence (required)

- A dedicated Testing Agent runs in parallel with coding agents during Phase 2.
- Checkpoints run repeatedly (for example every 60-90 minutes or once per feature slice merge):
  - Checkpoint A: schema and contract checks
  - Checkpoint B: endpoint behavior checks
  - Checkpoint C: business-rule and permission checks
  - Checkpoint D: regression pass
- Minimum test bundle per new endpoint/workflow slice:
  - 1 happy-path test (`2xx` + expected payload shape)
  - 1 authorization/ownership test (`401/403/404`)
  - 1 validation/business-rule test (`400/409/422`)
  - 1 regression assertion for related existing behavior
- A slice is merge-ready only when new tests are added and passing, the full relevant suite passes (or approved known failures are documented), and no unresolved critical failures remain from prior checkpoints.
- Every reviewer/coordinator pass must include changed test files, exact commands executed, execution mode (`docker compose ...` preferred), and failing output severity (if any).

### Test isolation

- Use the **savepoint transaction strategy** from the existing `conftest.py`.
  No test leaves data in the database.
- Integration tests require a real PostgreSQL test database (see `conftest.py` fixture).
- The `FakeEventBus` from `ARCHITECTURE.md` is the standard mock for unit tests.

### What to test per layer

| Layer | What to assert |
|---|---|
| Unit (services) | Business rules, correct event published, correct repo calls |
| Integration (repositories) | ORM ↔ schema correctness, cascades, constraints |
| API (routers) | HTTP status codes, response shape, auth enforcement, error cases |

### Test file locations

```
tests/
├── conftest.py                  # shared fixtures
├── unit/
│   ├── test_party_service.py
│   └── test_party_handlers.py
├── integration/
│   └── test_party_repository.py
└── api/
    ├── test_parties.py
    └── test_roles.py
```

New modules follow the same layout — one unit file, one integration file, one API file
per module added.

### Running tests

```bash
# All tests
pytest

# Unit only (no database required)
pytest tests/unit/

# With coverage report
pytest --cov=app --cov-report=term-missing

# Gate coverage check
pytest --cov=app --cov-fail-under=90
```

---

## 8. Architecture Rules (Non-Negotiable)

These rules come directly from `ARCHITECTURE.md` and must never be violated:

1. **Routers never query the database directly.** Routers call services; services call
   repositories.
2. **Services never construct HTTP responses.** Services return domain objects or raise
   domain exceptions; routers translate these into HTTP responses.
3. **Repositories never contain business logic.** Repositories perform only data access.
4. **All cross-module communication goes through the EventBus.** No service in module A
   may import or call a service in module B directly.
5. **The EventBus is injected as an interface (ABC), not a concrete class.** This enables
   the `FakeEventBus` in tests and a future `RabbitMQEventBus` in production.
6. **All critical business logic is transactional.** Persistence completes before events
   are published. If the DB write fails, no event is published.

---

## 9. Key Business Rules (Domain Law — Do Not Invent)

These are legally mandated rules. Implement them exactly; do not simplify or approximatethem without citing a spec change.

| Rule | Implementation |
|---|---|
| `momstilsvar = A + C + E − B` | Computed by `FilingService._compute_momstilsvar`. Never entered directly by users. |
| One canonical filing per `(se_nummer, filing_period, angivelse_type)` | Enforced by a **partial unique index** `WHERE korrektionsangivelse = false`. Not a full unique constraint with `version`. |
| Monthly deadline: 25th of following month | `FilingService._compute_deadline` |
| Quarterly deadline: 10th of second month after quarter end | `FilingService._compute_deadline` |
| Semi-annual deadline: 1 Sep (H1) / 1 Mar (H2) | `FilingService._compute_deadline` |
| Late filings are accepted, not blocked | Record `late_filing_days` and `late_filing_penalty`; publish `FilingPenaltyAccrued`. Do not reject the filing. |
| Late filing fee is configurable | Stored in `VatPolicy.late_filing_fee_amount` — not hardcoded. |
| Corrections link to original | `original_filing_id` FK; original filing status set to `CORRECTED`. |
| 3-year correction window | Enforce in `FilingService.correct_filing`. |
| Taxpayer ownership at API layer | `filing.party_id == current_user.party_id`. TAXPAYER users receive 404 (not 403) for another party's data — never reveal that the record exists. |

---

## 10. Spec Gap Handling

Before writing code, check whether the relevant spec sections are complete.

**If a spec gap would produce incorrect or legally wrong code:**
- Stop and flag the gap explicitly to the user.
- State which spec file and section is incomplete.
- Reference the `AGENT_REVIEWER_SPEC.md` finding number if one exists.
- Do not invent a solution — wait for the gap to be resolved in the spec.

**Known gaps to resolve before Module 3 (VAT Filing) code starts:**

| Gap | Reviewer Reference | Required Action |
|---|---|---|
| `VatPolicy` model and `VatPolicyRepository` undefined | GAP 1, ACTION 3 | Add model, migration, and repo to `AGENT_ARCHITECT_SPEC.md` |
| Bank holiday calendar seeding | MISSING 1 | Define table, source, and seed strategy |
| `party_id` FK missing from `User` model | GAP 10, ACTION 2 | Add column and migration to `AGENT_ARCHITECT_SPEC.md` |
| Filing `UniqueConstraint` uses wrong key set | FINDING 1, ACTION 1 | Change to partial unique index |
| `GET /api/v1/dashboard/summary` has no implementation spec | GAP 9, ACTION 4 | Add schema and router stub |
| Agterskrivelse scope unresolved in `AGENT_ROLES.md` | GAP 5, ACTION 5 | Explicitly defer to Phase 3 |

These gaps do not block Module 1 (Registration) work, but must be resolved before
Module 3 code is written.

---

## 11. Naming Conventions

| Context | Convention |
|---|---|
| Python files, variables, functions | `snake_case` |
| Python classes | `PascalCase` |
| Python constants | `UPPER_SNAKE_CASE` |
| TypeScript variables, functions | `camelCase` |
| TypeScript types, interfaces, components | `PascalCase` |
| Database columns | `snake_case` |
| API response JSON fields | `camelCase` (via Pydantic `alias` or `model_config`) |
| Danish domain terms in DB/code | Use Danish spelling where the Architect spec specifies it (e.g. `se_nummer`, `kvitteringsnummer`, `afregningsperiode_type`) |

---

## 12. CI/CD Pipeline (GitHub Actions)

The pipeline runs on every pull request and push to `main`.

Pipeline steps in order:

1. **Lint** — `ruff check .`
2. **Format check** — `ruff format --check .`
3. **Unit tests** — `pytest tests/unit/` (no database service required)
4. **Integration + API tests** — `pytest tests/integration/ tests/api/` (requires
   PostgreSQL service container)
5. **Coverage gate** — `pytest --cov=app --cov-fail-under=90`
6. **Container build** — `docker build -f Dockerfile .`
7. **Push to GHCR** — on `main` only, after all checks pass
8. **Auto deploy** — on `main`, run the Kubernetes deployment workflow using the newly published images

Use `python:3.12-slim` as the test runner image. Use the `postgres:16-alpine` service
container for integration tests.

---

## 13. Environment Variables

Never hardcode secrets. The following variables are required:

```
DATABASE_URL=postgresql://user:pass@db:5432/vatri_db
SECRET_KEY=<random 32-byte hex>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development|staging|production
```

Provide a `.env.example` with placeholder values. The real `.env` is gitignored.

---

## 14. What Claude Must Not Do

- **Do not modify another agent's output file** (e.g. do not edit `AGENT_ARCHITECT_SPEC.md`
  while acting as the Backend Coder).
- **Do not introduce commercial-licence dependencies.**
- **Do not start the next module before the current module's quality gate passes.**
- **Do not hardcode fee amounts, interest rates, or bank holidays** — these must come from
  the `VatPolicy` table.
- **Do not call another module's service directly** — use the EventBus.
- **Do not use `Float` for monetary values** — use `Numeric`/`Decimal` throughout.
- **Do not return 403 to a TAXPAYER for another party's data** — return 404.
- **Do not implement agterskrivelse** in Phase 2 — it is explicitly deferred to Phase 3.
- **Do not invent solutions to spec gaps** — flag them and wait for resolution.
