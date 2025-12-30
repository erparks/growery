"""add completed_at to notes

Revision ID: b7c8d9e0f1a2
Revises: f3a1c2d4e5f6
Create Date: 2025-12-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7c8d9e0f1a2"
down_revision = "f3a1c2d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("notes", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.create_index(
        op.f("ix_notes_completed_at"), "notes", ["completed_at"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_notes_completed_at"), table_name="notes")
    op.drop_column("notes", "completed_at")


