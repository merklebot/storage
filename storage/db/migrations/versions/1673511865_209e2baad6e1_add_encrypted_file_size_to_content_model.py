"""add encrypted_file_size to content model

Revision ID: 209e2baad6e1
Revises: 43ed663dd8e5
Create Date: 2023-01-12 11:24:25.882147

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "209e2baad6e1"
down_revision = "43ed663dd8e5"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column("encrypted_file_size", sa.BigInteger(), nullable=True),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "encrypted_file_size", schema=schema)
