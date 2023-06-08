"""add instant_till field to contents table

Revision ID: 441e1f8b12a5
Revises: 9cec17f8177e
Create Date: 2023-06-08 10:11:24.940590

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "441e1f8b12a5"
down_revision = "9cec17f8177e"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column(
            "instant_till",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "instant_till", schema=schema)
