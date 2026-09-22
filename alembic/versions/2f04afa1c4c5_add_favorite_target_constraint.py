"""add favorite target constraint

Revision ID: 2f04afa1c4c5
Revises: 48629c794b8d
Create Date: 2026-09-22 11:21:42.808881

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2f04afa1c4c5"
down_revision: Union[str, Sequence[str], None] = "48629c794b8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add a constraint requiring exactly one favorite target."""

    op.create_check_constraint(
        "ck_favorites_exactly_one_target",
        "favorites",
        "(team_id IS NOT NULL) != (competition_id IS NOT NULL)",
    )


def downgrade() -> None:
    """Remove the favorite target constraint."""

    op.drop_constraint(
        "ck_favorites_exactly_one_target",
        "favorites",
        type_="check",
    )