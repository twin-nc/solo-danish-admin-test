import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.events.auth_events import UserAuthenticated
from app.events.base import EventBus
from app.models.user import User
from app.repositories.user import UserRepository

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, repo: UserRepository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

    def _hash_password(self, password: str) -> str:
        return _pwd_context.hash(password)

    def _create_token(self, sub: str, role: str, expire_delta: timedelta) -> str:
        expire = datetime.now(timezone.utc) + expire_delta
        payload = {"sub": sub, "role": role, "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def login(self, email: str, password: str, db: Session) -> tuple[str, str]:
        user = self._repo.get_by_email(email, db)
        if user is None or not self._verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = self._create_token(
            sub=str(user.id),
            role=user.role,
            expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = self._create_token(
            sub=str(user.id),
            role=user.role,
            expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        await self._bus.publish(UserAuthenticated(user_id=user.id, role=user.role))
        return access_token, refresh_token

    async def refresh(self, refresh_token_str: str, db: Session) -> str:
        try:
            payload = jwt.decode(
                refresh_token_str,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            user_id_str: str | None = payload.get("sub")
            if user_id_str is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            user_id = uuid.UUID(user_id_str)
        except (JWTError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token")

        user = self._repo.get_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return self._create_token(
            sub=str(user.id),
            role=user.role,
            expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    async def create_user(
        self,
        email: str,
        password: str,
        role: str,
        party_id: uuid.UUID | None,
        db: Session,
    ) -> User:
        hashed = self._hash_password(password)
        return self._repo.create_user(
            email=email,
            hashed_password=hashed,
            role=role,
            party_id=party_id,
            db=db,
        )
