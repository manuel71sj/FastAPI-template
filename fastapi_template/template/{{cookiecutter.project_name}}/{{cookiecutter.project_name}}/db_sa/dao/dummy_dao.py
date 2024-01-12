from typing import List, Optional

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from {{cookiecutter.project_name}}.db.dependencies import get_db_session
from {{cookiecutter.project_name}}.db.models.dummy_model import DummyModel


class DummyDAO:
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_dummy_model(self, name: str) -> None:
        """
        Add single dummy to session.

        :param name: name of a dummy.
        """
        self.session.add(DummyModel(name=name))

    @staticmethod
    async def get_all_dummies_without_pagination(db: AsyncSession) -> SelectOfScalar[DummyModel]:
        """
        Get all dummy models without pagination.

        :return: stream of dummies.
        """
        return select(DummyModel)

    async def get_all_dummies(self, limit: int, offset: int) -> list[DummyModel]:
        """
        Get all dummy models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of dummies.
        """
        raw_dummies = await self.session.execute(select(DummyModel).limit(limit).offset(offset))

        return list(raw_dummies.scalars().fetchall())

    async def filter(self, name: str | None = None) -> list[DummyModel]:
        """
        Get specific dummy model.

        :param name: name of dummy instance.
        :return: dummy models.
        """
        query = select(DummyModel)
        if name:
            query = query.where(DummyModel.name == name)
        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())
