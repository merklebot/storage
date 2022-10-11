"""Logging facilities.

See https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app.
"""


import logging
import sys

from loguru import logger

from storage.config import settings

log = logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOGURU_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(handlers=[{"sink": sys.stdout}])
