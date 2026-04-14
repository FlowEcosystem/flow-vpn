"""add billing tables (tariffs + payments) with default tariffs

Revision ID: 20260414_000015
Revises: 20260414_000014
Create Date: 2026-04-14 00:00:00.000000
"""

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "20260414_000015"
down_revision = "20260414_000014"
branch_labels = None
depends_on = None

_DEFAULT_TARIFFS = [
    {
        "id": str(uuid.uuid4()),
        "name": "1 месяц",
        "duration_days": 30,
        "price_rub": 120,
        "is_active": True,
        "sort_order": 1,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "3 месяца",
        "duration_days": 90,
        "price_rub": 300,
        "is_active": True,
        "sort_order": 2,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "1 год",
        "duration_days": 365,
        "price_rub": 1500,
        "is_active": True,
        "sort_order": 3,
        "created_at": datetime.now(timezone.utc),
    },
]


def upgrade() -> None:
    op.create_table(
        "tariffs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("price_rub", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("tariff_id", sa.UUID(), nullable=True),
        sa.Column("access_id", sa.UUID(), nullable=True),
        sa.Column("amount_rub", sa.Integer(), nullable=False),
        sa.Column("stars_amount", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("payment_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tariff_id"], ["tariffs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["access_id"], ["vpn_accesses.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_external_id", "payments", ["external_id"])

    op.bulk_insert(
        sa.table(
            "tariffs",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("duration_days", sa.Integer),
            sa.column("price_rub", sa.Integer),
            sa.column("is_active", sa.Boolean),
            sa.column("sort_order", sa.Integer),
            sa.column("created_at", sa.DateTime(timezone=True)),
        ),
        _DEFAULT_TARIFFS,
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("tariffs")
