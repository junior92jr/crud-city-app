from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.cities import routers
from app.database import create_db_and_tables
from app.utils.logger import logger_config

logger = logger_config(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Triggers event before Fast API is started."""

    create_db_and_tables()

    logger.info("startup: triggered")

    yield

    logger.info("shutdown: triggered")


def create_application() -> FastAPI:
    """Return a FastApi application."""

    application = FastAPI(
        docs_url="/",
        lifespan=lifespan,
    )

    application.include_router(routers.router, prefix="/api/v1", tags=["Items"])

    return application


app = create_application()
