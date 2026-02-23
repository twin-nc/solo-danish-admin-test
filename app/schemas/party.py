import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Identifiers ──────────────────────────────────────────────────────────────

class PartyIdentifierCreate(BaseModel):
    identifierTypeCL: str = Field(..., examples=["TIN"])
    identifierValue: str = Field(..., examples=["1676-123456789"])


class PartyIdentifierRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    identifierTypeCL: str
    identifierValue: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "PartyIdentifierRead":
        return cls(
            id=obj.id,
            identifierTypeCL=obj.identifier_type_cl,
            identifierValue=obj.identifier_value,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Classifications ───────────────────────────────────────────────────────────

class PartyClassificationCreate(BaseModel):
    partyClassificationTypeCL: str = Field(..., examples=["BUSINESS_SIZE"])
    classificationValue: str = Field(..., examples=["SMALL"])


class PartyClassificationRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    partyClassificationTypeCL: str
    classificationValue: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "PartyClassificationRead":
        return cls(
            id=obj.id,
            partyClassificationTypeCL=obj.party_classification_type_cl,
            classificationValue=obj.classification_value,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── States ────────────────────────────────────────────────────────────────────

class PartyStateCreate(BaseModel):
    partyStateCL: str = Field(..., examples=["IN_BUSINESS"])


class PartyStateRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    partyStateCL: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "PartyStateRead":
        return cls(
            id=obj.id,
            partyStateCL=obj.party_state_cl,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Contacts ──────────────────────────────────────────────────────────────────

class PartyContactCreate(BaseModel):
    contactValue: str = Field(..., examples=["info@company.dk"])


class PartyContactRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    contactValue: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "PartyContactRead":
        return cls(
            id=obj.id,
            contactValue=obj.contact_value,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Names ─────────────────────────────────────────────────────────────────────

class PartyNameCreate(BaseModel):
    name: str = Field(..., examples=["Acme ApS"])
    isAlias: bool = False


class PartyNameRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    isAlias: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "PartyNameRead":
        return cls(
            id=obj.id,
            name=obj.name,
            isAlias=obj.is_alias,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


# ── Party ─────────────────────────────────────────────────────────────────────

class PartyCreate(BaseModel):
    partyTypeCode: str = Field(default="ORGADM1", examples=["ORGADM1"])
    identifiers: list[PartyIdentifierCreate]
    classifications: list[PartyClassificationCreate]
    states: list[PartyStateCreate]
    contacts: list[PartyContactCreate]
    names: list[PartyNameCreate]


class PartyRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    partyTypeCode: str
    identifiers: list[PartyIdentifierRead]
    classifications: list[PartyClassificationRead]
    states: list[PartyStateRead]
    contacts: list[PartyContactRead]
    names: list[PartyNameRead]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "PartyRead":
        return cls(
            id=obj.id,
            partyTypeCode=obj.party_type_code,
            identifiers=[PartyIdentifierRead.from_orm_map(i) for i in obj.identifiers],
            classifications=[
                PartyClassificationRead.from_orm_map(c) for c in obj.classifications
            ],
            states=[PartyStateRead.from_orm_map(s) for s in obj.states],
            contacts=[PartyContactRead.from_orm_map(c) for c in obj.contacts],
            names=[PartyNameRead.from_orm_map(n) for n in obj.names],
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
