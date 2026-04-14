"""vpn_accesses: drop user_id unique constraint (multi-subscription support)

Revision ID: 20260412_000007
Revises: bc2556ac9285
Create Date: 2026-04-12 21:00:00.000000

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20260412_000007"
down_revision: str | None = "bc2556ac9285"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("vpn_accesses_user_id_key", "vpn_accesses", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("vpn_accesses_user_id_key", "vpn_accesses", ["user_id"])
