from typing import Any, Generic, Type, TypeVar

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from {{cookiecutter.project_name}}.db.base import BaseUUIDModel
from {{cookiecutter.project_name}}.utils.uuid6 import UUID

ModelType = TypeVar('ModelType', bound=BaseUUIDModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseUUIDModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseUUIDModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, *, pk: UUID | None = None) -> ModelType | None:
        """
        pkID로 데이터 가져오기

        :param db: AsyncSession
        :param pk: pkID by UUID
        :return: ModelType | None
        """
        model = await db.exec(select(self.model).where(self.model.id == pk))
        return model.first()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType, user_id: UUID | None = None) -> None:
        """
        데이터 생성

        :param db: AsyncSession
        :param obj_in: Pydantic model class
        :param user_id: UUID |

        :return:
        """
        if user_id:
            create_data = self.model(**obj_in.model_dump(), create_user=user_id)
        else:
            create_data = self.model(**obj_in.model_dump())

        db.add(create_data)
        await db.commit()

    async def update(
        self, db: AsyncSession, pk: UUID, obj_in: UpdateSchemaType | dict[str, Any], user_id: UUID | None = None
    ) -> None:
        """
        pkID로 데이터 업데이트

        :param db:
        :param pk:
        :param obj_in: Pydantic model class or dict
        :param user_id:

        :return:
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if user_id:
            update_data.update({'update_user': user_id})

        result = await db.exec(select(self.model).where(self.model.id == pk))
        model = result.one()

        for key, value in update_data.items():
            setattr(model, key, value)

        await db.commit()
        await db.refresh(model)

    async def delete(self, db: AsyncSession, pk: UUID) -> None:
        """
        pkID로 데이터 삭제

        :param db:
        :param pk:

        :return:
        """
        result = await db.exec(select(self.model).where(self.model.id == pk))
        model = result.one()

        await db.delete(model)
        await db.commit()
