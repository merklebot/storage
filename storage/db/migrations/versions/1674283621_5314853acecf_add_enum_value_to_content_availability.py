"""add enum value to content availability

Revision ID: 5314853acecf
Revises: 209e2baad6e1
Create Date: 2023-01-21 09:47:01.173291

"""
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "5314853acecf"
down_revision = "209e2baad6e1"
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.execute("COMMIT")
        op.execute("ALTER TYPE contentavailability ADD VALUE 'PENDING'")
    except Exception as e:
        print(e)


@for_each_tenant_schema
def downgrade(schema: str):
    op.drop_column("contents", "availability", schema=schema)
    op.execute("ALTER TYPE contentavailability RENAME TO contentavailability_old")
    op.execute(
        "CREATE TYPE contentavailability "
        "AS ENUM('INSTANT', 'ENCRYPTED', 'ARCHIVE', 'ABSENT')"
    )
    op.execute(
        (
            f"ALTER TABLE {schema}.contents "
            "ALTER COLUMN availability TYPE contentavailability USING "
            "contentavailability::text::contentavailability"
        )
    )
    op.execute("DROP TYPE contentavailability_old")
