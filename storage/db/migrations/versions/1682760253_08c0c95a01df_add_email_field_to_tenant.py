"""add email field to tenant

Revision ID: 08c0c95a01df
Revises: 6d74e5e83072
Create Date: 2023-04-29 12:24:13.757101

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "08c0c95a01df"
down_revision = "6d74e5e83072"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tenants", sa.Column("owner_email", sa.String()), schema="shared")


def downgrade():
    op.drop_column("tenants", "owner_email", schema="shared")
    pass
