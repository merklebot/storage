"""add merklebot_user_id field to users table

Revision ID: 67c20c6f5712
Revises: 08c0c95a01df
Create Date: 2023-05-30 03:29:26.440846

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "67c20c6f5712"
down_revision = "08c0c95a01df"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "users",
        sa.Column("merklebot_user_id", sa.String, nullable=True),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("users", "merklebot_user_id", schema=schema)
