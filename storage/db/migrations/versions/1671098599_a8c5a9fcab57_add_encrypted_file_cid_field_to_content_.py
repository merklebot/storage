"""Add encrypted_file_cid field to Content model

Revision ID: a8c5a9fcab57
Revises: 51a5feebcdc7
Create Date: 2022-12-15 16:03:19.228967

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "a8c5a9fcab57"
down_revision = "51a5feebcdc7"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column("encrypted_file_cid", sa.String(length=256), nullable=True),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "encrypted_file_cid", schema=schema)
