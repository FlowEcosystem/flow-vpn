"""add source operation id to admin bulk operations

Revision ID: 20260414_000014
Revises: 20260414_000013
Create Date: 2026-04-14 00:00:14.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260414_000014"
down_revision: str | None = "20260414_000013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "admin_bulk_operations",
        sa.Column("source_operation_id", postgresql.UUID(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("admin_bulk_operations", "source_operation_id")
