"""Endpoints module."""

from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from giphynavigator.container import Container
from giphynavigator.models import SearchObject, Response, Gif, User
from giphynavigator.services.search_service import SearchService

router = APIRouter()


# TODO:
# @router.get("/gifs/{gif_id}", response_model=Gif)
# @router.post("/registerSession", response_model=User)
# @router.get("/sessions/{session_id}", response_model=User)
# @router.post("/sessions/{session_id}/favorites", response_model=User)

@router.get("/search", response_model=Response)
@inject
async def search(
        query: Optional[str] = None,
        limit: Optional[str] = None,
        offset: int = 0,
        default_query: str = Depends(Provide[Container.config.default.query]),
        default_limit: int = Depends(Provide[Container.config.default.limit.as_int()]),
        search_service: SearchService = Depends(Provide[Container.search_service]),
):
    query = query or default_query
    limit = limit or default_limit

    result: SearchObject = await search_service.search(query, limit, offset)

    return {
        "query": query,
        "limit": limit,
        "offset": offset,
        "gifs": result.gifs,
    }
