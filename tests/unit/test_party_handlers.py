import uuid

from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.events.handlers.party_handlers import (
    on_party_registered,
    on_party_role_assigned,
)


def test_on_party_registered_does_not_raise(caplog):
    event = PartyRegistered(
        party_id=uuid.uuid4(),
        party_type_code="ORGADM1",
        tin="1234-987654321",
    )

    with caplog.at_level("INFO"):
        on_party_registered(event)

    assert "Party registered" in caplog.text


def test_on_party_role_assigned_does_not_raise(caplog):
    event = PartyRoleAssigned(
        party_id=uuid.uuid4(),
        party_role_id=uuid.uuid4(),
        party_role_type_code="BUSINSSDM1",
    )

    with caplog.at_level("INFO"):
        on_party_role_assigned(event)

    assert "Party role assigned" in caplog.text
