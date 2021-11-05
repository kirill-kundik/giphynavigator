import uuid
from typing import List

from giphynavigator.models import Session, Gif
from giphynavigator.services.redis_service import RedisService
from giphynavigator.services.search_service import SearchService


class SessionServiceException(Exception):
    pass


class SessionNotFoundException(SessionServiceException):
    pass


class SessionService:
    def __init__(self, redis_service: RedisService, search_service: SearchService):
        self._redis_service = redis_service
        self._search_service = search_service

    @staticmethod
    def register() -> Session:
        return Session(id=uuid.uuid4())

    async def _load_gifs(self, ids: List[str]) -> List[Gif]:
        gifs = [await self._search_service.gif(gif_id) for gif_id in ids]

        return [gif for gif in gifs if gif]

    async def save(self, session: Session) -> Session:
        if session:
            await self._redis_service.set(f"session_{session.id}", session.dict())
        return session

    async def load(self, session_id: str) -> Session:
        session = await self._redis_service.get(f"session_{session_id}")

        if session:
            return Session(**session)
        raise SessionNotFoundException

    async def history(self, session_id: str, limit: int = 25, offset: int = 0) -> List[Gif]:
        session = await self.load(session_id)

        return await self._load_gifs(session.history[offset:offset + limit])

    async def favorites(self, session_id: str, limit: int = 25, offset: int = 0) -> List[Gif]:
        session = await self.load(session_id)

        return await self._load_gifs(session.favorites[offset:offset + limit])

    async def add_history(self, session_id: str, history_id: str) -> Session:
        session = await self.load(session_id)

        history = dict.fromkeys(session.history)
        if history_id in history:
            del history[history_id]

        history[history_id] = None
        session.history = list(history)

        await self.save(session)

        return session

    async def add_favorite(self, session_id: str, favorite_id: str) -> Session:
        session = await self.load(session_id)

        favorites = dict.fromkeys(session.favorites)
        if favorite_id in favorites:
            return session

        favorites[favorite_id] = None
        session.favorites = list(favorites)

        await self.save(session)

        return session

    async def remove_history(self, session_id: str, history_id: str) -> Session:
        session = await self.load(session_id)

        history = dict.fromkeys(session.history)
        if history_id not in history:
            return session

        del history[history_id]
        session.history = list(history)

        await self.save(session)

        return session

    async def remove_favorite(self, session_id: str, favorite_id: str) -> Session:
        session = await self.load(session_id)

        favorites = dict.fromkeys(session.favorites)
        if favorite_id not in favorites:
            return session

        del favorites[favorite_id]
        session.favorites = list(favorites)

        await self.save(session)

        return session
