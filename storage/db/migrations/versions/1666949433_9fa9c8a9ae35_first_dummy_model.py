"""First dummy model

Revision ID: 9fa9c8a9ae35
Revises:
Create Date: 2022-10-28 15:30:33.281654

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9fa9c8a9ae35"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_id"), "tenants", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_tenants_id"), table_name="tenants")
    op.drop_table("tenants")
    # ### end Alembic commands ###
