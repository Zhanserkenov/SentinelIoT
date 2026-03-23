"""drop email_verified from users

Revision ID: 9f3b2a1ce8d4
Revises: 58b2dfd5e105
Create Date: 2026-03-22 23:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3b2a1ce8d4"
down_revision: Union[str, Sequence[str], None] = "58b2dfd5e105"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "email_verified")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false())
    )
