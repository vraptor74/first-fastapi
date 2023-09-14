"""add content column to posts table

Revision ID: 42b842d3a5f8
Revises: 1ff8edf4c9e2
Create Date: 2023-09-11 19:17:56.341621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42b842d3a5f8'
down_revision: Union[str, None] = '1ff8edf4c9e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts",sa.Column("content",sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts","content")
    pass
