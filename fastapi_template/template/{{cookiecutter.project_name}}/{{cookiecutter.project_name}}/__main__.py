import os
import shutil

import uvicorn

{%- if cookiecutter.gunicorn == "True" %}
from {{cookiecutter.project_name}}.gunicorn_runner import GunicornApplication
{%- endif %}
from {{cookiecutter.project_name}}.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    {%- if cookiecutter.gunicorn == "True" %}
    if settings.reload:
        uvicorn.run(
            "{{cookiecutter.project_name}}.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        # We choose gunicorn only if reload
        # option is not used, because reload
        # feature doen't work with Uvicorn workers.
        GunicornApplication(
            "{{cookiecutter.project_name}}.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',  # noqa: WPS323
        ).run()
    {%- else %}
    uvicorn.run(
        "{{cookiecutter.project_name}}.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.value.lower(),
        factory=True,
    )
    {%- endif %}

if __name__ == "__main__":
    main()
