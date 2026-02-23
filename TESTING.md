# Testing — Danish Tax Administration Platform

## Overview

The project has **14 automated integration tests** covering all five API endpoints.
Tests run against a dedicated PostgreSQL test database (`vatri_test_db`) that is
created automatically on first run. Each test is fully isolated — all changes are
rolled back after each test, so tests never interfere with each other and leave no
data behind.

---

## Test Structure

```
tests/
├── conftest.py       # Shared fixtures: test database, session, TestClient
├── test_parties.py   # 7 tests — party registration and retrieval
└── test_roles.py     # 7 tests — role assignment and listing
```

---

## How Test Isolation Works

The repository layer calls `db.commit()` directly when saving data. To keep tests
isolated without truncating tables between every test, the fixture layer uses
SQLAlchemy's **savepoint mode**:

1. Before each test, a real database connection is opened and an outer transaction
   is started.
2. The `Session` is created with `join_transaction_mode="create_savepoint"`. This
   means that when the app code calls `db.commit()`, it only releases a savepoint —
   the outer transaction remains uncommitted.
3. After each test, the outer transaction is rolled back, undoing every write made
   during that test.
4. FastAPI's `get_db` dependency is overridden to return this test session, so the
   full request → router → service → repository path runs against the test database.

This means tests are:
- **Fast** — no table truncation or recreation between tests
- **Isolated** — each test starts with a clean slate
- **Realistic** — the full application stack runs, including real SQL queries

---

## Test Database Setup

The `test_engine` fixture (session-scoped) handles setup automatically:

- Connects to the `postgres` admin database and creates `vatri_test_db` if it does
  not exist.
- Calls `Base.metadata.create_all()` to build all 10 tables from the ORM models
  (bypassing Alembic for speed).
- At the end of the test session, drops all tables to leave the database clean.

No manual setup is required — just run `pytest`.

---

## Test Cases

### `tests/test_parties.py`

| Test | What it verifies |
|------|-----------------|
| `test_health` | `GET /health` returns `200` with `{"status": "ok"}` |
| `test_register_party_returns_201` | `POST /api/v1/parties` returns `201 Created` |
| `test_register_party_response_shape` | Response contains all expected fields with correct values |
| `test_register_party_assigns_uuid` | The returned `id` is a valid UUID |
| `test_get_party` | `GET /api/v1/parties/{id}` returns `200` for an existing party |
| `test_get_party_returns_same_data` | Fetched record matches the data that was registered |
| `test_get_party_not_found` | `GET /api/v1/parties/{unknown-id}` returns `404` with correct message |

### `tests/test_roles.py`

| Test | What it verifies |
|------|-----------------|
| `test_assign_role_returns_201` | `POST /api/v1/parties/{id}/roles` returns `201 Created` |
| `test_assign_role_response_shape` | Response contains party ID, role type, state, linked identifier, and linked contact |
| `test_list_roles` | `GET /api/v1/parties/{id}/roles` returns the assigned role after assignment |
| `test_list_roles_empty` | `GET /api/v1/parties/{id}/roles` returns an empty list before any roles are assigned |
| `test_assign_role_party_not_found` | Assigning a role to an unknown party returns `404` |
| `test_assign_role_invalid_identifier` | Supplying an identifier from a different party returns `400` |
| `test_assign_role_invalid_contact` | Supplying a contact from a different party returns `400` |

---

## Running Tests

**Prerequisites**

- Python virtual environment activated
- PostgreSQL running on `localhost:5432`
- `.env` file present with a valid `DATABASE_URL` (used only to resolve the
  database host/credentials — tests use `vatri_test_db`, not `vatri_db`)

**Commands**

```bash
# Activate the virtual environment (Windows)
venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Run only party tests
pytest tests/test_parties.py -v

# Run only role tests
pytest tests/test_roles.py -v

# Run a single test by name
pytest tests/test_parties.py::test_get_party_not_found -v
```

**Expected output**

```
tests/test_parties.py::test_health                        PASSED
tests/test_parties.py::test_register_party_returns_201    PASSED
tests/test_parties.py::test_register_party_response_shape PASSED
tests/test_parties.py::test_register_party_assigns_uuid   PASSED
tests/test_parties.py::test_get_party                     PASSED
tests/test_parties.py::test_get_party_returns_same_data   PASSED
tests/test_parties.py::test_get_party_not_found           PASSED
tests/test_roles.py::test_assign_role_returns_201         PASSED
tests/test_roles.py::test_assign_role_response_shape      PASSED
tests/test_roles.py::test_list_roles                      PASSED
tests/test_roles.py::test_list_roles_empty                PASSED
tests/test_roles.py::test_assign_role_party_not_found     PASSED
tests/test_roles.py::test_assign_role_invalid_identifier  PASSED
tests/test_roles.py::test_assign_role_invalid_contact     PASSED

14 passed in ~0.6s
```

---

## Test Dependencies

All test dependencies are included in `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 8.3.5 | Test runner |
| `pytest-asyncio` | 0.25.3 | Support for async test fixtures |
| `httpx` | 0.28.1 | Powers FastAPI's `TestClient` |
| `pytest-mock` | 3.14.0 | Mock utilities |
