import uuid
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

{%- if cookiecutter.orm == 'sqlalchemy' %}
from sqlmodel.ext.asyncio.session import AsyncSession
{%- endif %}

from starlette import status
from {{cookiecutter.project_name}}.db.dao.dummy_dao import DummyDAO
from {{cookiecutter.project_name}}.db.models.dummy_model import DummyModel


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    {%- if cookiecutter.orm == "sqlalchemy" %}
    dbsession: AsyncSession,
    {%- endif %}
) -> None:
    """Tests dummy instance creation."""
    {%- if cookiecutter.api_type == 'rest' %}
    url = fastapi_app.url_path_for('create_dummy_model')
    {%- endif %}
    test_name = uuid.uuid4().hex
    {%- if cookiecutter.api_type == 'rest' %}
    response = await client.put(url, json={
        "name": test_name
    })
    {%- endif %}
    assert response.status_code == status.HTTP_200_OK
    {%- if cookiecutter.orm == "sqlalchemy" %}
    dao = DummyDAO(dbsession)
    {%- endif %}
    instances = await dao.filter(name=test_name)
    assert instances[0].name == test_name


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    {%- if cookiecutter.orm == "sqlalchemy" %}
    dbsession: AsyncSession,
    {%- endif %}
) -> None:
    """Tests dummy instance retrieval."""
    {%- if cookiecutter.orm == "sqlalchemy" %}
    dao = DummyDAO(dbsession)
    {%- endif %}
    test_name = uuid.uuid4().hex
    await dao.create_dummy_model(name=test_name)

    {%- if cookiecutter.api_type == 'rest' %}
    url = fastapi_app.url_path_for('get_dummy_models')

    response = await client.get(url)
    dummies = response.json()
    {%- endif %}

    assert response.status_code == status.HTTP_200_OK
    assert len(dummies) == 1
    assert dummies[0]['name'] == test_name
