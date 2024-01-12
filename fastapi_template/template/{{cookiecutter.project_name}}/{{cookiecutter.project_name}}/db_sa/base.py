from datetime import datetime
from uuid import UUID

from {{cookiecutter.project_name}}.utils.strings import to_snake_case
from {{cookiecutter.project_name}}.utils.timezone import timezone
from {{cookiecutter.project_name}}.utils.uuid6 import get_uuid7_str
from sqlalchemy.orm import declared_attr
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel


# id: implements proposal uuid7 draft4
class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(self) -> str:
        return to_snake_case(self.__name__)


class Base(SQLModel):
    """Base for all models."""

    metadata = SQLModel.metadata


class BaseUUIDModel(Base):
    id: UUID = Field(default_factory=get_uuid7_str, primary_key=True, index=True, nullable=False, description='pkID')

    updated_at: datetime | None = Field(
        exclude=True,
        sa_column_kwargs={'onupdate': timezone.now},
        description='Updated at',
    )
    created_at: datetime | None = Field(
        exclude=True,
        default_factory=timezone.now,
        # sa_column_kwargs={'default_factory': timezone.now},
        description='Created at',
    )
