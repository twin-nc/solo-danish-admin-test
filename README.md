# Danish VAT Administration Platform (VATRI)

## Summary
This repository contains a Danish VAT administration platform with a FastAPI backend, a Next.js frontend, and PostgreSQL.

The system supports:
- Party registration and role assignment
- Authentication and role-based access (ADMIN, OFFICER, TAXPAYER)
- VAT filing lifecycle (draft, submit, receipt, correction)
- Tax assessments and appeals
- Admin dashboard and settings
- Audit logging and domain-event based module communication

Core business rules reflected in the docs and code include:
- `momstilsvar = A + C + E - B`
- Filing deadlines based on filing period type
- Late submissions are accepted and penalty data is recorded
- Ownership controls for TAXPAYER users

## Tech Stack
- Backend: Python, FastAPI, SQLAlchemy 2.0, Alembic
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand
- Database: PostgreSQL 16
- Testing: pytest, pytest-asyncio, httpx, pytest-cov

## Run The Project
### Docker (recommended)
```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Local backend (fallback)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Local frontend
```bash
cd frontend
npm install
npm run dev
```

## Testing
Run tests locally:
```bash
pytest -q
```

Containerized test flow is documented in `TESTING.md`.

## Relevant Documents
- `PROJECT_OVERVIEW.md`: Product context, business rules, and phased delivery plan
- `ARCHITECTURE.md`: Architectural patterns, module layering, and technical rationale
- `TESTING.md`: Test strategy, execution modes, and baseline expectations
- `AGENT_PLAN.md`: Original multi-agent execution plan
- `AGENT_ROLES.md`: Responsibilities and handoff boundaries between agents
- `AGENT_REVIEWER_SPEC.md`: Phase 1 cross-spec review findings and required actions
- `memory/MEMORY.md`: Running implementation memory and recent progress notes

## Where Things Stand At The Moment
Repository inspection on 2026-02-26 shows implementation has moved beyond the original plan documents:

- Backend now includes routers for `auth`, `parties`, `roles`, `filings`, `assessments`, `dashboard`, and `admin`.
- Backend models include `user`, `filing`, `assessment`, `vat_policy`, `admin_settings`, and `audit_log` (in addition to party models).
- Frontend is present with authenticated app routes and pages for dashboard, registrations, filings, assessments, admin settings/users, and login.
- The codebase currently contains 15 frontend page files and 22 router endpoint handlers.
- Test coverage scope has expanded significantly compared to older docs, with 100+ test functions across unit, integration, and API suites.
- Some planning docs still describe Phase 2 as pending, so status in `PROJECT_OVERVIEW.md` and `AGENT_PLAN.md` should be treated as historical planning context rather than current implementation state.

Practical status: the project appears in late Phase 2 / early Phase 3 territory (substantial backend and frontend implementation exists, with broad automated test suites already present).
