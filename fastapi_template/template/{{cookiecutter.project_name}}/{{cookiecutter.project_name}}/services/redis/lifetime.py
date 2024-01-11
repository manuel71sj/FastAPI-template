import redis.asyncio as redis     # type: ignore

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from redis.asyncio import ConnectionPool

from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}}.utils.health_check import http_limit_callback


async def init_redis(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection pool for redis.

    :param app: current fastapi application.
    """
    app.state.redis_pool = ConnectionPool.from_url(
        str(settings.redis_url),
    )

    r = redis.Redis(connection_pool=app.state.redis_pool)

    FastAPICache.init(RedisBackend(r), prefix='{{cookiecutter.project_name}}')

    # 리미터 연결
    await FastAPILimiter.init(
        r,
        prefix=settings.limiter_redis_prefix,
        http_callback=http_limit_callback,
    )
    

async def shutdown_redis(app: FastAPI) -> None:  # pragma: no cover
    """
    Closes redis connection pool.

    :param app: current FastAPI app.
    """
    FastAPICache.reset()

    # 닫기 리미터
    await FastAPILimiter.close()

    await app.state.redis_pool.disconnect()
