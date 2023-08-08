"""add cars model to db

Revision ID: 473b2c5534a9
Revises: 441e1f8b12a5
Create Date: 2023-07-10 15:54:46.887487

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "473b2c5534a9"
down_revision = "441e1f8b12a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pack_uuid", sa.String(), nullable=False),
        sa.Column("tenant_name", sa.String(), nullable=False),
        sa.Column("content_cids", sa.ARRAY(sa.String), server_default="{}"),
        sa.Column("contents_size", sa.BigInteger, nullable=True),
        sa.Column("root_cid", sa.String(), nullable=True),
        sa.Column("comm_p", sa.String(), nullable=True),
        sa.Column("car_size", sa.BigInteger(), nullable=True),
        sa.Column("piece_size", sa.BigInteger(), nullable=True),
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
    op.create_index(op.f("ix_cars_id"), "cars", ["id"], unique=False, schema="shared")


def downgrade() -> None:
    op.drop_index(op.f("ix_cars_id"), table_name="cars", schema="shared")
    op.drop_table("cars", schema="shared")
