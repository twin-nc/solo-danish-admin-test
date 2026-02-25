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


def _set_auth_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int,
) -> None:
    secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        max_age=max_age,
        samesite="lax",
        secure=secure,
        path="/",
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    access_token, refresh_token = await service.login(payload.email, payload.password, db)

    _set_auth_cookie(
        response=response,
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    _set_auth_cookie(
        response=response,
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
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

    _set_auth_cookie(
        response=response,
        key="access_token",
        value=new_access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return TokenResponse(access_token=new_access_token)


@router.post("/logout")
async def logout(response: Response) -> dict:
    secure = settings.ENVIRONMENT == "production"
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
    return {"message": "Logged out"}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.from_orm(current_user)
