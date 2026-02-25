"""
Integration tests for PartyRepository.

Scope: ORM ↔ schema correctness, cascade behaviour, and constraint enforcement.
Requires a real PostgreSQL test database (provided by the `db` fixture in conftest.py).

Testing Agent: fill in tests below using the `db` session fixture.
Each test is wrapped in a savepoint transaction — all writes are rolled back
automatically after the test completes.
"""

from app.repositories.party import PartyRepository

PARTY_PAYLOAD = {
    "partyTypeCode": "ORGADM1",
    "identifiers": [{"identifierTypeCL": "TIN", "identifierValue": "9999-111111111"}],
    "classifications": [
        {"partyClassificationTypeCL": "BUSINESS_SIZE", "classificationValue": "SMALL"},
    ],
    "states": [{"partyStateCL": "IN_BUSINESS"}],
    "contacts": [{"contactValue": "repo-test@virksomhed.dk"}],
    "names": [{"name": "Repo Test ApS", "isAlias": False}],
}


# ---------------------------------------------------------------------------
# Checkpoint A — schema / contract stubs
# ---------------------------------------------------------------------------


def test_create_party_persists_to_database(db):
    """Repository must write a Party row and return it with a populated id."""
    pass  # TODO (Testing Agent): call repo.create_party, assert row has UUID id


def test_create_party_persists_child_rows(db):
    """Identifiers, classifications, states, contacts, and names must all be saved."""
    pass  # TODO (Testing Agent): assert len(party.identifiers) == 1, etc.


# ---------------------------------------------------------------------------
# Checkpoint B — retrieval stubs
# ---------------------------------------------------------------------------


def test_get_party_by_id_returns_correct_record(db):
    """Repository must return the exact party that was created."""
    pass  # TODO (Testing Agent): create then fetch, compare id


def test_get_party_by_id_returns_none_for_unknown(db):
    """Repository must return None (not raise) when no record exists."""
    pass  # TODO (Testing Agent): fetch with a random UUID, assert result is None


# ---------------------------------------------------------------------------
# Checkpoint C — constraint / cascade stubs
# ---------------------------------------------------------------------------


def test_create_party_identifier_uniqueness(db):
    """Two parties may share an identifier value — uniqueness is per-party."""
    pass  # TODO (Testing Agent): create two parties with same TIN value, assert both saved
