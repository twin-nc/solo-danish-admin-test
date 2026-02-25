from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    # Populated via dependency override in main.py
    raise NotImplementedError


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    access_token, refresh_token = await service.login(payload.email, payload.password, db)

    secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=secure,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=secure,
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    new_access_token = await service.refresh(token, db)

    secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=secure,
    )
    return TokenResponse(access_token=new_access_token)


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.set_cookie(key="access_token", value="", max_age=0, httponly=True)
    response.set_cookie(key="refresh_token", value="", max_age=0, httponly=True)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.from_orm(current_user)
