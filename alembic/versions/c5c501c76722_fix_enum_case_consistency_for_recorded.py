"""fix enum case consistency for RECORDED

Revision ID: c5c501c76722
Revises: 39d8e0e0ae8d
Create Date: 2025-09-26 22:36:41.338137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5c501c76722'
down_revision: Union[str, None] = '39d8e0e0ae8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add uppercase RECORDED to enum
    op.execute("ALTER TYPE source_type ADD VALUE IF NOT EXISTS 'RECORDED';")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values easily
    pass
