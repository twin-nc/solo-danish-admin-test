import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Type

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


EventHandler = Callable[[BaseEvent], Any]


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all registered handlers."""

    @abstractmethod
    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler) -> None:
        """Register a handler for a given event type."""
