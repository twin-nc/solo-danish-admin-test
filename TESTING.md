# Testing - Danish Tax Administration Platform

## Overview

The project currently has **30 automated tests** across unit, integration, and API layers.
Tests are isolated per test case and run against a dedicated PostgreSQL test database
(`vatri_test_db`) created automatically by fixtures.

Execution policy is containerized-first. Local host execution is fallback-only.

---

## Test Structure

```
tests/
|-- conftest.py
|-- unit/
|   |-- test_party_handlers.py
|   `-- test_party_service.py
|-- integration/
|   `-- test_party_repository.py
`-- api/
    |-- test_parties.py
    `-- test_roles.py
```

---

## Isolation Model

The fixture layer uses SQLAlchemy savepoints:

1. Open one outer transaction per test.
2. Use `join_transaction_mode="create_savepoint"`.
3. App-level `db.commit()` releases savepoints, not the outer transaction.
4. Roll back the outer transaction after each test.

This keeps tests fast, isolated, and realistic (full router -> service -> repository path).

---

## Containerized Commands (Primary)

Run from the project root.

```bash
# Start stack (or at minimum db + backend)
docker compose up -d --build

# Full suite in container mode (mount repo so tests are available)
docker compose run --rm -v "${PWD}:/app" backend pytest -q tests -p no:cacheprovider

# Unit only
docker compose run --rm -v "${PWD}:/app" backend pytest -q tests/unit -p no:cacheprovider

# Integration + API
docker compose run --rm -v "${PWD}:/app" backend pytest -q tests/integration tests/api -p no:cacheprovider

# Coverage gate
docker compose run --rm -v "${PWD}:/app" backend pytest --cov=app --cov-fail-under=90 -q tests -p no:cacheprovider
```

Notes:
- The `-v "${PWD}:/app"` mount is required because the production backend image excludes `tests/`.
- `-p no:cacheprovider` avoids `.pytest_cache` permission issues when running as non-root in container mode.

---

## Local Fallback Commands

Use only when container execution is unavailable.

```bash
# Windows
venv\Scripts\activate

# Run all tests
pytest -q

# Coverage gate
pytest --cov=app --cov-fail-under=90 -q
```

---

## Current Baseline

- `pytest -q` -> 30 passed
- Containerized suite (mounted workspace) -> 30 passed
- Coverage is near-threshold (~89.85%) and should be treated as an active risk until raised above 90.00.

---

## Required Evidence for Agent Handoffs

Each coder/testing handoff must include:

1. Changed test files.
2. Exact commands executed.
3. Execution mode (`docker compose ...` preferred; local fallback reason if used).
4. Failing output and severity classification (if any).
