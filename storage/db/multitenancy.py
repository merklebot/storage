import functools
from contextlib import contextmanager
from typing import Callable

from alembic import op
from sqlalchemy import MetaData
from sqlalchemy.schema import CreateSchema
from typeguard import typechecked

from storage.db.base_class import Base
from storage.db.models.tenant import Tenant
from storage.db.session import SessionLocal, engine


def get_shared_metadata():
    meta = MetaData()
    for table in Base.metadata.tables.values():
        if table.schema != "tenant":
            table.tometadata(meta)
    return meta


def get_tenant_specific_metadata():
    meta = MetaData(schema="tenant")
    for table in Base.metadata.tables.values():
        if table.schema == "tenant":
            table.tometadata(meta)
    return meta


def tenant_create(name: str, schema: str, host: str) -> None:
    with with_db(schema) as db:
        tenant = Tenant(
            name=name,
            host=host,
            schema=schema,
        )
        db.add(tenant)

        db.execute(CreateSchema(schema))
        get_tenant_specific_metadata().create_all(bind=db.connection())

        db.commit()


@contextmanager
def with_db(tenant_schema: str | None):
    if tenant_schema:
        schema_translate_map = dict(tenant=tenant_schema)
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)

    try:
        db = SessionLocal(bind=connectable)
        yield db
    finally:
        db.close()


@typechecked
def for_each_tenant_schema(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped():
        schemas = op.get_bind().execute("SELECT schema FROM shared.tenants").fetchall()
        for (schema,) in schemas:
            func(schema)

    return wrapped
