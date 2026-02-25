import logging

from app.events.auth_events import UserAuthenticated

logger = logging.getLogger(__name__)


def on_user_authenticated(event: UserAuthenticated) -> None:
    logger.info(
        "User authenticated — user_id=%s role=%s",
        event.user_id,
        event.role,
    )
