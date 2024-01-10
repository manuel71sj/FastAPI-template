import asyncio
import sys
import uuid
from asyncio.events import AbstractEventLoop
from typing import Any, AsyncGenerator, Generator
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

{%- if cookiecutter.enable_redis == "True" %}
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from redis.asyncio import ConnectionPool
from {{cookiecutter.project_name}}.services.redis.dependency import get_redis_pool

{%- endif %}
{%- if cookiecutter.enable_rmq == "True" %}
from aio_pika import Channel
from aio_pika.abc import AbstractExchange, AbstractQueue
from aio_pika.pool import Pool
from {{cookiecutter.project_name}}.services.rabbit.dependencies import \
    get_rmq_channel_pool
from {{cookiecutter.project_name}}.services.rabbit.lifetime import (init_rabbit,
                                                                    shutdown_rabbit)

{%- endif %}
{%- if cookiecutter.enable_kafka == "True" %}
from aiokafka import AIOKafkaProducer
from {{cookiecutter.project_name}}.services.kafka.dependencies import get_kafka_producer
from {{cookiecutter.project_name}}.services.kafka.lifetime import (init_kafka,
                                                                   shutdown_kafka)

{%- endif %}

from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}}.web.application import get_app

{%- if cookiecutter.orm == "sqlalchemy" %}
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import (AsyncEngine,
                                    async_sessionmaker, create_async_engine)
from {{cookiecutter.project_name}}.db.dependencies import get_db_session
from {{cookiecutter.project_name}}.db.utils import create_database, drop_database
{%- endif %}


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return 'asyncio'

{%- if cookiecutter.orm == "sqlalchemy" %}
@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from {{cookiecutter.project_name}}.db.meta import meta  # noqa: WPS433
    from {{cookiecutter.project_name}}.db.models import load_all_models  # noqa: WPS433

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()

@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session    # type: ignore
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
{%- endif %}

{%- if cookiecutter.enable_rmq == 'True' %}

@pytest.fixture
async def test_rmq_pool() -> AsyncGenerator[Channel, None]:
    """
    Create rabbitMQ pool.

    :yield: channel pool.
    """
    app_mock = Mock()
    init_rabbit(app_mock)
    yield app_mock.state.rmq_channel_pool
    await shutdown_rabbit(app_mock)


@pytest.fixture
async def test_exchange_name() -> str:
    """
    Name of an exchange to use in tests.

    :return: name of an exchange.
    """
    return uuid.uuid4().hex


@pytest.fixture
async def test_routing_key() -> str:
    """
    Name of routing key to use while binding test queue.

    :return: key string.
    """
    return uuid.uuid4().hex


@pytest.fixture
async def test_exchange(
    test_exchange_name: str,
    test_rmq_pool: Pool[Channel],
) -> AsyncGenerator[AbstractExchange, None]:
    """
    Creates test exchange.

    :param test_exchange_name: name of an exchange to create.
    :param test_rmq_pool: channel pool for rabbitmq.
    :yield: created exchange.
    """
    async with test_rmq_pool.acquire() as conn:
        exchange = await conn.declare_exchange(
            name=test_exchange_name,
            auto_delete=True,
        )
        yield exchange

        await exchange.delete(if_unused=False)


@pytest.fixture
async def test_queue(
    test_exchange: AbstractExchange,
    test_rmq_pool: Pool[Channel],
    test_routing_key: str,
) -> AsyncGenerator[AbstractQueue, None]:
    """
    Creates queue connected to exchange.

    :param test_exchange: exchange to bind queue to.
    :param test_rmq_pool: channel pool for rabbitmq.
    :param test_routing_key: routing key to use while binding.
    :yield: queue binded to test exchange.
    """
    async with test_rmq_pool.acquire() as conn:
        queue = await conn.declare_queue(name=uuid.uuid4().hex)
        await queue.bind(
            exchange=test_exchange,
            routing_key=test_routing_key,
        )
        yield queue

        await queue.delete(if_unused=False, if_empty=False)

{%- endif %}

{%- if cookiecutter.enable_kafka == "True" %}

@pytest.fixture
async def test_kafka_producer() -> AsyncGenerator[AIOKafkaProducer, None]:
    """
    Creates kafka's producer.

    :yields: kafka's producer.
    """
    app_mock = Mock()
    await init_kafka(app_mock)
    yield app_mock.state.kafka_producer
    await shutdown_kafka(app_mock)

{%- endif %}

{% if cookiecutter.enable_redis == "True" -%}
@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()

{%- endif %}

@pytest.fixture
def fastapi_app(
    {%- if cookiecutter.orm == "sqlalchemy" %}
    dbsession: AsyncSession,
    {%- endif %}
    {% if cookiecutter.enable_redis == "True" -%}
    fake_redis_pool: ConnectionPool,
    {%- endif %}
    {%- if cookiecutter.enable_rmq == 'True' %}
    test_rmq_pool: Pool[Channel],
    {%- endif %}
    {%- if cookiecutter.enable_kafka == "True" %}
    test_kafka_producer: AIOKafkaProducer,
    {%- endif %}
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    {%- if cookiecutter.orm == "sqlalchemy" %}
    application.dependency_overrides[get_db_session] = lambda: dbsession
    {%- endif %}
    {%- if cookiecutter.enable_redis == "True" %}
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    {%- endif %}
    {%- if cookiecutter.enable_rmq == 'True' %}
    application.dependency_overrides[get_rmq_channel_pool] = lambda: test_rmq_pool
    {%- endif %}
    {%- if cookiecutter.enable_kafka == "True" %}
    application.dependency_overrides[get_kafka_producer] = lambda: test_kafka_producer
    {%- endif %}
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any   # noqa: ARG001
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
            yield ac
