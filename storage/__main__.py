import argparse
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.errors import DuplicateSchema
from sqlalchemy.exc import ProgrammingError
from tenacity import retry, stop_after_attempt, wait_fixed
from uvicorn import Config, Server

from storage import __version__, db
from storage.config import settings
from storage.db.models.tenant import Tenant, Token
from storage.db.multitenancy import tenant_create
from storage.db.session import SessionLocal, engine, with_db
from storage.logging import log, setup_logging
from storage.services.content_processor import start_content_processor
from storage.web.api import api_router, tags_metadata
from storage.web.security import create_api_key, get_api_key_hash


def pre_start():
    log.info("initializing")
    session = SessionLocal()
    retry_db_connect = retry(
        stop=stop_after_attempt(60),  # one minute
        wait=wait_fixed(1),
    )(db.try_connect)
    retry_db_connect(session)
    db.ensure_exists(engine)
    db.create_shared_metadata(engine)
    log.info("initialization complete")


def main(args):
    if args.content_processor:
        asyncio.run(start_content_processor())

        exit(0)

    if args.pre_start:
        pre_start()
        exit(0)
    if args.create_default_tenant or args.new_tenant_name:
        tenant_name = (
            "tenant_default" if args.create_default_tenant else args.new_tenant_name
        )
        try:
            tenant = Tenant(
                name=tenant_name,
                schema=tenant_name,
                host=tenant_name.replace("_", "-"),
            )
            tenant_create(tenant)
        except ProgrammingError as e:
            if isinstance(e.orig, DuplicateSchema):
                log.warning(f"tenant creation failure, {tenant.name=}, {e=}")
                return
                # exit(0)
            log.error(f"tenant creation failure, {tenant.name=}, {e=}")
            raise
        log.info(f"tenant created, {tenant.name=}, {tenant.schema=}, {tenant.host=}")
        return
        # exit(0)
    if args.existing_tenant_name:
        with with_db() as database:
            tenant = (
                database.query(Tenant)
                .filter(Tenant.name == args.existing_tenant_name)
                .first()
            )
        if not tenant:
            log.error(f"can't create api key, tenant not exists, {tenant=}")
            exit(1)
        api_key = create_api_key()
        token = Token(
            hashed_token=get_api_key_hash(api_key),
            owner_id=tenant.id,
        )
        with with_db() as database:
            database.add(token)
            database.commit()
        print(api_key)
        return api_key
        # exit(0)

    app = FastAPI(
        title="MerkleBot Storage",
        description="A RESTful API for storing files in web3 storage networks.",
        openapi_tags=tags_metadata,
        version=__version__,
    )
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


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--content-processor",
        help="start processor for files that should be encrypted and archived",
        action="store_true",
    )

    group.add_argument(
        "--pre-start", help="execute preliminary routine and exit", action="store_true"
    )
    group.add_argument(
        "--tenant-create", help="creates new tenant", dest="new_tenant_name"
    )
    group.add_argument(
        "--create-default-tenant",
        help="creates new tenant with tenant_default name",
        action="store_true",
    )
    group.add_argument(
        "--create-api-key-for-tenant",
        help="create API key token for a tenant",
        dest="existing_tenant_name",
    )

    args = parser.parse_args()
    main(args)
