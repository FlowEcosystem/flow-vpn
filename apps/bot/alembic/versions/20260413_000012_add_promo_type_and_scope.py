"""add promo type and scope fields

Revision ID: 20260413_000012
Revises: 20260413_000011
Create Date: 2026-04-13 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20260413_000012"
down_revision = "20260413_000011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "promo_codes",
        sa.Column("is_infinite", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "promo_codes",
        sa.Column("apply_to_all", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("promo_codes", "apply_to_all")
    op.drop_column("promo_codes", "is_infinite")
