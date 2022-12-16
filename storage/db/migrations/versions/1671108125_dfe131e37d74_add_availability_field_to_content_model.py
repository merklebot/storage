"""Add availability field to Content model

Revision ID: dfe131e37d74
Revises: a8c5a9fcab57
Create Date: 2022-12-15 18:42:05.711981

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "dfe131e37d74"
down_revision = "a8c5a9fcab57"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    op.add_column(
        "contents",
        sa.Column(
            "availability",
            sa.Enum(
                "INSTANT", "ENCRYPTED", "ARCHIVE", "ABSENT", name="contentavailability"
            ),
            nullable=False,
        ),
        schema=schema,
    )


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "availability", schema=schema)
