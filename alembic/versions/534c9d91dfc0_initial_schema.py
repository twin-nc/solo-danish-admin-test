"""initial_schema

Revision ID: 534c9d91dfc0
Revises:
Create Date: 2026-02-23 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "534c9d91dfc0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── parties ──────────────────────────────────────────────────────────────
    op.create_table(
        "parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_type_code", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_identifiers ────────────────────────────────────────────────────
    op.create_table(
        "party_identifiers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identifier_type_cl", sa.String(50), nullable=False),
        sa.Column("identifier_value", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_classifications ────────────────────────────────────────────────
    op.create_table(
        "party_classifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_classification_type_cl", sa.String(50), nullable=False),
        sa.Column("classification_value", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_states ─────────────────────────────────────────────────────────
    op.create_table(
        "party_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_state_cl", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_contacts ───────────────────────────────────────────────────────
    op.create_table(
        "party_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_value", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_names ──────────────────────────────────────────────────────────
    op.create_table(
        "party_names",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_alias", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_roles ──────────────────────────────────────────────────────────
    op.create_table(
        "party_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_role_type_code", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_role_states ────────────────────────────────────────────────────
    op.create_table(
        "party_role_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_role_state_cl", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["party_role_id"], ["party_roles.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_role_eligible_identifiers ──────────────────────────────────────
    op.create_table(
        "party_role_eligible_identifiers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_identifier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("primary", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["party_role_id"], ["party_roles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["party_identifier_id"], ["party_identifiers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── party_role_eligible_contacts ─────────────────────────────────────────
    op.create_table(
        "party_role_eligible_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("primary", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["party_role_id"], ["party_roles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["party_contact_id"], ["party_contacts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("party_role_eligible_contacts")
    op.drop_table("party_role_eligible_identifiers")
    op.drop_table("party_role_states")
    op.drop_table("party_roles")
    op.drop_table("party_names")
    op.drop_table("party_contacts")
    op.drop_table("party_states")
    op.drop_table("party_classifications")
    op.drop_table("party_identifiers")
    op.drop_table("parties")
