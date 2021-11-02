"""Containers module."""

from dependency_injector import containers, providers

from giphynavigator import redis
from giphynavigator.services import giphy_service, search_service, redis_service


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["giphynavigator.endpoints"])

    config = providers.Configuration(yaml_files=["config.yml"])

    giphy_client = providers.Factory(
        giphy_service.GiphyService,
        api_key=config.giphy.api_key,
        timeout=config.giphy.request_timeout,
    )

    redis_pool = providers.Resource(
        redis.init_redis,
        host=config.redis_host,
    )

    redis_client = providers.Factory(
        redis_service.RedisService,
        redis=redis_pool,
    )

    search_service = providers.Factory(
        search_service.SearchService,
        giphy_client=giphy_client,
        redis_service=redis_client,
    )
