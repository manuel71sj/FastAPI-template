from math import ceil
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

from {{cookiecutter.project_name}}.common.exception import errors


async def http_limit_callback(
    request: Request,
    response: Response,
    expire: int,
) -> Any:
    """
    한도 요청 시 기본 콜백 함수

    :param request:
    :param response:
    :param expire: 남은 시간(밀리초)
    :return:
    """
    expires = ceil(expire / 1000)

    raise errors.HTTPError(
        code=429,
        msg='요청이 너무 자주 발생합니다. 나중에 다시 시도하세요.',
        headers={
            'Retry-After': str(expires),
        },
    )


def ensure_unique_route_names(app: FastAPI) -> None:
    """
    Ensure that all routes have unique names.

    :param app: current FastAPI app.
    """
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f'Non-unique route name: {route.name}')
            temp_routes.add(route.name)
