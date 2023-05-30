"""add merklebot_user_id field to tenants table

Revision ID: e668720dee8d
Revises: 67c20c6f5712
Create Date: 2023-05-30 03:44:46.601064

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e668720dee8d"
down_revision = "67c20c6f5712"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tenants", sa.Column("merklebot_user_id", sa.String()), schema="shared"
    )


def downgrade():
    op.drop_column("tenants", "merklebot_user_id", schema="shared")
    pass
