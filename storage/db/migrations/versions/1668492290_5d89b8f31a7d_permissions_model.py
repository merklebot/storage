"""Permissions model

Revision ID: 5d89b8f31a7d
Revises: 848a67166f63
Create Date: 2022-11-15 12:04:50.066051

"""
import sqlalchemy as sa
from alembic import op

from storage.db.multitenancy import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = "5d89b8f31a7d"
down_revision = "848a67166f63"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str):
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.Enum("READ", name="permission_kind"), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignee_id"],
            [f"{schema}.users.id"],
            name=op.f("fk_permissions_assignee_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["content_id"],
            [f"{schema}.contents.id"],
            name=op.f("fk_permissions_content_id_contents"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_permissions")),
        schema=schema,
    )
    op.create_index(
        op.f("ix_permissions_id"),
        "permissions",
        ["id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        op.f("ix_permissions_kind"),
        "permissions",
        ["kind"],
        unique=False,
        schema=schema,
    )
    # ### end Alembic commands ###


@for_each_tenant_schema
def downgrade(schema: str):
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_permissions_kind"),
        table_name="permissions",
        schema=schema,
    )
    op.drop_index(
        op.f("ix_permissions_id"),
        table_name="permissions",
        schema=schema,
    )
    op.drop_table("permissions", schema=schema)
    # ### end Alembic commands ###
