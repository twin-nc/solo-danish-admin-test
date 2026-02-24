# Agent Plan — Danish Tax Administration Platform

## Current State

The project has a fully working **Python/FastAPI backend** for the Registration module:

- PostgreSQL + SQLAlchemy 2.0 + Alembic migrations
- Layered architecture (Router → Service → Repository → Model)
- Domain events via an abstract EventBus (InMemoryEventBus, swappable to RabbitMQ/Kafka)
- 14 passing integration tests with full transaction isolation
- 5 API endpoints: health, register party, get party, assign role, list roles

**What does not exist yet:**
- Frontend (no UI at all)
- Authentication / authorisation
- Tax Filing module
- Tax Assessment module

---

## Agent Roles

### Researcher Agent
Researches Danish tax administration — with a focus on Danish VAT (moms) — and provides continuous input on requirements from legal, procedural, and practical perspectives. Runs at every phase and iterates with the Architect and Designer agents to ensure the platform reflects real Danish tax law and SKAT procedures.

**Responsibilities:**
- Research Danish VAT law (momslov), filing periods, deadlines, penalties, and required fields
- Research Danish business registration (CVR, business types, SKAT registration process)
- Analyse skat.dk (especially skat.dk/erhverv and TastSelv Erhverv) for real-world system context
- Map the end-to-end procedural flow from business registration to VAT assessment
- Review Architect and Designer specs and identify gaps, missing fields, and incorrect assumptions
- Produce actionable recommendations for data model corrections, business rule enforcement, and UI/UX alignment with SKAT conventions

**Output:** `AGENT_RESEARCHER_SPEC.md`
**Iterates with:** Architect Agent, Designer Agent

---

### Architect Agent
Designs all system components that do not yet exist, producing a single spec file that all Coder agents use as their source of truth.

**Responsibilities:**
- Define the frontend architecture (Next.js + TypeScript)
- Design JWT-based authentication (login, refresh, roles: admin, officer, taxpayer)
- Design the Tax Filing module following existing patterns (services / repositories / routers / events)
- Design the Tax Assessment module (same pattern)
- Define all new API contracts and request/response schemas
- Define new domain events and event handlers
- Document how all modules communicate through the event bus

**Output:** `AGENT_ARCHITECT_SPEC.md`

---

### Designer Agent
Defines the visual design, component library, and user flows for the admin platform UI.

**Responsibilities:**
- Design the admin dashboard layout (overview stats, recent registrations, filing status)
- Design Registration, Filing, and Assessment pages
- Define the component library (tables, forms, cards, modals, status badges, navigation)
- Define design tokens (Danish government-inspired palette: navy blues, whites, greys, accent colours)
- Map user flows for each role (admin, officer, taxpayer)
- Define responsive layout breakpoints

**Output:** `AGENT_DESIGN_SPEC.md`

---

### Frontend Coder Agent
Implements the Next.js frontend using the Designer's spec and Architect's API contracts.

**Responsibilities:**
- Scaffold the Next.js + TypeScript project under `frontend/`
- Implement authentication pages (login, logout, token refresh)
- Implement the admin dashboard
- Implement Registration views (register party, view party, assign role)
- Implement Filing views (submit filing, view filings)
- Implement Assessment views (view assessments, status tracking)
- Connect all views to the backend API using typed API clients

**Input:** `AGENT_ARCHITECT_SPEC.md`, `AGENT_DESIGN_SPEC.md`
**Output:** `frontend/` directory

---

### Backend Coder Agent
Implements new backend modules following the existing architecture patterns.

**Responsibilities:**
- Implement the Tax Filing module (`app/routers/filings.py`, `app/services/filing.py`, `app/repositories/filing.py`, `app/models/filing.py`)
- Implement the Tax Assessment module (same structure)
- Implement JWT authentication middleware and user model
- Add Alembic migrations for all new tables
- Wire new modules into `app/main.py`
- Publish and handle domain events between modules

**Input:** `AGENT_ARCHITECT_SPEC.md`
**Output:** New modules inside `app/`, new Alembic migration files

---

## Phase 3 Agents (Later)

### Test Agent
Writes automated tests for all new code following the existing testing patterns.

**Responsibilities:**
- Write API integration tests for Filing and Assessment endpoints
- Write tests for authentication (login, token validation, role enforcement)
- Write tests for new event handlers
- Ensure test isolation using the existing savepoint transaction strategy

**Input:** All new code from Coder agents
**Output:** `tests/test_filings.py`, `tests/test_assessments.py`, `tests/test_auth.py`

