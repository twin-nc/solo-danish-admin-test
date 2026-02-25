import uuid
from datetime import datetime, timezone

from app.main import app as fastapi_app
from app.routers.auth import get_auth_service


class FakeAuthService:
    async def login(self, email, password, db):
        return ("fake-access-token", "fake-refresh-token")

    async def refresh(self, refresh_token, db):
        return "new-access-token"


def test_login_sets_auth_cookies(client):
    fastapi_app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()
    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "auth@example.com", "password": "password"},
        )
    finally:
        fastapi_app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-access-token"
    assert client.cookies.get("access_token")
    assert client.cookies.get("refresh_token")


def test_refresh_requires_cookie(client):
    fastapi_app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()
    try:
        response = client.post("/api/v1/auth/refresh")
    finally:
        fastapi_app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_refresh_sets_new_access_cookie(client):
    fastapi_app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()
    client.cookies.set("refresh_token", "seed-refresh-token")
    try:
        response = client.post("/api/v1/auth/refresh")
    finally:
        fastapi_app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-token"
    assert client.cookies.get("access_token") == "new-access-token"


def test_logout_clears_auth_cookies(client):
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}
    set_cookie = ",".join(response.headers.get_list("set-cookie"))
    assert "access_token=" in set_cookie
    assert "refresh_token=" in set_cookie


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_me_returns_user(authenticated_client):
    response = authenticated_client.get("/api/v1/auth/me")
    data = response.json()

    assert response.status_code == 200
    assert data["role"] == "ADMIN"
    assert data["party_id"] is None
    uuid.UUID(data["id"])
    datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).astimezone(
        timezone.utc
    )
