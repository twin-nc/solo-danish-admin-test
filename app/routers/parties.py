import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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
) -> PartyRead:
    party = await service.register_party(payload, db)
    return PartyRead.from_orm(party)


@router.get("/{party_id}", response_model=PartyRead)
async def get_party(
    party_id: uuid.UUID,
    db: Session = Depends(get_db),
    service: PartyService = Depends(get_party_service),
) -> PartyRead:
    party = await service.get_party(party_id, db)
    return PartyRead.from_orm(party)
