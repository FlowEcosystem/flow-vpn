"""app_settings: add max vpn accesses per user

Revision ID: 20260412_000008
Revises: 20260412_000007
Create Date: 2026-04-12 23:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20260412_000008"
down_revision: str | None = "20260412_000007"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "app_settings",
        sa.Column(
            "max_vpn_accesses_per_user",
            sa.SmallInteger(),
            nullable=False,
            server_default="0",
        ),
    )
    op.alter_column("app_settings", "max_vpn_accesses_per_user", server_default=None)


def downgrade() -> None:
    op.drop_column("app_settings", "max_vpn_accesses_per_user")
