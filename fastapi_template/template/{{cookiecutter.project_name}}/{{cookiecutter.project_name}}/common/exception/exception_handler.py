from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import PydanticUserError, ValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from {{cookiecutter.project_name}}.common.exception.errors import BaseExceptionMixin
from {{cookiecutter.project_name}}.common.response.response_schema import response_base
from {{cookiecutter.project_name}}.db.schemas.base import (
    CUSTOM_USAGE_ERROR_MESSAGES,
    CUSTOM_VALIDATION_ERROR_MESSAGES,
    convert_usage_errors,
    convert_validation_errors,
)
from {{cookiecutter.project_name}}.settings import settings

if TYPE_CHECKING:
    from pydantic_core import ErrorDetails


@sync_to_async
def _get_exception_code(status_code: int) -> int:
    """
    오류 코드 가져오기

    :param status_code: HTTP 상태 코드
    :return: 오류 코드
    """
    try:
        STATUS_PHRASES[status_code]
    except Exception:
        code = 400
    else:
        code = status_code

    return code


async def _validation_exception_handler(e: RequestValidationError | ValidationError) -> JSONResponse:
    """
    유효성 검사 오류 처리기

    :param e: 오류
    :return:
    """

    message = ''
    errors: list[ErrorDetails] = await convert_validation_errors(e, CUSTOM_VALIDATION_ERROR_MESSAGES)

    for error in errors[:1]:
        if error.get('type') == 'json_invalid':
            message += 'json 구문 분석 실패'
        else:
            error_input = error.get('input')

            ctx = error.get('ctx')
            ctx_error = ctx.get('error') if ctx else None

            # field = str(error.get('loc')[-1])
            loc = error.get('loc')
            field = str(loc[-1]) if loc is not None else 'unknown'

            error_msg = error.get('msg')
            message += f'{field} {ctx_error if ctx else error_msg}: {error_input}'

    return JSONResponse(
        status_code=422,
        content=await response_base.fail(
            code=422,
            msg='잘못된 요청 매개변수' if len(message) == 0 else f'잘못된 요청 매개변수: {message}',
            data={'errors': e.errors()} if message == '' and settings.reload is True else None,
        ),
    )


def register_exception(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        HTTP 예외 처리기

        :param request: 요청
        :param exc: 예외
        :return:
        """
        content = {'code': exc.status_code, 'msg': exc.detail}
        request.state.__request_http_exception__ = content

        return JSONResponse(
            status_code=await _get_exception_code(exc.status_code),
            content=await response_base.fail(code=content.get('code'), msg=content['msg']),  # type: ignore
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        FastAPI 유효성 검사 예외 처리기

        :param request: 요청
        :param exc: 예외
        :return:
        """
        return await _validation_exception_handler(exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """
        Pydantic 유효성 검사 예외 처리기

        :param request: 요청
        :param exc: 예외
        :return:
        """
        return await _validation_exception_handler(exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError) -> JSONResponse:
        """
        Pydantic 사용자 오류 처리기

        :param request: 요청
        :param exc: 예외
        :return:
        """
        return JSONResponse(
            status_code=500,
            content=await response_base.fail(
                code=exc.code, msg=await convert_usage_errors(exc, CUSTOM_USAGE_ERROR_MESSAGES)  # type: ignore
            ),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        모든 예외 처리기

        :param request: 요청
        :param exc: 예외
        :return:
        """
        if isinstance(exc, BaseExceptionMixin):
            return JSONResponse(
                status_code=await _get_exception_code(exc.code),
                content=await response_base.fail(code=exc.code, msg=str(exc.msg), data=exc.data if exc.data else None),
                background=exc.background,
            )

        elif isinstance(exc, AssertionError):
            return JSONResponse(
                status_code=500,
                content=await response_base.fail(
                    code=500,
                    msg=','.join(exc.args)  # type: ignore
                    if exc.args
                    else exc.__repr__()
                    if not exc.__repr__().startswith('AssertionError()')
                    else exc.__doc__,
                )
                if settings.environment == 'dev'
                else await response_base.fail(code=500, msg='Internal Server Error'),
            )
        else:
            import traceback

            from loguru import logger

            logger.error(f'알 수 없는 이상 징후: {exc}')
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content=await response_base.fail(code=500, msg=str(exc))
                if settings.environment == 'dev'
                else await response_base.fail(code=500, msg='Internal Server Error'),
            )

    if settings.middleware_cors:

        @app.exception_handler(500)
        async def cors_status_code_500_exception_handler(request: Request, exc: Exception) -> JSONResponse:
            """
            CORS 500 예외 처리기

            :param request: 요청
            :param exc: 예외
            :return:
            """
            response = JSONResponse(
                status_code=exc.code if isinstance(exc, BaseExceptionMixin) else 500,
                content={'code': exc.code, 'msg': exc.msg, 'data': exc.data}
                if isinstance(exc, BaseExceptionMixin)
                else await response_base.fail(code=500, msg=str(exc))
                if settings.environment == 'dev'
                else await response_base.fail(code=500, msg='Internal Server Error'),
                background=exc.background if isinstance(exc, BaseExceptionMixin) else None,
            )

            origin = request.headers.get('origin')

            if origin:
                cors = CORSMiddleware(
                    app=app, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*']
                )
                response.headers.update(cors.simple_headers)
                has_cookie = 'cookie' in request.headers
                if cors.allow_all_origins and has_cookie:
                    response.headers['Access-Control-Allow-Origin'] = origin
                elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers.add_vary_header('Origin')
            return response
