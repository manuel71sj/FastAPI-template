from sqlmodel import Field, SQLModel
from {{cookiecutter.project_name}}.db.base import Base
# class DummyModel1(Base):
#     """Model for demo purpose."""
#
#     __tablename__ = 'dummy_model'
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(length=200))  # noqa: WPS432


class DummyModel(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, nullable=True, max_length=200)