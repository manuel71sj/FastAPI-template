import logging
from typing import Awaitable, Callable

from fastapi import FastAPI
from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}}.core import path_conf
{%- if cookiecutter.enable_loguru == "True" %}
from {{cookiecutter.project_name}}.middleware.log_middleware import log_request_middleware
{% endif %}

{%- if cookiecutter.enable_redis == "True" %}
from {{cookiecutter.project_name}}.services.redis.lifetime import (init_redis,
                                                                   shutdown_redis)
{%- endif %}

{%- if cookiecutter.enable_rmq == "True" %}
from {{cookiecutter.project_name}}.services.rabbit.lifetime import (init_rabbit,
                                                                    shutdown_rabbit)
{%- endif %}

{%- if cookiecutter.enable_kafka == "True" %}
from {{cookiecutter.project_name}}.services.kafka.lifetime import (init_kafka,
                                                                   shutdown_kafka)
{%- endif %}

{%- if cookiecutter.enable_taskiq == "True" %}
from {{cookiecutter.project_name}}.tkq import broker
{%- endif %}

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from {{cookiecutter.project_name}}.settings import settings


{%- if cookiecutter.orm == "sqlalchemy" %}
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

    {%- if cookiecutter.enable_migrations != "True" %}
from {{cookiecutter.project_name}}.db.meta import meta
from {{cookiecutter.project_name}}.db.models import load_all_models
    {%- endif %}


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    app.state.db_engine = engine
    app.state.db_session_factory = session_factory
{%- endif %}

{%- if cookiecutter.enable_migrations != "True" %}
    {%- if cookiecutter.orm in ["sqlalchemy"] %}
async def _create_tables() -> None:  # pragma: no cover
    """Populates tables in the database."""
    load_all_models()
        {%- if cookiecutter.orm == "sqlalchemy" %}
    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as connection:
        await connection.run_sync(meta.create_all)
    await engine.dispose()
        {%- endif %}
    {%- endif %}
{%- endif %}

def register_startup_event(app: FastAPI) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        app.middleware_stack = None
        {%- if cookiecutter.enable_taskiq == "True" %}
        if not broker.is_worker_process:
            await broker.startup()
        {%- endif %}
        {%- if cookiecutter.orm == "sqlalchemy" %}
        _setup_db(app)
        {%- endif %}
        {%- if cookiecutter.db_info.name != "none" and cookiecutter.enable_migrations != "True" %}
            {%- if cookiecutter.orm in ["sqlalchemy"] %}
        await _create_tables()
            {%- endif %}
        {%- endif %}
        {%- if cookiecutter.enable_redis == "True" %}
        init_redis(app)
        {%- endif %}
        {%- if cookiecutter.enable_rmq == "True" %}
        init_rabbit(app)
        {%- endif %}
        {%- if cookiecutter.enable_kafka == "True" %}
        await init_kafka(app)
        {%- endif %}
        app.middleware_stack = app.build_middleware_stack()
        
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(app: FastAPI) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        {%- if cookiecutter.enable_taskiq == "True" %}
        if not broker.is_worker_process:
            await broker.shutdown()
        {%- endif %}
        {%- if cookiecutter.orm == "sqlalchemy" %}
        await app.state.db_engine.dispose()
        {%- endif %}
        {%- if cookiecutter.enable_redis == "True" %}
        await shutdown_redis(app)
        {%- endif %}
        {%- if cookiecutter.enable_rmq == "True" %}
        await shutdown_rabbit(app)
        {%- endif %}
        {%- if cookiecutter.enable_kafka == "True" %}
        await shutdown_kafka(app)
        {%- endif %}
        pass  # noqa: WPS420

    return _shutdown


def register_static_file(app: FastAPI) -> None:
    """
    Register static file.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    if settings.static_file:
        import os

        from fastapi.staticfiles import StaticFiles

        if not os.path.exists(path_conf.StaticPath):
            os.makedirs(path_conf.StaticPath)
        app.mount('/static', StaticFiles(directory=path_conf.StaticPath), name='static')


def register_middleware(app: FastAPI) -> None:
    """
    Register middleware.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """
    # gzip
    if settings.middleware_gzip:
        app.add_middleware(GZipMiddleware)
{%- if cookiecutter.enable_loguru == "True" %}
    # 인터페이스 액세스 로그
    if settings.middleware_access:
        app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
{% endif %}
    # CORS
    if settings.middleware_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
