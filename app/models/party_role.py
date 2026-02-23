import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid
from app.models.party import Party, PartyContact, PartyIdentifier  # noqa: F401


class PartyRole(Base, TimestampMixin):
    __tablename__ = "party_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_role_type_code: Mapped[str] = mapped_column(String(50), nullable=False)

    party: Mapped["Party"] = relationship(back_populates="roles")
    states: Mapped[list["PartyRoleState"]] = relationship(
        back_populates="party_role", cascade="all, delete-orphan"
    )
    eligible_identifiers: Mapped[list["PartyRoleEligibleIdentifier"]] = relationship(
        back_populates="party_role", cascade="all, delete-orphan"
    )
    eligible_contacts: Mapped[list["PartyRoleEligibleContact"]] = relationship(
        back_populates="party_role", cascade="all, delete-orphan"
    )


class PartyRoleState(Base, TimestampMixin):
    __tablename__ = "party_role_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("party_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_role_state_cl: Mapped[str] = mapped_column(String(50), nullable=False)

    party_role: Mapped["PartyRole"] = relationship(back_populates="states")


class PartyRoleEligibleIdentifier(Base, TimestampMixin):
    __tablename__ = "party_role_eligible_identifiers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("party_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_identifier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("party_identifiers.id", ondelete="CASCADE"),
        nullable=False,
    )
    primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    party_role: Mapped["PartyRole"] = relationship(
        back_populates="eligible_identifiers"
    )
    identifier: Mapped["PartyIdentifier"] = relationship()


class PartyRoleEligibleContact(Base, TimestampMixin):
    __tablename__ = "party_role_eligible_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("party_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("party_contacts.id", ondelete="CASCADE"),
        nullable=False,
    )
    primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    party_role: Mapped["PartyRole"] = relationship(back_populates="eligible_contacts")
    contact: Mapped["PartyContact"] = relationship()
