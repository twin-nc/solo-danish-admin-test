"""
Unit tests for PartyService.

Scope: business rules, event publishing, and repository delegation.
No database required — all dependencies are faked.

Testing Agent: fill in tests below following the FakeEventBus pattern.
Each test must stay within the unit-test contract:
  - Use FakeEventBus (defined in ARCHITECTURE.md) to assert event publishing.
  - Use unittest.mock.MagicMock or a hand-rolled fake for PartyRepository.
  - Never touch the database.
"""

from unittest.mock import MagicMock

from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.services.party import PartyService


class FakeEventBus:
    """Minimal in-memory event bus for unit tests (see ARCHITECTURE.md)."""

    def __init__(self):
        self.published = []

    async def publish(self, event):
        self.published.append(event)

    def subscribe(self, event_type, handler):
        pass


# ---------------------------------------------------------------------------
# Checkpoint A — schema / contract stubs
# (Replace `pass` with real assertions once PartyService API is confirmed.)
# ---------------------------------------------------------------------------


def test_register_party_publishes_party_registered_event():
    """Service must publish PartyRegistered after a successful registration."""
    pass  # TODO (Testing Agent): implement with FakeEventBus + mock repo


def test_register_party_calls_repository_create():
    """Service must delegate persistence to PartyRepository.create_party."""
    pass  # TODO (Testing Agent): assert repo.create_party was called once


# ---------------------------------------------------------------------------
# Checkpoint B — endpoint behaviour stubs
# ---------------------------------------------------------------------------


def test_assign_role_publishes_party_role_assigned_event():
    """Service must publish PartyRoleAssigned after a successful role assignment."""
    pass  # TODO (Testing Agent): implement with FakeEventBus + mock repo


def test_assign_role_raises_for_unknown_party():
    """Service must raise a domain exception when the party does not exist."""
    pass  # TODO (Testing Agent): mock repo to return None, assert exception


# ---------------------------------------------------------------------------
# Checkpoint C — business-rule stubs
# ---------------------------------------------------------------------------


def test_assign_role_raises_for_cross_party_identifier():
    """Service must reject an identifier that belongs to a different party."""
    pass  # TODO (Testing Agent): supply a foreign identifier_id, assert 400-equivalent


def test_assign_role_raises_for_cross_party_contact():
    """Service must reject a contact that belongs to a different party."""
    pass  # TODO (Testing Agent): supply a foreign contact_id, assert 400-equivalent
