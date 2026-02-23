import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Role Eligible Identifier ──────────────────────────────────────────────────

class EligibleIdentifierCreate(BaseModel):
    party_identifier_id: uuid.UUID
    primary: bool = False


class EligibleIdentifierRead(BaseModel):
    id: uuid.UUID
    party_identifier_id: uuid.UUID
    primary: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "EligibleIdentifierRead":
        return cls(
            id=obj.id,
            party_identifier_id=obj.party_identifier_id,
            primary=obj.primary,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Role Eligible Contact ─────────────────────────────────────────────────────

class EligibleContactCreate(BaseModel):
    party_contact_id: uuid.UUID
    primary: bool = False


class EligibleContactRead(BaseModel):
    id: uuid.UUID
    party_contact_id: uuid.UUID
    primary: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "EligibleContactRead":
        return cls(
            id=obj.id,
            party_contact_id=obj.party_contact_id,
            primary=obj.primary,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Role State ────────────────────────────────────────────────────────────────

class RoleStateCreate(BaseModel):
    partyRoleStateCL: str = Field(..., examples=["ACTIVE"])


class RoleStateRead(BaseModel):
    id: uuid.UUID
    partyRoleStateCL: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "RoleStateRead":
        return cls(
            id=obj.id,
            partyRoleStateCL=obj.party_role_state_cl,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Party Role ────────────────────────────────────────────────────────────────

class PartyRoleCreate(BaseModel):
    party_role_type_code: str = Field(default="BUSINSSDM1", examples=["BUSINSSDM1"])
    states: list[RoleStateCreate] = []
    eligible_identifiers: list[EligibleIdentifierCreate] = []
    eligible_contacts: list[EligibleContactCreate] = []


class PartyRoleRead(BaseModel):
    id: uuid.UUID
    party_id: uuid.UUID
    party_role_type_code: str
    states: list[RoleStateRead]
    eligible_identifiers: list[EligibleIdentifierRead]
    eligible_contacts: list[EligibleContactRead]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "PartyRoleRead":
        return cls(
            id=obj.id,
            party_id=obj.party_id,
            party_role_type_code=obj.party_role_type_code,
            states=[RoleStateRead.from_orm_map(s) for s in obj.states],
            eligible_identifiers=[
                EligibleIdentifierRead.from_orm_map(e) for e in obj.eligible_identifiers
            ],
            eligible_contacts=[
                EligibleContactRead.from_orm_map(c) for c in obj.eligible_contacts
            ],
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
