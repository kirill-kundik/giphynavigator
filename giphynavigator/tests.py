"""Tests module."""

from unittest import mock

import pytest
from httpx import AsyncClient

from giphynavigator.application import app
from giphynavigator.services.giphy_service import GiphyService


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_index(client):
    giphy_client_mock = mock.AsyncMock(spec=GiphyService)
    giphy_client_mock.search.return_value = {
        "data": [
            {"url": "https://giphy.com/gif1.gif", "id": "123", "embed_url": "123"},
            {"url": "https://giphy.com/gif2.gif", "id": "124", "embed_url": "124"},
        ],
    }

    with app.container.giphy_client.override(giphy_client_mock):
        response = await client.get(
            "/search",
            params={
                "query": "test",
                "limit": 10,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        "query": "test",
        "limit": 10,
        "offset": 0,
        "gifs": [
            {
                "url": "https://giphy.com/gif1.gif",
                "id": "123",
                "embed_url": "123",
                "author_avatar": "",
                "author_profile": "",
                "author_username": ""
            },
            {
                "url": "https://giphy.com/gif2.gif",
                "id": "124",
                "embed_url": "124",
                "author_avatar": "",
                "author_profile": "",
                "author_username": ""
            },
        ],
    }


@pytest.mark.asyncio
async def test_index_no_data(client):
    giphy_client_mock = mock.AsyncMock(spec=GiphyService)
    giphy_client_mock.search.return_value = {
        "data": [],
    }

    with app.container.giphy_client.override(giphy_client_mock):
        response = await client.get("/search")

    assert response.status_code == 200
    data = response.json()
    assert data["gifs"] == []


@pytest.mark.asyncio
async def test_index_default_params(client):
    giphy_client_mock = mock.AsyncMock(spec=GiphyService)
    giphy_client_mock.search.return_value = {
        "data": [],
    }

    with app.container.giphy_client.override(giphy_client_mock):
        response = await client.get("/search")

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == app.container.config.default.query()
    assert data["limit"] == app.container.config.default.limit()
