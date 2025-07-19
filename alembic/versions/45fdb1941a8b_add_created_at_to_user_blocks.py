"""add_created_at_to_user_blocks

Revision ID: 45fdb1941a8b
Revises: 20250719_105440
Create Date: 2025-01-25 15:26:03.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45fdb1941a8b'
down_revision: Union[str, Sequence[str], None] = '20250719_105440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add created_at column to user_blocks table."""
    # Add created_at column with default value
    op.add_column('user_blocks', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    # Update existing records to have created_at = current timestamp
    op.execute("UPDATE user_blocks SET created_at = NOW() WHERE created_at IS NULL")
    
    # Make the column non-nullable after setting default values
    op.alter_column('user_blocks', 'created_at', nullable=False)


def downgrade() -> None:
    """Remove created_at column from user_blocks table."""
    op.drop_column('user_blocks', 'created_at')
