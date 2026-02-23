# Architecture — Danish Tax Administration Platform

## Overview

This is the backend for a Danish tax administration web application. It is designed to
support multiple modules — starting with **Entity Registration**, with **Tax Filing** and
**Tax Assessment** to follow. The backend exposes a REST API built with FastAPI and stores
data in PostgreSQL.

The architecture is intentionally **pivot-friendly**: it is structured to support growth
and complexity over time without requiring a rewrite.

---

## Architectural Style

The system combines three well-known patterns:

### 1. Layered Architecture
The codebase is divided into four horizontal layers. Each layer has a single
responsibility and only communicates downward:

```
┌─────────────────────────────────────┐
│          Routers (HTTP layer)        │  Receives HTTP requests, delegates to services
├─────────────────────────────────────┤
│         Services (business logic)    │  Enforces business rules, orchestrates work
├─────────────────────────────────────┤
│       Repositories (data access)     │  All database queries live here
├─────────────────────────────────────┤
│          Models (ORM / schema)       │  SQLAlchemy table definitions
└─────────────────────────────────────┘
```

**Rule**: Routers never query the database directly. Services never construct HTTP
responses. Repositories never contain business logic.

### 2. Domain-Driven Design (DDD) — Domain Events
When a significant business action occurs (e.g., a company registers), the service
emits a **domain event** — a named, timestamped record of the fact:

- `PartyRegistered` — a business entity has been registered
- `PartyRoleAssigned` — a role has been assigned to a registered party

Other parts of the system (future modules) subscribe to these events and react
independently. The registration module does not need to know what tax filing does —
it simply announces what happened.

### 3. Hexagonal Architecture (Ports and Adapters)
The `EventBus` is defined as an **abstract interface (ABC)**. The current implementation
is an `InMemoryEventBus` (runs in-process, no infrastructure required). When the system
needs to scale or decouple across services, a `RabbitMQEventBus` or `KafkaEventBus` can
be dropped in by changing a single line in `main.py`. No business logic changes.

```
          ┌──────────────────────────────────┐
          │         Business Logic            │
          │  (Services, Repositories, Events) │
          └──────────────┬───────────────────┘
                         │ talks to interfaces (ports)
          ┌──────────────▼───────────────────┐
          │           Adapters                │
          │  InMemoryEventBus / PostgreSQL /  │
          │  RabbitMQ (future) / HTTP         │
          └──────────────────────────────────┘
```

---

## Module Structure

```
app/
├── main.py              # App entry point, dependency wiring
├── config.py            # Environment-based configuration (pydantic-settings)
├── db/
│   └── session.py       # SQLAlchemy engine, session factory, FastAPI dependency
├── models/              # SQLAlchemy ORM table definitions
├── schemas/             # Pydantic models for API request/response validation
├── repositories/        # All database access (queries, inserts, updates)
├── services/            # Business logic (orchestrates repos + publishes events)
├── events/              # Event definitions, bus interface, bus implementation, handlers
└── routers/             # FastAPI route handlers (thin HTTP layer)
```

---

## Registration Module

The first module implements **entity registration** based on the Party / PartyRole
data model.

### Data Model

A registration consists of two steps:

**Step 1 — Party creation** (`POST /api/v1/parties`)

A `Party` represents a legal entity (organisation). It has:
- **Identifiers** — e.g. TIN (Tax Identification Number)
- **Classifications** — business size (SMALL / MEDIUM / LARGE) and economic sector
- **States** — current status, e.g. IN_BUSINESS
- **Contacts** — email address
- **Names** — legal/alias name

**Step 2 — Role assignment** (`POST /api/v1/parties/{id}/roles`)

A `PartyRole` assigns a business role (`BUSINSSDM1`) to a registered party and links
which of the party's identifiers and contacts are eligible for that role.

### Key Code Values

| Field | Valid Values |
|-------|-------------|
| `identifierTypeCL` | `TIN` |
| `partyClassificationTypeCL` | `BUSINESS_SIZE`, `ECONOMIC_ACTIVITIES` |
| `partyStateCL` | `IN_BUSINESS` |
| `partyTypeCode` | `ORGADM1` (Organisation) |
| `partyRoleTypeCode` | `BUSINSSDM1` (Business) |
| Business sizes | `SMALL`, `MEDIUM`, `LARGE` |
| Sectors | `PIZZERIA`, `CAFE`, `FINE_DINE_MEAT`, `FINE_DINE_VEGETARIAN`, `CLEANING_SERVICES`, `DISTRIBUTORS`, `MEAT_PROCESSORS`, `FOOD_PROCESSORS`, `LIVESTOCK_FARMERS`, `CROP_FARMERS`, `IMPORTER`, `CUSTOMER` |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/parties` | Register a new party |
| GET | `/api/v1/parties/{party_id}` | Retrieve a party |
| POST | `/api/v1/parties/{party_id}/roles` | Assign a role to a party |
| GET | `/api/v1/parties/{party_id}/roles` | List roles for a party |

---

## Event Flow (Registration Module)

```
POST /api/v1/parties
  └─→ PartyService.register_party()
        ├─→ PartyRepository.create_party()   [writes to DB]
        └─→ EventBus.publish(PartyRegistered)
              └─→ on_party_registered()      [logs, future: triggers workflows]

POST /api/v1/parties/{id}/roles
  └─→ PartyService.assign_role()
        ├─→ PartyRepository.create_role()    [writes to DB]
        └─→ EventBus.publish(PartyRoleAssigned)
              └─→ on_party_role_assigned()   [logs, future: triggers downstream modules]
