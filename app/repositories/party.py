import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.party import (
    Party,
    PartyClassification,
    PartyContact,
    PartyIdentifier,
    PartyName,
    PartyState,
)
from app.models.party_role import (
    PartyRole,
    PartyRoleEligibleContact,
    PartyRoleEligibleIdentifier,
    PartyRoleState,
)
from app.schemas.party import PartyCreate
from app.schemas.party_role import PartyRoleCreate


class PartyRepository:
    # ── Party ─────────────────────────────────────────────────────────────────

    def create_party(self, payload: PartyCreate, db: Session) -> Party:
        party = Party(party_type_code=payload.partyTypeCode)
        db.add(party)
        db.flush()  # get party.id before adding children

        for item in payload.identifiers:
            db.add(
                PartyIdentifier(
                    party_id=party.id,
                    identifier_type_cl=item.identifierTypeCL,
                    identifier_value=item.identifierValue,
                )
            )
        for item in payload.classifications:
            db.add(
                PartyClassification(
                    party_id=party.id,
                    party_classification_type_cl=item.partyClassificationTypeCL,
                    classification_value=item.classificationValue,
                )
            )
        for item in payload.states:
            db.add(
                PartyState(
                    party_id=party.id,
                    party_state_cl=item.partyStateCL,
                )
            )
        for item in payload.contacts:
            db.add(
                PartyContact(
                    party_id=party.id,
                    contact_value=item.contactValue,
                )
            )
        for item in payload.names:
            db.add(
                PartyName(
                    party_id=party.id,
                    name=item.name,
                    is_alias=item.isAlias,
                )
            )

        db.commit()
        return self.get_party_by_id(party.id, db)  # type: ignore[return-value]

    def get_party_by_id(self, party_id: uuid.UUID, db: Session) -> Party | None:
        return (
            db.query(Party)
            .options(
                selectinload(Party.identifiers),
                selectinload(Party.classifications),
                selectinload(Party.states),
                selectinload(Party.contacts),
                selectinload(Party.names),
            )
            .filter(Party.id == party_id)
            .first()
        )

    def list_parties(self, db: Session) -> list[Party]:
        return (
            db.query(Party)
            .options(
                selectinload(Party.identifiers),
                selectinload(Party.classifications),
                selectinload(Party.states),
                selectinload(Party.contacts),
                selectinload(Party.names),
            )
            .order_by(Party.created_at.desc())
            .all()
        )

    # ── Identifiers / Contacts (for ownership validation) ─────────────────────

    def get_identifier(
        self, identifier_id: uuid.UUID, party_id: uuid.UUID, db: Session
    ) -> PartyIdentifier | None:
        return (
            db.query(PartyIdentifier)
            .filter(
                PartyIdentifier.id == identifier_id,
                PartyIdentifier.party_id == party_id,
            )
            .first()
        )

    def get_contact(
        self, contact_id: uuid.UUID, party_id: uuid.UUID, db: Session
    ) -> PartyContact | None:
        return (
            db.query(PartyContact)
            .filter(
                PartyContact.id == contact_id,
                PartyContact.party_id == party_id,
            )
            .first()
        )

    # ── Roles ─────────────────────────────────────────────────────────────────

    def create_role(
        self, party_id: uuid.UUID, payload: PartyRoleCreate, db: Session
    ) -> PartyRole:
        role = PartyRole(
            party_id=party_id,
            party_role_type_code=payload.party_role_type_code,
        )
        db.add(role)
        db.flush()

        for item in payload.states:
            db.add(
                PartyRoleState(
                    party_role_id=role.id,
                    party_role_state_cl=item.partyRoleStateCL,
                )
            )
        for item in payload.eligible_identifiers:
            db.add(
                PartyRoleEligibleIdentifier(
                    party_role_id=role.id,
                    party_identifier_id=item.party_identifier_id,
                    primary=item.primary,
                )
            )
        for item in payload.eligible_contacts:
            db.add(
                PartyRoleEligibleContact(
                    party_role_id=role.id,
                    party_contact_id=item.party_contact_id,
                    primary=item.primary,
                )
            )

        db.commit()
        return self.get_role_by_id(role.id, db)  # type: ignore[return-value]

    def get_role_by_id(self, role_id: uuid.UUID, db: Session) -> PartyRole | None:
        return (
            db.query(PartyRole)
            .options(
                selectinload(PartyRole.states),
                selectinload(PartyRole.eligible_identifiers),
                selectinload(PartyRole.eligible_contacts),
            )
            .filter(PartyRole.id == role_id)
            .first()
        )

    def list_roles(self, party_id: uuid.UUID, db: Session) -> list[PartyRole]:
        return (
            db.query(PartyRole)
            .options(
                selectinload(PartyRole.states),
                selectinload(PartyRole.eligible_identifiers),
                selectinload(PartyRole.eligible_contacts),
            )
            .filter(PartyRole.party_id == party_id)
            .all()
        )
