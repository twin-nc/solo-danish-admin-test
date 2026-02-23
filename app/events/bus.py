import asyncio
import logging
from collections import defaultdict
from typing import Type

from app.events.base import BaseEvent, EventBus, EventHandler

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed %s to %s", handler.__name__, event_type.__name__)

    async def publish(self, event: BaseEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        logger.debug(
            "Publishing %s (event_id=%s) to %d handler(s)",
            type(event).__name__,
            event.event_id,
            len(handlers),
        )
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception(
                    "Handler %s raised an exception for event %s",
                    handler.__name__,
                    type(event).__name__,
                )
