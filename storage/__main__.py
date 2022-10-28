import argparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tenacity import retry, stop_after_attempt, wait_fixed
from uvicorn import Config, Server

from storage import db
from storage.config import settings
from storage.db.session import SessionLocal, engine
from storage.logging import log, setup_logging
from storage.web.api import api_router


def pre_start():
    log.info("initializing")
    session = SessionLocal()
    retry_db_connect = retry(
        stop=stop_after_attempt(60),  # one minute
        wait=wait_fixed(1),
    )(db.try_connect)
    retry_db_connect(session)
    db.ensure_exists(engine)
    log.info("initialization complete")


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pre-start", help="execute preliminary routine and exit", action="store_true"
    )
    args = parser.parse_args()
    if args.pre_start:
        pre_start()
        exit(0)

    app = FastAPI(title="MerkleBot Storage")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    server = Server(
        Config(
            app,
            host=str(settings.SERVER_HOST),
            port=settings.SERVER_PORT,
            root_path=settings.SERVER_ROOT_PATH,
            log_level=settings.LOGURU_LEVEL.lower(),
        ),
    )

    setup_logging()  # should be called after uvicorn server instantiation

    server.run()
