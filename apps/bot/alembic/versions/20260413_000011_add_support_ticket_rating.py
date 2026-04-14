"""add support ticket rating

Revision ID: 20260413_000011
Revises: 20260412_000010_add_broadcasts
Create Date: 2026-04-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "20260413_000011"
down_revision = "20260412_000010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "support_tickets",
        sa.Column("rating", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("support_tickets", "rating")
