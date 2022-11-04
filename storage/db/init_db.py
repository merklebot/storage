from alembic.migration import MigrationContext
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils.functions import create_database, database_exists

from storage.db.multitenancy import get_shared_metadata
from storage.db.session import SessionLocal
from storage.logging import log


def ensure_exists(engine: Engine) -> None:
    if not database_exists(engine.url):
        log.warn(f"db not exists, {engine.url=}")
        create_database(engine.url)
        log.info(f"db created, {engine.url=}")


def create_shared_metadata(engine: Engine) -> None:
    with engine.begin() as db:
        context = MigrationContext.configure(db)
        if context.get_current_revision() is not None:
            log.info(
                "db already holds alembic revision, skipping shared metadata creation"
            )
            return
        db.execute(CreateSchema("shared"))
        get_shared_metadata().create_all(bind=db)
    log.info("shared metadata created")


def try_connect(db: SessionLocal) -> None:
    try:
        db.execute("SELECT 1")
    except Exception as e:
        log.error(e)
        raise e
