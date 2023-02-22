"""add filename field to content

Revision ID: 6d74e5e83072
Revises: 2f9a1bbc174c
Create Date: 2023-02-21 22:54:20.536378

"""
from alembic import op
import sqlalchemy as sa


from storage.db.multitenancy import for_each_tenant_schema


# revision identifiers, used by Alembic.
revision = '6d74e5e83072'
down_revision = '2f9a1bbc174c'
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column("filename", sa.String(), nullable=True),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "filename", schema=schema)
