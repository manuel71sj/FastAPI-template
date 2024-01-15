from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from {{cookiecutter.project_name}}.common.pagination import DependsPagination, paging_data
from {{cookiecutter.project_name}}.common.response.response_schema import response_base
from {{cookiecutter.project_name}}.db.dao.dummy_dao import DummyDAO
from {{cookiecutter.project_name}}.db.meta import async_engine
from {{cookiecutter.project_name}}.db.models.dummy_model import DummyModel
from {{cookiecutter.project_name}}.web.api.dummy.schema import (DummyModelDTO,
                                                                DummyModelInputDTO)

router = APIRouter()


@logger.catch
@router.get("/", response_model=List[DummyModelDTO])
async def get_dummy_models(
    limit: int = 10,
    offset: int = 0,
    dummy_dao: DummyDAO = Depends(),    # noqa: B008
) -> List[DummyModel]:
    """
    Retrieve all dummy objects from the database.

    :param limit: limit of dummy objects, defaults to 10.
    :param offset: offset of dummy objects, defaults to 0.
    :param dummy_dao: DAO for dummy models.
    :return: list of dummy objects from database.
    """
    logger.info("hello")
    logger.bind(
        payload={
            "limit": limit,
            "offset": offset,
        },
    ).info("get_dummy_models 天")

    return await dummy_dao.get_all_dummies(limit=limit, offset=offset)


@logger.catch
@router.get(
    '/list',
    # response_model=list[DummyModelDTO],
    dependencies=[DependsPagination],
)
async def get_pageed_dummy_model() -> dict[str, Any]:
    async with AsyncSession(async_engine) as db:
        all_data = await DummyDAO.get_all_dummies_without_pagination(db)
        page_data = await paging_data(db, all_data, DummyModelDTO)
    return await response_base.success(data=page_data)


@router.put("/")
async def create_dummy_model(
    new_dummy_object: DummyModelInputDTO,
    dummy_dao: DummyDAO = Depends(),    # noqa: B008
) -> None:
    """
    Creates dummy model in the database.

    :param new_dummy_object: new dummy model item.
    :param dummy_dao: DAO for dummy models.
    """
    await dummy_dao.create_dummy_model(name=new_dummy_object.name)
