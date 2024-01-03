from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class LogMiddleware(BaseHTTPMiddleware):
    @logger.catch
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        logger.bind(
            req={
                "method": request.method,
                "url": request.url,
                "user_agent": request.headers.get("user-agent"),
                "cookie": request.headers.get("cookie"),
            },
            res={"status_code": response.status_code},
        ).info("Incoming request")
        return response
