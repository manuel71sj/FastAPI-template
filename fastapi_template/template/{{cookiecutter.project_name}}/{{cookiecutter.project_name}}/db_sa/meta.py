from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from {{cookiecutter.project_name}}.settings import settings

meta = SQLModel.metadata

async_engine = create_async_engine(str(settings.db_url), echo=settings.db_echo, future=True)