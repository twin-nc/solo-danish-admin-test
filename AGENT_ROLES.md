# Agent Roles — Danish Tax Administration Platform

This document is the authoritative reference for every agent in the multi-agent build system. It defines what each agent is responsible for, what it is explicitly **not** responsible for, what inputs it consumes, and what outputs it produces.

---

## Overview

| Agent | Phase | Runs In Parallel With | Output File |
|---|---|---|---|
| Researcher | 1 | Architect, Designer | `AGENT_RESEARCHER_SPEC.md` |
| Architect | 1 | Researcher, Designer | `AGENT_ARCHITECT_SPEC.md` |
| Designer | 1 | Researcher, Architect | `AGENT_DESIGN_SPEC.md` |
| Reviewer | 1 Review | — (sequential gate) | `AGENT_REVIEWER_SPEC.md` |
| Backend Coder | 2 | Frontend Coder | New modules in `app/` |
| Frontend Coder | 2 | Backend Coder | `frontend/` directory |
| Test | 3 | Docs | New files in `tests/` |
| Docs | 3 | Test | `ARCHITECTURE.md`, `API_DOCS.md`, `SETUP.md` |

---

## Agent Definitions

---

### 1. Researcher Agent

**One-line summary:** Grounds the platform in real Danish tax law, SKAT procedures, and actual system conventions — and surfaces gaps when other agents get it wrong.

#### Purpose
The Researcher ensures that every business rule, data field, deadline, status value, and procedural step in the platform reflects how the Danish tax system actually works. It is the domain expert in the team. Its findings are authoritative over any assumption made by the Architect or Designer when the two conflict.

#### Responsibilities
- Research Danish VAT law (Momsloven), including: filing periods, registration thresholds, rubrik fields (A–E), tax calculation rules (momstilsvar = A + C + E − B), and penalty structures
- Research Danish business registration: CVR number format and validation (8-digit, modulus-11), SE number structure and purpose, VAT registration process at Erhvervsstyrelsen and Skattestyrelsen
- Analyse skat.dk (especially `skat.dk/erhverv` and TastSelv Erhverv) to understand real-world terminology, UI conventions, and procedural flows
- Map the end-to-end journey from business registration → VAT registration → momsangivelse → skatteansættelse
- Review the Architect's data model for missing or incorrectly typed fields (e.g. field names that do not match SKAT terminology, wrong data types, missing unique constraints)
- Review the Designer's UI wireframes for forms that reference non-existent fields, incorrect status labels, or procedural flows that do not match SKAT practice
- Produce actionable corrections: specific field additions, type changes, constraint additions, and status vocabulary corrections

#### Not Responsible For
- Making architectural decisions about technology or system structure
- Designing UI components or layouts
- Writing code or migrations

#### Inputs
- `skat.dk` and public Danish tax documentation
- `AGENT_ARCHITECT_SPEC.md` (to review for domain accuracy)
- `AGENT_DESIGN_SPEC.md` (to review for domain accuracy)

#### Output
**`AGENT_RESEARCHER_SPEC.md`** — structured research findings covering:
- Danish VAT law summary with citable sources
- Field-by-field corrections to the Architect's data model
- Status vocabulary corrections (Danish terms: KLADDE, INDSENDT, GODKENDT, etc.)
- Deadline and penalty schedule
- Identified gaps and recommended additions
- A summary verdict on each spec reviewed

---

### 2. Architect Agent

**One-line summary:** Designs all system components that do not yet exist — the technical source of truth for all Coder agents.

#### Purpose
The Architect defines how the system is built: module boundaries, data models, API contracts, authentication strategy, event schemas, and migration plan. Every Coder agent builds from this spec. It must be complete, internally consistent, and follow the existing patterns in the codebase.

#### Responsibilities
- Define the frontend architecture (Next.js 14+, App Router, TypeScript, Tailwind CSS, Zustand)
- Design JWT-based authentication: login, token refresh, logout, role model (admin, officer, taxpayer), HttpOnly cookie storage
- Design the Tax Filing module following the existing layered pattern: Router → Service → Repository → Model → Schema → Events
- Design the Tax Assessment module (same pattern)
- Define all new API endpoints: HTTP method, path, request schema, response schema, auth requirement, role restriction
- Define new domain events (name, payload fields, publisher, subscribers)
- Define Alembic migration files needed for all new tables
- Document how all modules communicate through the EventBus (no direct service-to-service calls)
- Produce Python code stubs or pseudocode for all major components

