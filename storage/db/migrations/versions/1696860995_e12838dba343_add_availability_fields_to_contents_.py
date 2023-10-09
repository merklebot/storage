"""add availability fields to contents table

Revision ID: e12838dba343
Revises: 871b7622dd89
Create Date: 2023-10-09 17:16:35.253856

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "e12838dba343"
down_revision = "871b7622dd89"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "is_instant",
        sa.Column("key", sa.Boolean, nullable=True, server_default="true"),
        schema=schema,
    )
    op.add_column(
        "is_filecoin",
        sa.Column("key", sa.Boolean, nullable=True, server_default="false"),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "is_instant", schema=schema)
    op.drop_column("contents", "is_filecoin", schema=schema)
