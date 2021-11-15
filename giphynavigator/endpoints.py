"""Endpoints module."""

from typing import Optional, List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Path, HTTPException, Query

from giphynavigator.container import Container
from giphynavigator.models import Response, Gif, Session
from giphynavigator.services.search_service import SearchService
from giphynavigator.services.session_service import SessionService
from giphynavigator.utils import UUID_REGEX

router = APIRouter()


@router.get("/", tags=["default"])
async def health_check():
    return {"success": True}


@router.post("/sessions", response_model=Session, status_code=200, tags=["sessions"])
@inject
async def create_session(
        session_service: SessionService = Depends(Provide[Container.session_client]),
):
    session = session_service.register()
    await session_service.save(session)

    return session


@router.get("/sessions/{session_id}", response_model=Session, tags=["sessions"])
@inject
async def get_session(
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        session_service: SessionService = Depends(Provide[Container.session_client]),
):
    return await session_service.load(session_id)


@router.get("/sessions/{session_id}/history", response_model=Response, tags=["sessions"])
@inject
async def get_history(
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        limit: Optional[int] = Query(None, gt=0),
        offset: int = Query(0, ge=0),
        default_limit: int = Depends(Provide[Container.config.default.limit.as_int()]),
        session_service: SessionService = Depends(Provide[Container.session_client]),
):
    limit: int = limit or default_limit

    result: List[Gif] = await session_service.history(session_id, limit, offset)

    return Response(limit=limit, offset=offset, gifs=result)


@router.post("/sessions/{session_id}/history", status_code=200, tags=["sessions"])
@inject
async def add_history(
        item_id: str,
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        session_service: SessionService = Depends(Provide[Container.session_client])
):
    await session_service.add_history(session_id, item_id)


@router.delete("/sessions/{session_id}/history", status_code=200, tags=["sessions"])
@inject
async def remove_history(
        item_id: str,
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        session_service: SessionService = Depends(Provide[Container.session_client])
):
    await session_service.remove_history(session_id, item_id)


@router.get("/sessions/{session_id}/favorites", response_model=Response, tags=["sessions"])
@inject
async def get_favorites(
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        limit: Optional[int] = Query(None, gt=0),
        offset: int = Query(0, ge=0),
        default_limit: int = Depends(Provide[Container.config.default.limit.as_int()]),
        session_service: SessionService = Depends(Provide[Container.session_client]),
):
    limit: int = limit or default_limit

    result: List[Gif] = await session_service.favorites(session_id, limit, offset)

    return Response(limit=limit, offset=offset, gifs=result)


@router.post("/sessions/{session_id}/favorites", status_code=200, tags=["sessions"])
@inject
async def add_favorites(
        item_id: str,
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        session_service: SessionService = Depends(Provide[Container.session_client])
):
    await session_service.add_favorite(session_id, item_id)


@router.delete("/sessions/{session_id}/favorites", status_code=200, tags=["sessions"])
@inject
async def remove_favorites(
        item_id: str,
        session_id: str = Path(..., title="The id of the Session to get", regex=UUID_REGEX),
        session_service: SessionService = Depends(Provide[Container.session_client])
):
    await session_service.remove_favorite(session_id, item_id)


@router.get("/gifs/trending", response_model=Response, tags=["gifs"])
@inject
async def trending_gifs(
        limit: Optional[int] = Query(None, gt=0),
        offset: int = Query(0, ge=0),
        default_limit: int = Depends(Provide[Container.config.default.limit.as_int()]),
        search_service: SearchService = Depends(Provide[Container.search_client])
):
    limit: int = limit or default_limit

    result = await search_service.trending(limit, offset)

    return Response(limit=limit, offset=offset, gifs=result)


@router.get("/gifs/{gif_id}", response_model=Gif, tags=["gifs"])
@inject
async def get_gif(
        gif_id: str = Path(..., title="The id of the Gif to get"),
        search_service: SearchService = Depends(Provide[Container.search_client]),
):
    gif = await search_service.gif(gif_id)

    if gif:
        return gif
    raise HTTPException(status_code=404, detail="Gif not found")


@router.get("/search", response_model=Response, tags=["search"])
@inject
async def search(
        query: Optional[str] = None,
        limit: Optional[int] = Query(None, gt=0),
        offset: int = Query(0, ge=0),
        default_query: str = Depends(Provide[Container.config.default.query]),
        default_limit: int = Depends(Provide[Container.config.default.limit.as_int()]),
        search_service: SearchService = Depends(Provide[Container.search_client]),
):
    query: str = query or default_query
    limit: int = limit or default_limit

    result: List[Gif] = await search_service.search(query, limit, offset)

    return Response(query=query, limit=limit, offset=offset, gifs=result)
