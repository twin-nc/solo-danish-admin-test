import uuid
from typing import Callable

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository

_user_repo = UserRepository()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = _user_repo.get_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_role(*roles: str) -> Callable:
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return dependency
