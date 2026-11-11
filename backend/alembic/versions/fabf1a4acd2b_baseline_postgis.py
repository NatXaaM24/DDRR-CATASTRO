"""baseline postgis

Revision ID: fabf1a4acd2b
Revises: 
Create Date: 2026-11-11 11:49:05.351352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = 'fabf1a4acd2b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
