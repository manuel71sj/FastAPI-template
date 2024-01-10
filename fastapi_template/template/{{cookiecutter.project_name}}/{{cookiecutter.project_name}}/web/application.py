from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

{%- if cookiecutter.enable_loguru == "True" %}
from {{cookiecutter.project_name}}.logging import configure_logging
{%- endif %}
from {{cookiecutter.project_name}}.web.api.router import api_router
from {{cookiecutter.project_name}}.web.lifetime import (
    register_middleware,
    register_shutdown_event,
    register_startup_event,
    register_static_file,
)


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

    # Adds static directory.
    # This directory is used to access swagger files.
    register_static_file(app)

    # Adds middleware.
    register_middleware(app)

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
