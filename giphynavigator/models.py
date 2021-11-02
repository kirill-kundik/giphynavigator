"""Module with app models."""

from typing import List

from pydantic import BaseModel


class Gif(BaseModel):
    id: str
    url: str
    embed_url: str
    author_username: str = ""
    author_profile: str = ""
    author_avatar: str = ""


class User(BaseModel):
    session_id: str
    history: List[Gif] = []
    favorites: List[Gif] = []


class SearchObject(BaseModel):
    gifs: List[Gif] = []


class Response(BaseModel):
    query: str
    limit: int
    offset: int = 0
    gifs: List[Gif]
