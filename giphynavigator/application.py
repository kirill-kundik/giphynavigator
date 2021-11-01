"""Application module."""

from fastapi import FastAPI

from .container import Container
from . import endpoints


def create_app() -> FastAPI:
    container = Container()
    container.config.giphy.api_key.from_env("GIPHY_API_KEY")

    web_app = FastAPI()
    web_app.container = container
    web_app.include_router(endpoints.router)
    return web_app


app = create_app()
