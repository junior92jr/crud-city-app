"""Module that contains the main Fastapi application."""

from fastapi import FastAPI

from app.city_api import views


def create_application() -> FastAPI:
    """Return a FastApi application."""

    application = FastAPI()
    application.include_router(
        views.router, prefix="/city", tags=["Cities API"])

    return application


app = create_application()
