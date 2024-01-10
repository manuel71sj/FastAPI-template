from datetime import datetime
from uuid import UUID

from {{cookiecutter.project_name}}.utils.strings import to_snake_case
from {{cookiecutter.project_name}}.utils.uuid6 import uuid7
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
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={'onupdate': datetime.utcnow},
    )
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
