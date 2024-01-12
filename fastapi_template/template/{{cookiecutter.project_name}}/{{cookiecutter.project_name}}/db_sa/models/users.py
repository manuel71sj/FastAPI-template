# type: ignore
import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB, SQLModelUserDatabaseAsync

from {{cookiecutter.project_name}}.db.base import BaseUUIDModel
from {{cookiecutter.project_name}}.db.dependencies import get_db_session
from {{cookiecutter.project_name}}.settings import settings
from sqlmodel import Field
from sqlmodel.ext.asyncio.session import AsyncSession


class User(SQLModelBaseUserDB, BaseUUIDModel, table=True):
    email: str = Field(max_length=50, unique=True, index=True, description='E-mail')
    """Represents a user entity."""

    class ConfigDict:
        from_attributes = True


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Represents a read command for a user."""


class UserCreate(schemas.BaseUserCreate):
    """Represents a create command for a user."""


class UserUpdate(schemas.BaseUserUpdate):
    """Represents an update command for a user."""


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages a user session and its tokens."""
    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> SQLModelUserDatabaseAsync:
    """
    Yield a SQLModelUserDatabaseAsync instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLModelUserDatabaseAsync.
    """
    yield SQLModelUserDatabaseAsync(session, User)


async def get_user_manager(
    user_db: SQLModelUserDatabaseAsync = Depends(get_user_db), # noqa: B008
) -> UserManager:
    """
    Yield a UserManager instance.

    :param user_db: SQLAlchemy user db instance
    :yields: an instance of UserManager.
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """
    Return a JWTStrategy in order to instantiate it dynamically.

    :returns: instance of JWTStrategy with provided settings.
    """
    return JWTStrategy(secret=settings.users_secret, lifetime_seconds=None)


{%- if cookiecutter.jwt_auth == "True" %}
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
{%- endif %}

{%- if cookiecutter.cookie_auth == "True" %}
cookie_transport = CookieTransport()
auth_cookie = AuthenticationBackend(
    name="cookie", transport=cookie_transport, get_strategy=get_jwt_strategy
)
{%- endif %}

backends = [
    {%- if cookiecutter.cookie_auth == "True" %}
    auth_cookie,
    {%- endif %}
    {%- if cookiecutter.jwt_auth == "True" %}
    auth_jwt,
    {%- endif %}
]

api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)

current_active_user = api_users.current_user(active=True)
