"""add admin bulk operations

Revision ID: 20260414_000013
Revises: 20260413_000012
Create Date: 2026-04-14 00:00:13.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260414_000013"
down_revision: str | None = "20260413_000012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_bulk_operations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("target_segment", sa.String(length=32), nullable=False),
        sa.Column("source_page", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("total_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("processed_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("affected_accesses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("target_telegram_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("message_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_admin_bulk_operations_status_created_at",
        "admin_bulk_operations",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_admin_bulk_operations_status_created_at", table_name="admin_bulk_operations")
    op.drop_table("admin_bulk_operations")
