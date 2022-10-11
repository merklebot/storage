from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from storage.config import settings
from storage.logging import setup_logging
from storage.web.api import api_router

if __name__ == "__main__":
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
