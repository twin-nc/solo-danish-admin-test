import logging

from app.events.party_events import PartyRegistered, PartyRoleAssigned

logger = logging.getLogger(__name__)


def on_party_registered(event: PartyRegistered) -> None:
    logger.info(
        "Party registered — party_id=%s type=%s tin=%s",
        event.party_id,
        event.party_type_code,
        event.tin,
    )


def on_party_role_assigned(event: PartyRoleAssigned) -> None:
    logger.info(
        "Party role assigned — party_id=%s role_id=%s role_type=%s",
        event.party_id,
        event.party_role_id,
        event.party_role_type_code,
    )
