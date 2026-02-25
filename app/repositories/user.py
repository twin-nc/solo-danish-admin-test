import uuid

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_email(self, email: str, db: Session) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID, db: Session) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def create_user(
        self,
        email: str,
        hashed_password: str,
        role: str,
        party_id: uuid.UUID | None,
        db: Session,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
            party_id=party_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
