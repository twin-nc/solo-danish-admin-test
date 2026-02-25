import uuid
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.events.auth_events import UserAuthenticated
from app.services.auth import AuthService


class FakeEventBus:
    def __init__(self):
        self.published = []

    async def publish(self, event):
        self.published.append(event)

    def subscribe(self, event_type, handler):
        pass


def _build_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        email="auth-user@example.com",
        hashed_password="hashed-password",
        role="ADMIN",
        party_id=None,
    )


@pytest.mark.asyncio
async def test_login_returns_access_and_refresh_tokens():
    repo = MagicMock()
    user = _build_user()
    repo.get_by_email.return_value = user
    bus = FakeEventBus()
    service = AuthService(repo=repo, bus=bus)
    service._verify_password = lambda plain, hashed: True  # noqa: SLF001

    access_token, refresh_token = await service.login(
        email=user.email,
        password="valid-password",
        db=MagicMock(),
    )

    access_payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    refresh_payload = jwt.decode(
        refresh_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert access_payload["sub"] == str(user.id)
    assert access_payload["token_type"] == "access"
    assert refresh_payload["token_type"] == "refresh"
    assert len(bus.published) == 1
    assert isinstance(bus.published[0], UserAuthenticated)


@pytest.mark.asyncio
async def test_login_raises_401_when_user_missing():
    repo = MagicMock()
    repo.get_by_email.return_value = None
    service = AuthService(repo=repo, bus=FakeEventBus())

    with pytest.raises(HTTPException) as exc:
        await service.login("missing@example.com", "password", MagicMock())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_raises_401_when_password_invalid():
    repo = MagicMock()
    user = _build_user()
    repo.get_by_email.return_value = user
    service = AuthService(repo=repo, bus=FakeEventBus())
    service._verify_password = lambda plain, hashed: False  # noqa: SLF001

    with pytest.raises(HTTPException) as exc:
        await service.login(user.email, "wrong", MagicMock())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token():
    repo = MagicMock()
    user = _build_user()
    repo.get_by_id.return_value = user
    service = AuthService(repo=repo, bus=FakeEventBus())
    refresh_token = service._create_token(  # noqa: SLF001
        sub=str(user.id),
        role=user.role,
        token_type="refresh",
        expire_delta=timedelta(days=1),
    )

    new_access_token = await service.refresh(refresh_token, MagicMock())
    payload = jwt.decode(
        new_access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == str(user.id)
    assert payload["token_type"] == "access"


@pytest.mark.asyncio
async def test_refresh_raises_401_on_invalid_token():
    service = AuthService(repo=MagicMock(), bus=FakeEventBus())

    with pytest.raises(HTTPException) as exc:
        await service.refresh("not-a-jwt", MagicMock())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_refresh_raises_401_when_user_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    user = _build_user()
    service = AuthService(repo=repo, bus=FakeEventBus())
    refresh_token = service._create_token(  # noqa: SLF001
        sub=str(user.id),
        role=user.role,
        token_type="refresh",
        expire_delta=timedelta(days=1),
    )

    with pytest.raises(HTTPException) as exc:
        await service.refresh(refresh_token, MagicMock())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_refresh_raises_401_when_token_type_is_not_refresh():
    repo = MagicMock()
    user = _build_user()
    service = AuthService(repo=repo, bus=FakeEventBus())
    access_token = service._create_token(  # noqa: SLF001
        sub=str(user.id),
        role=user.role,
        token_type="access",
        expire_delta=timedelta(minutes=5),
    )

    with pytest.raises(HTTPException) as exc:
        await service.refresh(access_token, MagicMock())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_create_user_hashes_password_and_calls_repository():
    repo = MagicMock()
    repo.create_user.return_value = _build_user()
    service = AuthService(repo=repo, bus=FakeEventBus())
    service._hash_password = lambda password: "hashed-value"  # noqa: SLF001

    await service.create_user(
        email="create-user@example.com",
        password="plain-text",
        role="OFFICER",
        party_id=None,
        db=MagicMock(),
    )

    repo.create_user.assert_called_once()
    kwargs = repo.create_user.call_args.kwargs
    assert kwargs["hashed_password"] == "hashed-value"
    assert kwargs["role"] == "OFFICER"
