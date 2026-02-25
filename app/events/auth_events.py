import uuid

from app.events.base import BaseEvent


class UserAuthenticated(BaseEvent):
    user_id: uuid.UUID
    role: str
