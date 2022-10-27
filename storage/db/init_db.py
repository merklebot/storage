from sqlalchemy.engine import Engine
from sqlalchemy_utils.functions import create_database, database_exists

from storage.db.session import SessionLocal
from storage.logging import log


def ensure_exists(engine: Engine) -> None:
    if not database_exists(engine.url):
        log.warn(f"db not exists, {engine.url=}")
        create_database(engine.url)
        log.info(f"db created, {engine.url=}")


def try_connect(db: SessionLocal) -> None:
    try:
        db.execute("SELECT 1")
    except Exception as e:
        log.error(e)
        raise e
