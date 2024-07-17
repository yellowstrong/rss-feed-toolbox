from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware


class ExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception):
        request.state.error = exc
        return await request.app.exception_handlers[exc.__class__](request, exc)
