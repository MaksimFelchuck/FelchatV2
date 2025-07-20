"""add updated_at column to users

Revision ID: 20250719_105440
Revises: 68a53938392b
Create Date: 2025-07-19 10:54:40.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20250719_105440"
down_revision: Union[str, Sequence[str], None] = "68a53938392b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add updated_at column to users table."""
    # Add updated_at column with default value
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Update existing records to have updated_at = created_at
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")


def downgrade() -> None:
    """Remove updated_at column from users table."""
    op.drop_column("users", "updated_at")
