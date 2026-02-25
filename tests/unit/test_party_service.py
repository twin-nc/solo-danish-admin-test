import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.schemas.party import PartyCreate
from app.schemas.party_role import PartyRoleCreate
from app.services.party import PartyService


class FakeEventBus:
    def __init__(self):
        self.published = []

    async def publish(self, event):
        self.published.append(event)

    def subscribe(self, event_type, handler):
        pass


PARTY_PAYLOAD = {
    "partyTypeCode": "ORGADM1",
    "identifiers": [{"identifierTypeCL": "TIN", "identifierValue": "1234-987654321"}],
    "classifications": [
        {"partyClassificationTypeCL": "BUSINESS_SIZE", "classificationValue": "MEDIUM"},
    ],
    "states": [{"partyStateCL": "IN_BUSINESS"}],
    "contacts": [{"contactValue": "unit-test@virksomhed.dk"}],
    "names": [{"name": "Unit Test ApS", "isAlias": False}],
}


def _build_party(identifier_value: str = "1234-987654321"):
    return SimpleNamespace(
        id=uuid.uuid4(),
        party_type_code="ORGADM1",
        identifiers=[
            SimpleNamespace(identifier_type_cl="TIN", identifier_value=identifier_value)
        ],
    )


def _build_role():
    return SimpleNamespace(id=uuid.uuid4(), party_role_type_code="BUSINSSDM1")


def _build_role_payload(
    identifier_id: uuid.UUID, contact_id: uuid.UUID
) -> PartyRoleCreate:
    return PartyRoleCreate(
        party_role_type_code="BUSINSSDM1",
        states=[{"partyRoleStateCL": "ACTIVE"}],
        eligible_identifiers=[{"party_identifier_id": identifier_id, "primary": True}],
        eligible_contacts=[{"party_contact_id": contact_id, "primary": True}],
    )


@pytest.mark.asyncio
async def test_register_party_publishes_party_registered_event():
    repo = MagicMock()
    party = _build_party()
    repo.create_party.return_value = party
    bus = FakeEventBus()
    service = PartyService(repo=repo, bus=bus)
    payload = PartyCreate(**PARTY_PAYLOAD)
    db = MagicMock()

    result = await service.register_party(payload=payload, db=db)

    assert result is party
    assert len(bus.published) == 1
    published = bus.published[0]
    assert isinstance(published, PartyRegistered)
    assert published.party_id == party.id
    assert published.party_type_code == "ORGADM1"
    assert published.tin == "1234-987654321"


@pytest.mark.asyncio
async def test_register_party_calls_repository_create():
    repo = MagicMock()
    repo.create_party.return_value = _build_party()
    bus = FakeEventBus()
    service = PartyService(repo=repo, bus=bus)
    payload = PartyCreate(**PARTY_PAYLOAD)
    db = MagicMock()

    await service.register_party(payload=payload, db=db)

    repo.create_party.assert_called_once_with(payload, db)


@pytest.mark.asyncio
async def test_assign_role_publishes_party_role_assigned_event():
    repo = MagicMock()
    party_id = uuid.uuid4()
    identifier_id = uuid.uuid4()
    contact_id = uuid.uuid4()
    payload = _build_role_payload(identifier_id=identifier_id, contact_id=contact_id)
    role = _build_role()

    repo.get_party_by_id.return_value = _build_party()
    repo.get_identifier.return_value = object()
    repo.get_contact.return_value = object()
    repo.create_role.return_value = role

    bus = FakeEventBus()
    service = PartyService(repo=repo, bus=bus)
    db = MagicMock()

    result = await service.assign_role(party_id=party_id, payload=payload, db=db)

    assert result is role
    repo.create_role.assert_called_once_with(party_id, payload, db)
    assert len(bus.published) == 1
    published = bus.published[0]
    assert isinstance(published, PartyRoleAssigned)
    assert published.party_id == party_id
    assert published.party_role_id == role.id
    assert published.party_role_type_code == "BUSINSSDM1"


@pytest.mark.asyncio
async def test_assign_role_raises_for_unknown_party():
    repo = MagicMock()
    repo.get_party_by_id.return_value = None
    bus = FakeEventBus()
    service = PartyService(repo=repo, bus=bus)

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(
            party_id=uuid.uuid4(),
            payload=PartyRoleCreate(
                party_role_type_code="BUSINSSDM1",
                states=[],
                eligible_identifiers=[],
                eligible_contacts=[],
            ),
            db=MagicMock(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Party not found"


@pytest.mark.asyncio
async def test_assign_role_raises_for_cross_party_identifier():
    repo = MagicMock()
    party_id = uuid.uuid4()
    payload = _build_role_payload(identifier_id=uuid.uuid4(), contact_id=uuid.uuid4())

    repo.get_party_by_id.return_value = _build_party()
    repo.get_identifier.return_value = None

    bus = FakeEventBus()
    service = PartyService(repo=repo, bus=bus)

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(party_id=party_id, payload=payload, db=MagicMock())

    assert exc.value.status_code == 400
    assert "does not belong to party" in exc.value.detail
    repo.create_role.assert_not_called()


@pytest.mark.asyncio
async def test_assign_role_raises_for_cross_party_contact():
    repo = MagicMock()
    party_id = uuid.uuid4()
    payload = _build_role_payload(identifier_id=uuid.uuid4(), contact_id=uuid.uuid4())

    repo.get_party_by_id.return_value = _build_party()
    repo.get_identifier.return_value = object()
    repo.get_contact.return_value = None

    bus = FakeEventBus()
    service = PartyService(repo=repo, bus=bus)

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(party_id=party_id, payload=payload, db=MagicMock())

    assert exc.value.status_code == 400
    assert "does not belong to party" in exc.value.detail
    repo.create_role.assert_not_called()
