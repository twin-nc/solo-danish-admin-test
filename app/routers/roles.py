import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.parties import get_party_service
from app.schemas.party_role import PartyRoleCreate, PartyRoleRead
from app.services.party import PartyService

router = APIRouter(prefix="/api/v1/parties", tags=["roles"])


@router.post(
    "/{party_id}/roles",
    response_model=PartyRoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def assign_role(
    party_id: uuid.UUID,
    payload: PartyRoleCreate,
    db: Session = Depends(get_db),
    service: PartyService = Depends(get_party_service),
) -> PartyRoleRead:
    role = await service.assign_role(party_id, payload, db)
    return PartyRoleRead.from_orm(role)


@router.get("/{party_id}/roles", response_model=list[PartyRoleRead])
async def list_roles(
    party_id: uuid.UUID,
    db: Session = Depends(get_db),
    service: PartyService = Depends(get_party_service),
) -> list[PartyRoleRead]:
    roles = await service.list_roles(party_id, db)
    return [PartyRoleRead.from_orm(r) for r in roles]