```

---

## Technology Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python | Consistent with existing scripts; strong ecosystem for data/tax |
| Web framework | FastAPI | Async, auto-generated OpenAPI docs, Pydantic-native |
| Database | PostgreSQL | Relational, reliable, excellent UUID support |
| ORM | SQLAlchemy 2.0 | Modern typed API; standard in Python ecosystem |
| Migrations | Alembic | The standard migration tool for SQLAlchemy projects |
| Event bus | InMemoryEventBus (initial) | No infrastructure needed to start; swappable via ABC |
| Future event bus | RabbitMQ or Kafka | To be decided based on scale and team preference |

---

## Future Modules

The following modules are planned and will follow the same layered, event-driven pattern:

- **Tax Filing** — business entities submit VAT returns; subscribes to `PartyRegistered`
- **Tax Assessment** — evaluates submissions; subscribes to filing events

Each module will have its own `services/`, `repositories/`, `routers/`, and events.
Cross-module communication happens exclusively through the event bus — modules never
call each other's services directly.

---

## Testing Strategy

### Philosophy: The Testing Pyramid

```
        ▲
       / \
      / E2E\        ← Few: full HTTP requests against a running app
     /──────\
    /  Integ- \     ← Some: repositories against a real test database
   /  ration   \
  /─────────────\
 /  Unit Tests   \  ← Many: services and handlers with mocks
/─────────────────\
```

More unit tests, fewer end-to-end tests. Each layer is tested in isolation where
possible, which keeps tests fast and failures easy to diagnose.

---

### Test Types

#### 1. Unit Tests — Services and Event Handlers
Test business logic in complete isolation. Dependencies (repositories, event bus)
are replaced with fakes or mocks.

**Key technique — `FakeEventBus`:**
Because the `EventBus` is an interface (ABC), unit tests use a simple fake
implementation that records published events instead of dispatching them:

```python
class FakeEventBus(EventBus):
    def __init__(self):
        self.published = []

    async def publish(self, event):
        self.published.append(event)

    def subscribe(self, event_type, handler):
        pass
```

This lets you assert that a service published the right event without any
infrastructure:

```python
def test_register_party_publishes_event():
    bus = FakeEventBus()
    repo = FakePartyRepository()
    service = PartyService(repo=repo, bus=bus)

    service.register_party(payload=..., db=...)

    assert len(bus.published) == 1
    assert isinstance(bus.published[0], PartyRegistered)
    assert bus.published[0].tin == "1676-123456789"
```

**What is tested here:**
- Business rules (e.g. cross-party ownership validation on role assignment)
- That the correct event type is published after each operation
- That repositories are called with the right arguments

---

#### 2. Integration Tests — Repositories
Test that database queries work correctly against a real PostgreSQL test database.
The test database is created once per test session and wiped between tests.

```python
def test_create_party_persists_identifiers(db_session):
    repo = PartyRepository()
    party = repo.create_party(payload=valid_party_payload, db=db_session)

    assert party.id is not None
    assert len(party.identifiers) == 1
    assert party.identifiers[0].identifier_type_cl == "TIN"
```

**What is tested here:**
- SQLAlchemy models map correctly to the database schema
- Cascade deletes work (deleting a party removes all children)
- `selectinload` returns nested data correctly
- Alembic migrations produce the expected schema

---

#### 3. API Tests — Routers (End-to-End)
Test the full HTTP stack using FastAPI's built-in `TestClient` (powered by `httpx`).
The database is a test database; the event bus is the real `InMemoryEventBus`.

```python
def test_post_party_returns_201(client):
    response = client.post("/api/v1/parties", json=valid_party_payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["identifiers"][0]["identifierValue"] == "1676-123456789"

def test_assign_role_with_foreign_identifier_returns_400(client, existing_party):
    foreign_identifier_id = str(uuid.uuid4())  # belongs to a different party
    response = client.post(f"/api/v1/parties/{existing_party.id}/roles", json={
        "party_role_type_code": "BUSINSSDM1",
        "eligible_identifiers": [{"party_identifier_id": foreign_identifier_id, "primary": True}]
    })

    assert response.status_code == 400
```

**What is tested here:**
- HTTP status codes are correct
- Response shapes match the Pydantic schemas
- Error cases return the right status and message
- The full request → router → service → repository → response path works

---

### Test Layout

```
tests/
├── conftest.py                  # shared fixtures: test DB, TestClient, FakeEventBus
├── unit/
│   ├── test_party_service.py    # PartyService with mocked repo + FakeEventBus
│   └── test_party_handlers.py  # event handler logic in isolation
├── integration/
│   └── test_party_repository.py # repository queries against test PostgreSQL
└── api/
    ├── test_parties.py          # POST /parties, GET /parties/{id}
    └── test_roles.py            # POST/GET /parties/{id}/roles
```

---

### Test Dependencies

Added to `requirements.txt` (or a separate `requirements-dev.txt`):

```
pytest==8.2.0
pytest-asyncio==0.23.6
httpx==0.27.0
pytest-mock==3.14.0
```

- `pytest` — test runner
- `pytest-asyncio` — support for `async def` test functions
- `httpx` — powers FastAPI's `TestClient`
- `pytest-mock` — convenience wrapper around `unittest.mock`

---

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests (fast, no database needed)
pytest tests/unit/

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run a single file
pytest tests/api/test_parties.py -v
```

---

### Prerequisites
- Python 3.11+
- PostgreSQL running locally (or via Docker)

### Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env: set DATABASE_URL=postgresql://user:pass@localhost:5432/vatri_db

# 4. Create the database
psql -U postgres -c "CREATE DATABASE vatri_db;"

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
