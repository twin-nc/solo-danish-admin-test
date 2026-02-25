import uuid

from app.models.party import PartyIdentifier
from app.repositories.party import PartyRepository
from app.schemas.party import PartyCreate

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


def _payload_with(identifier_value: str, email: str, name: str) -> PartyCreate:
    payload = {
        **PARTY_PAYLOAD,
        "identifiers": [
            {"identifierTypeCL": "TIN", "identifierValue": identifier_value}
        ],
        "contacts": [{"contactValue": email}],
        "names": [{"name": name, "isAlias": False}],
    }
    return PartyCreate(**payload)


def test_create_party_persists_to_database(db):
    repo = PartyRepository()
    payload = PartyCreate(**PARTY_PAYLOAD)

    party = repo.create_party(payload=payload, db=db)
    fetched = repo.get_party_by_id(party.id, db)

    assert party.id is not None
    assert fetched is not None
    assert fetched.id == party.id
    assert fetched.party_type_code == "ORGADM1"


def test_create_party_persists_child_rows(db):
    repo = PartyRepository()
    payload = PartyCreate(**PARTY_PAYLOAD)

    party = repo.create_party(payload=payload, db=db)

    assert len(party.identifiers) == 1
    assert party.identifiers[0].identifier_type_cl == "TIN"
    assert party.identifiers[0].identifier_value == "9999-111111111"
    assert len(party.classifications) == 1
    assert party.classifications[0].party_classification_type_cl == "BUSINESS_SIZE"
    assert len(party.states) == 1
    assert party.states[0].party_state_cl == "IN_BUSINESS"
    assert len(party.contacts) == 1
    assert party.contacts[0].contact_value == "repo-test@virksomhed.dk"
    assert len(party.names) == 1
    assert party.names[0].name == "Repo Test ApS"


def test_get_party_by_id_returns_correct_record(db):
    repo = PartyRepository()
    payload = PartyCreate(**PARTY_PAYLOAD)
    created = repo.create_party(payload=payload, db=db)

    fetched = repo.get_party_by_id(created.id, db)

    assert fetched is not None
    assert fetched.id == created.id


def test_get_party_by_id_returns_none_for_unknown(db):
    repo = PartyRepository()

    fetched = repo.get_party_by_id(uuid.uuid4(), db)

    assert fetched is None


def test_create_party_identifier_uniqueness(db):
    repo = PartyRepository()
    shared_identifier = "7777-123456789"
    first = repo.create_party(
        payload=_payload_with(
            identifier_value=shared_identifier,
            email="first@virksomhed.dk",
            name="First Company ApS",
        ),
        db=db,
    )
    second = repo.create_party(
        payload=_payload_with(
            identifier_value=shared_identifier,
            email="second@virksomhed.dk",
            name="Second Company ApS",
        ),
        db=db,
    )

    identifier_rows = (
        db.query(PartyIdentifier)
        .filter(PartyIdentifier.identifier_value == shared_identifier)
        .all()
    )

    assert first.id != second.id
    assert len(identifier_rows) == 2
