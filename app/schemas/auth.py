import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    role: str
    party_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj: object) -> "UserRead":
        return cls.model_validate(obj)
