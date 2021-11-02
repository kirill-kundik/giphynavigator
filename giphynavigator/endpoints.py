"""Endpoints module."""

from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from giphynavigator.container import Container
from giphynavigator.models import SearchObject, Response
from giphynavigator.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=Response)
@inject
async def index(
        query: Optional[str] = None,
        limit: Optional[str] = None,
        offset: int = 0,
        default_query: str = Depends(Provide[Container.config.default.query]),
        default_limit: int = Depends(Provide[Container.config.default.limit.as_int()]),
        search_service: SearchService = Depends(Provide[Container.search_service]),
):
    query = query or default_query
    limit = limit or default_limit

    search: SearchObject = await search_service.search(query, limit, offset)

    return {
        "query": query,
        "limit": limit,
        "offset": offset,
        "gifs": search.gifs,
    }
