"""Containers module."""

from dependency_injector import containers, providers

from . import redis
from .services import giphy_service, search_service, redis_service


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    config = providers.Configuration(yaml_files=["config.yml"])

    giphy_client = providers.Factory(
        giphy_service.GiphyService,
        api_key=config.giphy.api_key,
        timeout=config.giphy.request_timeout,
    )

    search_service = providers.Factory(
        search_service.SearchService,
        giphy_client=giphy_client,
    )

    redis_pool = providers.Resource(
        redis.init_redis,
        host=config.redis_host,
        password=config.redis_password,
    )

    service = providers.Factory(
        redis_service.RedisService,
        redis=redis_pool,
    )
