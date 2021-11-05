"""Application module."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from giphynavigator import endpoints
from giphynavigator.container import Container
from giphynavigator.services.session_service import SessionServiceException


def create_app() -> FastAPI:
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.giphy.api_key.from_env("GIPHY_API_KEY")

    web_app = FastAPI()
    web_app.container = container
    web_app.include_router(endpoints.router)
    return web_app


app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SessionServiceException)
async def session_not_found_exception_handler(
        _request: Request, _exc: SessionServiceException
):
    raise HTTPException(status_code=400, detail="You have to register your session.")
