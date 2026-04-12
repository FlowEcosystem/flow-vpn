"""create app settings table

Revision ID: 20260412_000002
Revises: 20260412_000001
Create Date: 2026-04-12 00:00:02.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260412_000002"
down_revision: str | None = "20260412_000001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


access_mode = postgresql.ENUM(
    "free_access",
    "billing_enabled",
    name="access_mode",
    create_type=False,
)


def upgrade() -> None:
    access_mode.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "app_settings",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("access_mode", access_mode, nullable=False),
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
    op.execute(
        sa.text(
            """
            insert into app_settings (id, access_mode)
            values (1, 'free_access')
            """
        )
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    access_mode.drop(op.get_bind(), checkfirst=True)
