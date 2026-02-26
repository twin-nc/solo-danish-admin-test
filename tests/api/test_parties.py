import uuid

PARTY_PAYLOAD = {
    "partyTypeCode": "ORGADM1",
    "identifiers": [{"identifierTypeCL": "TIN", "identifierValue": "1234-987654321"}],
    "classifications": [
        {"partyClassificationTypeCL": "BUSINESS_SIZE", "classificationValue": "MEDIUM"},
        {
            "partyClassificationTypeCL": "ECONOMIC_ACTIVITIES",
            "classificationValue": "CAFE",
        },
    ],
    "states": [{"partyStateCL": "IN_BUSINESS"}],
    "contacts": [{"contactValue": "test@virksomhed.dk"}],
    "names": [{"name": "Test Café ApS", "isAlias": False}],
}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_party_requires_auth(client):
    response = client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    assert response.status_code == 401


def test_list_parties_requires_auth(client):
    response = client.get("/api/v1/parties")
    assert response.status_code == 401


def test_register_party_returns_201(authenticated_client):
    response = authenticated_client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    assert response.status_code == 201


def test_list_parties_returns_records(authenticated_client):
    payload_1 = dict(PARTY_PAYLOAD)
    payload_1["identifiers"] = [
        {"identifierTypeCL": "TIN", "identifierValue": "1234-987654321"}
    ]
    payload_1["names"] = [{"name": "Party One ApS", "isAlias": False}]

    payload_2 = dict(PARTY_PAYLOAD)
    payload_2["identifiers"] = [
        {"identifierTypeCL": "TIN", "identifierValue": "1234-987654322"}
    ]
    payload_2["names"] = [{"name": "Party Two ApS", "isAlias": False}]

    create_1 = authenticated_client.post("/api/v1/parties", json=payload_1)
    create_2 = authenticated_client.post("/api/v1/parties", json=payload_2)
    assert create_1.status_code == 201
    assert create_2.status_code == 201

    response = authenticated_client.get("/api/v1/parties")
    assert response.status_code == 200
    data = response.json()
    ids = {item["id"] for item in data}
    assert create_1.json()["id"] in ids
    assert create_2.json()["id"] in ids


def test_register_party_response_shape(authenticated_client):
    response = authenticated_client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    data = response.json()

    assert "id" in data
    assert data["partyTypeCode"] == "ORGADM1"
    assert len(data["identifiers"]) == 1
    assert data["identifiers"][0]["identifierTypeCL"] == "TIN"
    assert data["identifiers"][0]["identifierValue"] == "1234-987654321"
    assert len(data["classifications"]) == 2
    assert len(data["states"]) == 1
    assert data["states"][0]["partyStateCL"] == "IN_BUSINESS"
    assert len(data["contacts"]) == 1
    assert data["contacts"][0]["contactValue"] == "test@virksomhed.dk"
    assert len(data["names"]) == 1
    assert data["names"][0]["name"] == "Test Café ApS"
    assert data["names"][0]["isAlias"] is False


def test_register_party_assigns_uuid(authenticated_client):
    response = authenticated_client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    party_id = response.json()["id"]
    # Should be a valid UUID
    uuid.UUID(party_id)


def test_get_party(authenticated_client):
    create_resp = authenticated_client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    party_id = create_resp.json()["id"]

    get_resp = authenticated_client.get(f"/api/v1/parties/{party_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == party_id


def test_get_party_returns_same_data(authenticated_client):
    create_resp = authenticated_client.post("/api/v1/parties", json=PARTY_PAYLOAD)
    created = create_resp.json()
    party_id = created["id"]

    fetched = authenticated_client.get(f"/api/v1/parties/{party_id}").json()
    assert fetched["partyTypeCode"] == created["partyTypeCode"]
    assert fetched["identifiers"][0]["identifierValue"] == "1234-987654321"
    assert fetched["names"][0]["name"] == "Test Café ApS"


def test_get_party_not_found(authenticated_client):
    response = authenticated_client.get(f"/api/v1/parties/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Party not found"
