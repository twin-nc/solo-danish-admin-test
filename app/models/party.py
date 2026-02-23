import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class Party(Base, TimestampMixin):
    __tablename__ = "parties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_type_code: Mapped[str] = mapped_column(String(50), nullable=False)

    identifiers: Mapped[list["PartyIdentifier"]] = relationship(
        back_populates="party", cascade="all, delete-orphan"
    )
    classifications: Mapped[list["PartyClassification"]] = relationship(
        back_populates="party", cascade="all, delete-orphan"
    )
    states: Mapped[list["PartyState"]] = relationship(
        back_populates="party", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["PartyContact"]] = relationship(
        back_populates="party", cascade="all, delete-orphan"
    )
    names: Mapped[list["PartyName"]] = relationship(
        back_populates="party", cascade="all, delete-orphan"
    )
    roles: Mapped[list["PartyRole"]] = relationship(  # noqa: F821
        back_populates="party", cascade="all, delete-orphan"
    )


class PartyIdentifier(Base, TimestampMixin):
    __tablename__ = "party_identifiers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
    )
    identifier_type_cl: Mapped[str] = mapped_column(String(50), nullable=False)
    identifier_value: Mapped[str] = mapped_column(String(255), nullable=False)

    party: Mapped["Party"] = relationship(back_populates="identifiers")


class PartyClassification(Base, TimestampMixin):
    __tablename__ = "party_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_classification_type_cl: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    classification_value: Mapped[str] = mapped_column(String(100), nullable=False)

    party: Mapped["Party"] = relationship(back_populates="classifications")


class PartyState(Base, TimestampMixin):
    __tablename__ = "party_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
    )
    party_state_cl: Mapped[str] = mapped_column(String(50), nullable=False)

    party: Mapped["Party"] = relationship(back_populates="states")


class PartyContact(Base, TimestampMixin):
    __tablename__ = "party_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
    )
    contact_value: Mapped[str] = mapped_column(String(255), nullable=False)

    party: Mapped["Party"] = relationship(back_populates="contacts")


class PartyName(Base, TimestampMixin):
    __tablename__ = "party_names"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_alias: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    party: Mapped["Party"] = relationship(back_populates="names")