---

### Docs Agent
Generates and updates all project documentation.

**Responsibilities:**
- Update `ARCHITECTURE.md` to reflect new modules and authentication
- Generate `API_DOCS.md` covering all endpoints with request/response examples
- Write a `SETUP.md` covering local development, environment variables, and running the full stack
- Document the event flow between all modules

**Input:** All code, `AGENT_ARCHITECT_SPEC.md`
**Output:** Updated `ARCHITECTURE.md`, new `API_DOCS.md`, new `SETUP.md`

---

## Execution Phases

### Phase 1 — Parallel
Run Architect, Designer, and Researcher agents simultaneously. Researcher reviews and iterates with Architect and Designer outputs.

```
Phase 1:
  Architect Agent   ──→  AGENT_ARCHITECT_SPEC.md
  Designer Agent    ──→  AGENT_DESIGN_SPEC.md
  Researcher Agent  ──→  AGENT_RESEARCHER_SPEC.md
                         (reviews Architect + Designer specs; provides legal/procedural feedback)
```

### Phase 2 — After Phase 1
Run Frontend Coder and Backend Coder agents in parallel. Both consume Phase 1 outputs.

```
Phase 2:
  Frontend Coder Agent  ──→  frontend/
  Backend Coder Agent   ──→  app/ (new modules)
```

### Phase 3 — After Phase 2
Run Test and Docs agents in parallel once all code exists.

```
Phase 3:
  Test Agent  ──→  tests/ (new test files)
  Docs Agent  ──→  ARCHITECTURE.md, API_DOCS.md, SETUP.md
```

---

## Handoff Flow

```
Researcher Agent ──→ (reviews + annotates) ──→ Architect Agent ──┐
                                                                   ├──→ Frontend Coder Agent ──→ Test Agent ──→ Docs Agent
                                              Designer Agent   ──┘
                                                                   └──→ Backend Coder Agent  ──→ Test Agent ──→ Docs Agent
```

The Researcher Agent runs continuously across phases. Its output (`AGENT_RESEARCHER_SPEC.md`) is an input to all Coder agents alongside the Architect and Designer specs.

---

## Technology Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Frontend framework | Next.js + TypeScript | App Router, SSR, type safety |
| Auth strategy | JWT (access + refresh tokens) | Stateless, works well with FastAPI |
| Auth storage | HttpOnly cookies | Secure, not accessible to JS |
| Component styling | Tailwind CSS | Utility-first, consistent with design tokens |
| API communication | fetch with typed response models | No extra dependency, matches Pydantic schemas |
| Future event bus | RabbitMQ or Kafka | Already abstracted via EventBus ABC |
| New backend modules | Same patterns as Registration | Consistency, no relearning curve |

---

## File Map After All Phases Complete

```
solo_danish_test/
├── app/                          # Backend (Python/FastAPI)
│   ├── main.py
│   ├── config.py
│   ├── db/
│   ├── models/                   # + filing.py, assessment.py, user.py
│   ├── schemas/                  # + filing.py, assessment.py, auth.py
│   ├── repositories/             # + filing.py, assessment.py
│   ├── services/                 # + filing.py, assessment.py
│   ├── events/                   # + filing_events.py, assessment_events.py
│   └── routers/                  # + filings.py, assessments.py, auth.py
├── frontend/                     # Frontend (Next.js/TypeScript) — NEW
│   ├── app/
│   │   ├── (auth)/login/
│   │   ├── dashboard/
│   │   ├── registrations/
│   │   ├── filings/
│   │   └── assessments/
│   ├── components/
│   ├── lib/
│   └── types/
├── alembic/
│   └── versions/                 # + new migration files
├── tests/                        # + test_filings.py, test_assessments.py, test_auth.py
├── ARCHITECTURE.md               # Updated
├── TESTING.md
├── API_DOCS.md                   # NEW
├── SETUP.md                      # NEW
├── AGENT_PLAN.md                 # This file
├── AGENT_ARCHITECT_SPEC.md       # Generated by Architect Agent
├── AGENT_DESIGN_SPEC.md          # Generated by Designer Agent
└── AGENT_RESEARCHER_SPEC.md      # Generated by Researcher Agent
```

---

## Notes

- All agents must follow the existing naming conventions and code style.
- No agent modifies another agent's output files directly.
- The orchestrator (Claude Code) coordinates handoffs between phases.
- Agents in the same phase run in parallel and work on non-overlapping files.
- The event bus remains the only cross-module communication mechanism — modules never call each other's services directly.
