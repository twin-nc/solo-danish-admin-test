import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.events.base import EventBus
from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.models.party import Party
from app.models.party_role import PartyRole
from app.repositories.party import PartyRepository
from app.schemas.party import PartyCreate
from app.schemas.party_role import PartyRoleCreate


class PartyService:
    def __init__(self, repo: PartyRepository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    async def register_party(self, payload: PartyCreate, db: Session) -> Party:
        party = self._repo.create_party(payload, db)

        tin = next(
            (i.identifier_value for i in party.identifiers if i.identifier_type_cl == "TIN"),
            None,
        )
        await self._bus.publish(
            PartyRegistered(
                party_id=party.id,
                party_type_code=party.party_type_code,
                tin=tin,
            )
        )
        return party

    async def get_party(self, party_id: uuid.UUID, db: Session) -> Party:
        party = self._repo.get_party_by_id(party_id, db)
        if party is None:
            raise HTTPException(status_code=404, detail="Party not found")
        return party

    async def assign_role(
        self, party_id: uuid.UUID, payload: PartyRoleCreate, db: Session
    ) -> PartyRole:
        # Ensure party exists
        party = self._repo.get_party_by_id(party_id, db)
        if party is None:
            raise HTTPException(status_code=404, detail="Party not found")

        # Validate that all eligible identifiers belong to this party
        for ei in payload.eligible_identifiers:
            record = self._repo.get_identifier(ei.party_identifier_id, party_id, db)
            if record is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Identifier {ei.party_identifier_id} does not belong to party {party_id}"
                    ),
                )

        # Validate that all eligible contacts belong to this party
        for ec in payload.eligible_contacts:
            record = self._repo.get_contact(ec.party_contact_id, party_id, db)
            if record is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Contact {ec.party_contact_id} does not belong to party {party_id}"
                    ),
                )

        role = self._repo.create_role(party_id, payload, db)

        await self._bus.publish(
            PartyRoleAssigned(
                party_id=party_id,
                party_role_id=role.id,
                party_role_type_code=role.party_role_type_code,
            )
        )
        return role

    async def list_roles(self, party_id: uuid.UUID, db: Session) -> list[PartyRole]:
        party = self._repo.get_party_by_id(party_id, db)
        if party is None:
            raise HTTPException(status_code=404, detail="Party not found")
        return self._repo.list_roles(party_id, db)
