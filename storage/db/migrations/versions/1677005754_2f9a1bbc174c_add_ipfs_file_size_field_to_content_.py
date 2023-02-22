"""add ipfs_file_size field to content model

Revision ID: 2f9a1bbc174c
Revises: 5314853acecf
Create Date: 2023-02-21 21:55:54.484757

"""
from alembic import op
import sqlalchemy as sa


from storage.db.multitenancy import for_each_tenant_schema


# revision identifiers, used by Alembic.
revision = '2f9a1bbc174c'
down_revision = '5314853acecf'
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column("ipfs_file_size", sa.BigInteger(), nullable=True),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "ipfs_file_size", schema=schema)