#### Not Responsible For
- Domain knowledge of Danish tax law (defers to Researcher)
- Visual design, UI layout, or user flows (defers to Designer)
- Writing production-ready implementation code (defers to Coder agents)

#### Inputs
- Existing codebase (to maintain consistency with patterns in Registration module)
- `AGENT_RESEARCHER_SPEC.md` (to incorporate legal/domain corrections)

#### Output
**`AGENT_ARCHITECT_SPEC.md`** — covering:
- Frontend architecture and file tree
- Authentication design (token strategy, middleware, role guard)
- Data models for all new tables (SQLAlchemy 2.0 mapped columns)
- Pydantic schemas (request/response)
- Repository interfaces
- Service method signatures and business logic descriptions
- Event definitions and handler registrations
- Full API contract table (all endpoints)
- Alembic migration plan

---

### 3. Designer Agent

**One-line summary:** Defines the visual language, component library, and user flows for the admin platform UI — grounded in the SKAT design system.

#### Purpose
The Designer ensures the platform looks and behaves like a credible Danish government administration tool. It draws directly from the visual conventions of `skat.dk` and the Danish government's Det Fælles Designsystem (DDS). The output is the single reference for the Frontend Coder agent.

#### Responsibilities
- Establish design tokens: colour palette (SKAT navy `#004B87`, greys, whites, accent), typography (Source Sans Pro), spacing scale, border radius, shadow levels
- Design the admin dashboard layout: stat cards, recent registrations table, filing status overview
- Design all primary pages: Login, Dashboard, Parties List, Party Detail, Register Party, Filings List, Filing Detail, Create Filing (Momsangivelse), Assessments List, Assessment Detail
- Define the component library: Button, Badge/StatusChip, DataTable, FormField, Card, PageHeader, SideNav, StatCard, Modal, Toast — with all variants and states
- Map user flows for each role (admin, officer, taxpayer): entry point, available pages, permitted actions
- Define responsive layout behaviour (desktop primary, tablet-aware)
- Ensure WCAG 2.1 AA compliance in colour contrast and interactive element sizing
- Use SKAT terminology for all UI labels (Danish terms where appropriate, consistent with skat.dk)

#### Not Responsible For
- Technology or framework decisions (defers to Architect)
- Domain law and procedural accuracy (defers to Researcher)
- Implementing any code (defers to Frontend Coder)

#### Inputs
- `skat.dk` (visual reference)
- Det Fælles Designsystem documentation
- `AGENT_RESEARCHER_SPEC.md` (for correct Danish terminology and status labels)
- `AGENT_ARCHITECT_SPEC.md` (to know what fields and endpoints exist)

#### Output
**`AGENT_DESIGN_SPEC.md`** — covering:
- Design tokens (as CSS custom properties and Tailwind config)
- Component specifications (all variants, states, props)
- Page wireframes (annotated layouts)
- User flow diagrams (step-by-step transitions per role)
- Frontend file tree (`frontend/` directory structure)

---

### 4. Reviewer Agent

**One-line summary:** Quality gate and critic — interrogates the accuracy, coherence, and justification of all Phase 1 outputs before any code is written.

#### Purpose
The Reviewer is the team lead who reads all Phase 1 work with a critical eye. Its job is not to redesign anything — it is to ask hard questions, surface contradictions between specs, and verify that domain knowledge has been applied correctly. Phase 2 does not start until the Reviewer has signed off.

The Reviewer's standard is: *"If a developer picked up these three specs and started building today, would they have everything they need, and would what they build actually reflect how Danish VAT administration works?"*

#### Responsibilities

**Cross-spec coherence:**
- Verify that every field shown in the Designer's UI forms exists in the Architect's data model
- Verify that every API endpoint referenced in the Designer's user flows is defined in the Architect's API contract
- Verify that the Architect's data model incorporates the Researcher's corrections (Rubrik A-E fields, CVR/SE numbers, afregningsperiode types, frist deadlines, agterskrivelse fields)
- Identify any place where one spec assumes something that another spec has not defined

**Domain accuracy:**
- Challenge specific claims in the Researcher's spec: are the deadlines correct? are the penalty amounts accurate? is the CVR validation rule correctly stated?
- Challenge the Architect's use of Danish terminology: are status values in Danish where they should be? are field names aligned with SKAT conventions?
- Challenge the Designer's labels and terminology: are Danish terms spelled correctly? do status badges match the status values in the Architect's schema?

