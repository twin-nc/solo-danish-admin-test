import uuid

from app.events.base import BaseEvent


class PartyRegistered(BaseEvent):
    party_id: uuid.UUID
    party_type_code: str
    tin: str | None = None


class PartyRoleAssigned(BaseEvent):
    party_id: uuid.UUID
    party_role_id: uuid.UUID
    party_role_type_code: str
