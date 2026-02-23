import logging

from fastapi import FastAPI

from app.events.bus import InMemoryEventBus
from app.events.handlers.party_handlers import (
    on_party_registered,
    on_party_role_assigned,
)
from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.repositories.party import PartyRepository
from app.routers import parties, roles
from app.routers.parties import get_party_service
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

repo = PartyRepository()
service = PartyService(repo=repo, bus=bus)


def _get_party_service() -> PartyService:
    return service


app.dependency_overrides[get_party_service] = _get_party_service

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(parties.router)
app.include_router(roles.router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
