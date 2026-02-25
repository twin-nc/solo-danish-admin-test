import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User
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
    _: User = Depends(require_role("ADMIN", "OFFICER")),
) -> PartyRoleRead:
    role = await service.assign_role(party_id, payload, db)
    return PartyRoleRead.from_orm(role)


@router.get("/{party_id}/roles", response_model=list[PartyRoleRead])
async def list_roles(
    party_id: uuid.UUID,
    db: Session = Depends(get_db),
    service: PartyService = Depends(get_party_service),
    current_user: User = Depends(get_current_user),
) -> list[PartyRoleRead]:
    if current_user.role == "TAXPAYER" and current_user.party_id != party_id:
        raise HTTPException(status_code=404, detail="Party not found")
    roles = await service.list_roles(party_id, db)
    return [PartyRoleRead.from_orm(r) for r in roles]
