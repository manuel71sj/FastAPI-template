from secrets import token_urlsafe
from time import time

from loguru import logger
from starlette import status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}.utils.access_log_atoms import AccessLogAtoms


async def log_request_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """
    각 요청을 고유하게 식별하고 처리 시간을 기록합니다.

    :param request: request.
    :param call_next: RequestResponseEndpoint.
    :return: Response.
    """
    start_time = time()
    request_id: str = token_urlsafe(settings.request_id_length)
    exception = None

    # keep the same request_id in the context of all subsequent calls to logger
    with logger.contextualize(request_id=request_id):
        try:
            response = await call_next(request)
        except Exception as exc:
            exception = exc
            response = PlainTextResponse(
                "Internal Server Error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        final_time = time()
        elapsed = final_time - start_time

        response_dict = {
            "status": response.status_code,
            "headers": response.headers.raw,
        }

        atoms = AccessLogAtoms(request, response_dict, final_time)  # type: ignore

        data = {
            "client": atoms["h"],
            "schema": atoms["S"],
            "protocol": atoms["H"],
            "method": atoms["m"],
            "path_with_query": atoms["Uq"],
            "status_code": response.status_code,
            "response_length": atoms["b"],
            "elapsed": elapsed,
            "referer": atoms["f"],
            "user_agent": atoms["a"],
        }

        if exception:
            logger.opt(exception=exception).error("unhandled exception", **data)
        else:
            logger.info("log request", **data)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Processed-Time"] = str(elapsed)
    return response