**Decision justification:**
- For every significant architectural decision (JWT vs session, HttpOnly vs localStorage, InMemoryEventBus vs direct call, etc.) — ask whether the rationale holds and whether alternatives were considered
- For every design decision that deviates from skat.dk conventions — ask whether the deviation is intentional and justified

**Gap detection:**
- Identify responsibilities that no agent has claimed (e.g. who handles an expired VAT registration? who handles a late filing penalty calculation?)
- Identify fields that the Researcher recommended but that did not appear in the Architect's final model
- Identify user flows the Designer described that have no corresponding API endpoint

#### Not Responsible For
- Proposing wholesale redesigns or alternative architectures
- Writing code, migrations, or UI components
- Conducting additional domain research (defers to Researcher)

#### Inputs
- `AGENT_ARCHITECT_SPEC.md`
- `AGENT_DESIGN_SPEC.md`
- `AGENT_RESEARCHER_SPEC.md`

#### Output
**`AGENT_REVIEWER_SPEC.md`** — structured as:
- **Executive Summary:** overall verdict (ready for Phase 2 / conditional / blocked)
- **Cross-spec coherence findings:** list of inconsistencies with specific references (spec name, section, line)
- **Domain accuracy findings:** challenged claims with reasoning
- **Decision justification findings:** unjustified decisions flagged for resolution
- **Gap analysis:** unresolved responsibilities and missing definitions
- **Section verdicts:** pass / flag / reject per major section of each spec
- **Required actions before Phase 2:** explicit list of items that must be resolved

#### Blocking Rule
**Phase 2 (Coder agents) does not start until the Reviewer has produced its output and the orchestrator has confirmed all blocking issues are resolved.**

---

### 5. Backend Coder Agent

**One-line summary:** Implements all new backend modules — Auth, Filing, Assessment — following the existing layered architecture patterns.

#### Purpose
The Backend Coder translates the Architect's spec (as corrected by the Reviewer) into production-quality Python code. It follows the patterns already established in the Registration module exactly — no new patterns, no framework changes.

#### Responsibilities
- Implement the Auth module: `app/models/user.py`, `app/schemas/auth.py`, `app/repositories/user.py`, `app/services/auth.py`, `app/routers/auth.py`
- Implement the Filing module: `app/models/filing.py`, `app/schemas/filing.py`, `app/repositories/filing.py`, `app/services/filing.py`, `app/events/filing_events.py`, `app/routers/filings.py`
- Implement the Assessment module (same structure)
- Implement JWT middleware and role guard dependencies
- Write Alembic migrations for all new tables (migrations 0002–0005)
- Wire all new routers and event handlers into `app/main.py`
- Implement domain event publishing and handler registration via the existing EventBus abstraction
- Implement momstilsvar calculation on filing submission (A + C + E − B)
- Implement filing deadline (frist) calculation per afregningsperiode type

#### Not Responsible For
- Frontend code (defers to Frontend Coder)
- Test files (defers to Test Agent)
- Documentation (defers to Docs Agent)

#### Inputs
- `AGENT_ARCHITECT_SPEC.md`
- `AGENT_RESEARCHER_SPEC.md` (for domain-specific business logic)
- `AGENT_REVIEWER_SPEC.md` (for corrections to incorporate)
- Existing codebase (Registration module as the pattern reference)

#### Output
- New Python modules inside `app/`
- New Alembic migration files in `alembic/versions/`
- Updated `app/main.py`

---

### 6. Frontend Coder Agent

**One-line summary:** Implements the Next.js frontend — all pages, components, and API client — using the Designer's spec and Architect's API contracts.

#### Purpose
The Frontend Coder builds the complete UI as defined by the Designer, wired to the backend API as defined by the Architect. It uses TypeScript throughout and connects to the backend using typed fetch clients that mirror the Pydantic schemas.

