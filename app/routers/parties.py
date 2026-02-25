import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.party import PartyCreate, PartyRead
from app.services.party import PartyService

router = APIRouter(prefix="/api/v1/parties", tags=["parties"])


def get_party_service() -> PartyService:
    # Populated via dependency override in main.py
    raise NotImplementedError


@router.post("", response_model=PartyRead, status_code=status.HTTP_201_CREATED)
async def register_party(
    payload: PartyCreate,
    db: Session = Depends(get_db),
    service: PartyService = Depends(get_party_service),
    _: User = Depends(require_role("ADMIN", "OFFICER")),
) -> PartyRead:
    party = await service.register_party(payload, db)
    return PartyRead.from_orm(party)


@router.get("/{party_id}", response_model=PartyRead)
async def get_party(
    party_id: uuid.UUID,
    db: Session = Depends(get_db),
    service: PartyService = Depends(get_party_service),
    current_user: User = Depends(get_current_user),
) -> PartyRead:
    if current_user.role == "TAXPAYER" and current_user.party_id != party_id:
        raise HTTPException(status_code=404, detail="Party not found")
    party = await service.get_party(party_id, db)
    return PartyRead.from_orm(party)
