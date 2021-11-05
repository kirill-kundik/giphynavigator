"""Module with app models."""

from typing import List, Optional

from pydantic import BaseModel


class Gif(BaseModel):
    id: str
    url: str
    embed_url: str
    author_username: str = ""
    author_profile: str = ""
    author_avatar: str = ""


class Session(BaseModel):
    id: str
    history: List[str] = []
    favorites: List[str] = []


class Response(BaseModel):
    query: Optional[str] = None
    limit: int
    offset: int = 0
    gifs: List[Gif]