#### Responsibilities
- Scaffold the Next.js 14+ project under `frontend/` with App Router, TypeScript, and Tailwind CSS
- Implement authentication pages and HttpOnly cookie handling (login, token refresh middleware)
- Implement the admin dashboard (stat cards, recent activity tables)
- Implement all Registration views: Parties List, Party Detail, Register Party modal, Assign Role
- Implement all Filing views: Filings List, Filing Detail, Create Momsangivelse form (Rubrik A-E fields), Submit, Correction
- Implement all Assessment views: Assessments List, Assessment Detail, Status update, Agterskrivelse action
- Build all components defined in the Designer's spec: Button, Badge, DataTable, FormField, Card, PageHeader, SideNav, StatCard, Modal, Toast
- Implement role-based navigation (admin sees all; officer sees filings and assessments; taxpayer sees own filings)
- Connect all views to the backend via typed API client functions in `lib/api-client.ts`
- Implement Zustand store for auth state

#### Not Responsible For
- Backend code or migrations (defers to Backend Coder)
- Test files (defers to Test Agent)
- Documentation (defers to Docs Agent)

#### Inputs
- `AGENT_ARCHITECT_SPEC.md` (API contracts and schemas)
- `AGENT_DESIGN_SPEC.md` (components, tokens, pages, user flows)
- `AGENT_REVIEWER_SPEC.md` (corrections to incorporate)

#### Output
- Complete `frontend/` directory

---

### 7. Test Agent

**One-line summary:** Writes integration tests for all new code following the existing savepoint transaction isolation pattern.

#### Purpose
The Test Agent ensures that every new endpoint, business rule, auth flow, and event handler is covered by an automated test. It follows the exact same patterns as the existing 14-passing tests in the Registration module.

#### Responsibilities
- Write integration tests for all Filing endpoints: create, list, get by ID, submit, correction
- Write integration tests for all Assessment endpoints: create, list, get by ID, update status, agterskrivelse
- Write tests for the Auth flow: login (valid credentials), login (invalid credentials), token refresh, logout, protected route access, role enforcement
- Write tests for momstilsvar calculation on submit
- Write tests for filing period uniqueness constraint (duplicate se_nummer + period + type)
- Write tests for event handler side effects where testable
- Ensure full test isolation using the existing savepoint transaction strategy (no test leaves data in the database)

#### Not Responsible For
- Frontend tests (out of scope for this phase)
- Writing application code (defers to Coder agents)
- Documentation (defers to Docs Agent)

#### Inputs
- All new code from Backend Coder Agent
- `AGENT_ARCHITECT_SPEC.md` (for expected behaviour)
- Existing `tests/` directory (for patterns to follow)

#### Output
- `tests/test_filings.py`
- `tests/test_assessments.py`
- `tests/test_auth.py`

---

### 8. Docs Agent

**One-line summary:** Generates and updates all project documentation to reflect the completed platform.

#### Purpose
The Docs Agent produces developer-facing documentation: how to set up the project, how the architecture works, and a complete API reference. It reads the final state of all code and specs and synthesises them into readable documents.

#### Responsibilities
- Update `ARCHITECTURE.md` to reflect all new modules, the authentication system, the event bus wiring, and the updated ERD
- Generate `API_DOCS.md` with all 17+ endpoints documented: HTTP method, path, auth requirement, role restriction, request body, response body, example curl calls
- Write `SETUP.md` covering: prerequisites, local development setup, environment variables, running backend, running frontend, running tests, common issues
- Document the event flow: which service publishes each event, which handler subscribes, what the handler does

#### Not Responsible For
- Writing application code or test code
- Making architectural decisions

#### Inputs
- All final code (backend + frontend)
- `AGENT_ARCHITECT_SPEC.md`
- `AGENT_RESEARCHER_SPEC.md`
- `AGENT_REVIEWER_SPEC.md`

#### Output
- `ARCHITECTURE.md` (updated)
- `API_DOCS.md` (new)
- `SETUP.md` (new)

---

## Rules That Apply to All Agents

1. **No agent modifies another agent's output file.** Each agent owns its own output exclusively.
2. **No agent skips reading the Reviewer's findings.** All Phase 2+ agents must incorporate `AGENT_REVIEWER_SPEC.md`.
3. **Naming conventions are fixed.** All agents follow the existing Python naming conventions (snake_case), TypeScript conventions (camelCase for variables, PascalCase for components), and file naming already established in the codebase.
4. **The event bus is the only cross-module channel.** No module may call another module's service directly.
5. **The Reviewer's blocking issues must be resolved before Phase 2 starts.** The orchestrator is responsible for confirming resolution.
6. **Agents do not gold-plate.** Each agent produces only what is needed for its defined scope. No agent adds features, abstractions, or documentation beyond its responsibilities.
