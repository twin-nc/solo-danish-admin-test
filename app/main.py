import logging

from fastapi import FastAPI

from app.events.auth_events import UserAuthenticated
from app.events.bus import InMemoryEventBus
from app.events.handlers.auth_handlers import on_user_authenticated
from app.events.handlers.party_handlers import (
    on_party_registered,
    on_party_role_assigned,
)
from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.repositories.party import PartyRepository
from app.repositories.user import UserRepository
from app.routers import parties, roles
from app.routers.auth import get_auth_service
from app.routers.auth import router as auth_router
from app.routers.parties import get_party_service
from app.services.auth import AuthService
from app.services.party import PartyService

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Danish Tax Administration — Registration API",
    version="1.0.0",
    description="Entity registration module for the Danish tax administration platform.",
)

# ── Dependency wiring ─────────────────────────────────────────────────────────

bus = InMemoryEventBus()
bus.subscribe(PartyRegistered, on_party_registered)
bus.subscribe(PartyRoleAssigned, on_party_role_assigned)
bus.subscribe(UserAuthenticated, on_user_authenticated)

repo = PartyRepository()
service = PartyService(repo=repo, bus=bus)

user_repo = UserRepository()
auth_service = AuthService(repo=user_repo, bus=bus)


def _get_party_service() -> PartyService:
    return service


def _get_auth_service() -> AuthService:
    return auth_service


app.dependency_overrides[get_party_service] = _get_party_service
app.dependency_overrides[get_auth_service] = _get_auth_service

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(parties.router)
app.include_router(roles.router)
app.include_router(auth_router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
