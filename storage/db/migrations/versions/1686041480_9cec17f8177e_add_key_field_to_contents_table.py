"""add key field to contents table

Revision ID: 9cec17f8177e
Revises: e668720dee8d
Create Date: 2023-06-06 11:51:20.444318

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "9cec17f8177e"
down_revision = "e668720dee8d"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column("key", sa.String, nullable=True),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "key", schema=schema)
