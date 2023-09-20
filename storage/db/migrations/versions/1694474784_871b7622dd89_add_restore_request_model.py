"""add restore request model

Revision ID: 871b7622dd89
Revises: 473b2c5534a9
Create Date: 2023-09-12 02:26:24.593174

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "871b7622dd89"
down_revision = "473b2c5534a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restore_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_name", sa.String(), nullable=False),
        sa.Column("content_id", sa.Integer, nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("worker_instance", sa.String(), nullable=True),
        sa.Column("webhook_url", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="shared",
    )
    op.create_index(
        op.f("ix_restore_request_id"),
        "restore_requests",
        ["id"],
        unique=False,
        schema="shared",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_restore_request_id"), table_name="restore_requests", schema="shared"
    )
    op.drop_table("restore_requests", schema="shared")
