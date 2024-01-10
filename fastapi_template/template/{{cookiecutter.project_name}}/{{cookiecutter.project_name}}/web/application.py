import logging

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}}.web.api.router import api_router

from importlib import metadata

from {{cookiecutter.project_name}}.web.lifetime import (register_shutdown_event,
                                                        register_startup_event)

from starlette.middleware.base import BaseHTTPMiddleware

{%- if cookiecutter.enable_loguru == "True" %}
from {{cookiecutter.project_name}}.logging import configure_logging
from {{cookiecutter.project_name}}.middleware.log_middleware import log_request_middleware

{%- endif %}

{%- if cookiecutter.self_hosted_swagger == 'True' %}
from pathlib import Path

from fastapi.staticfiles import StaticFiles

APP_ROOT = Path(__file__).parent.parent
{%- endif %}


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    {%- if cookiecutter.enable_loguru == "True" %}
    configure_logging()
    {%- endif %}

    app = FastAPI(
        title="{{cookiecutter.project_name}}",
        version=metadata.version("{{cookiecutter.project_name}}"),
        {%- if cookiecutter.self_hosted_swagger == 'True' %}
        docs_url=None,
        redoc_url=None,
        {% else %}
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        {%- endif %}
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    {%- if cookiecutter.enable_loguru == "True" %}
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
    {% endif %}
    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    {%- if cookiecutter.self_hosted_swagger == 'True' %}
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static"
    )
    {% endif %}

    return app
