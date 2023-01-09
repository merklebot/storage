"""add timestamp mixin

Revision ID: 43ed663dd8e5
Revises: dfe131e37d74
Create Date: 2023-01-09 17:56:48.082020

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "43ed663dd8e5"
down_revision = "dfe131e37d74"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema=schema,
    )

    op.add_column(
        "contents",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "created_at", schema=schema)
    op.drop_column("contents", "updated_at", schema=schema)
