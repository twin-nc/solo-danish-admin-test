import uuid

import pytest

PARTY_PAYLOAD = {
    "partyTypeCode": "ORGADM1",
    "identifiers": [{"identifierTypeCL": "TIN", "identifierValue": "1234-987654321"}],
    "classifications": [
        {"partyClassificationTypeCL": "BUSINESS_SIZE", "classificationValue": "SMALL"},
    ],
    "states": [{"partyStateCL": "IN_BUSINESS"}],
    "contacts": [{"contactValue": "test@virksomhed.dk"}],
    "names": [{"name": "Test ApS", "isAlias": False}],
}


@pytest.fixture
def registered_party(client):
    """Register a party and return its response data."""
    response = client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    assert response.status_code == 201
    return response.json()


def _role_payload(registered_party, **overrides):
    payload = {
        "party_role_type_code": "BUSINSSDM1",
        "states": [{"partyRoleStateCL": "ACTIVE"}],
        "eligible_identifiers": [
            {
                "party_identifier_id": registered_party["identifiers"][0]["id"],
                "primary": True,
            }
        ],
        "eligible_contacts": [
            {
                "party_contact_id": registered_party["contacts"][0]["id"],
                "primary": True,
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_assign_role_returns_201(client, registered_party):
    response = client.post(
        f"/api/v1/parties/{registered_party['id']}/roles",
        json=_role_payload(registered_party),
    )
    assert response.status_code == 201


def test_assign_role_response_shape(client, registered_party):
    response = client.post(
        f"/api/v1/parties/{registered_party['id']}/roles",
        json=_role_payload(registered_party),
    )
    data = response.json()

    assert data["party_id"] == registered_party["id"]
    assert data["party_role_type_code"] == "BUSINSSDM1"
    assert len(data["states"]) == 1
    assert data["states"][0]["partyRoleStateCL"] == "ACTIVE"
    assert len(data["eligible_identifiers"]) == 1
    assert data["eligible_identifiers"][0]["primary"] is True
    assert len(data["eligible_contacts"]) == 1
    assert data["eligible_contacts"][0]["primary"] is True


def test_list_roles(client, registered_party):
    party_id = registered_party["id"]
    client.post(f"/api/v1/parties/{party_id}/roles", json=_role_payload(registered_party))

    response = client.get(f"/api/v1/parties/{party_id}/roles")
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert len(roles) == 1
    assert roles[0]["party_role_type_code"] == "BUSINSSDM1"


def test_list_roles_empty(client, registered_party):
    response = client.get(f"/api/v1/parties/{registered_party['id']}/roles")
    assert response.status_code == 200
    assert response.json() == []


def test_list_roles_party_not_found(client):
    response = client.get(f"/api/v1/parties/{uuid.uuid4()}/roles")
    assert response.status_code == 404
    assert response.json()["detail"] == "Party not found"


def test_assign_role_party_not_found(client):
    payload = {
        "party_role_type_code": "BUSINSSDM1",
        "states": [{"partyRoleStateCL": "ACTIVE"}],
        "eligible_identifiers": [],
        "eligible_contacts": [],
    }
    response = client.post(f"/api/v1/parties/{uuid.uuid4()}/roles", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Party not found"


def test_assign_role_invalid_identifier(client, registered_party):
    payload = _role_payload(
        registered_party,
        eligible_identifiers=[{"party_identifier_id": str(uuid.uuid4()), "primary": True}],
    )
    response = client.post(
        f"/api/v1/parties/{registered_party['id']}/roles", json=payload
    )
    assert response.status_code == 400


def test_assign_role_invalid_contact(client, registered_party):
    payload = _role_payload(
        registered_party,
        eligible_contacts=[{"party_contact_id": str(uuid.uuid4()), "primary": True}],
    )
    response = client.post(
        f"/api/v1/parties/{registered_party['id']}/roles", json=payload
    )
    assert response.status_code == 400
