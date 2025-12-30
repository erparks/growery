"""create notes

Revision ID: f3a1c2d4e5f6
Revises: ecdaab6a8955
Create Date: 2025-12-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f3a1c2d4e5f6"
down_revision = "ecdaab6a8955"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("photo_history_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plant_id"],
            ["plants.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["photo_history_id"],
            ["photo_histories.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notes_plant_id"), "notes", ["plant_id"], unique=False
    )
    op.create_index(
        op.f("ix_notes_created_at"), "notes", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_notes_due_date"), "notes", ["due_date"], unique=False
    )
    op.create_index(
        op.f("ix_notes_photo_history_id"),
        "notes",
        ["photo_history_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_notes_photo_history_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_due_date"), table_name="notes")
    op.drop_index(op.f("ix_notes_created_at"), table_name="notes")
    op.drop_index(op.f("ix_notes_plant_id"), table_name="notes")
    op.drop_table("notes")


