from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.helper.logger_helper import logger
from app.utils.timezone import timezone


class AccessMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = timezone.now()
        response = await call_next(request)
        end_time = timezone.now()
        logger.debug(
            f'{request.client.host: <15} | {request.method: <8} | {response.status_code: <6} | '
            f'{request.url.path} | {round((end_time - start_time).total_seconds(), 3) * 1000.0}ms'
        )
        return response
