import traceback

from fastapi import status, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.helper.exception_helper import AuthenticationError, AuthorizationError, BizError
from app.utils.response import response_fail


def register_app_error_handle(app: FastAPI):

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, e: AuthenticationError) -> JSONResponse:
        """未登录"""
        return JSONResponse(
            content=jsonable_encoder(response_fail(msg=e.message)),
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, e: AuthorizationError) -> JSONResponse:
        """无权限"""
        return JSONResponse(
            content=jsonable_encoder(response_fail(msg=e.message)),
            status_code=status.HTTP_403_FORBIDDEN
        )

    @app.exception_handler(BizError)
    async def biz_exception_handler(request: Request, e: BizError) -> JSONResponse:
        """业务逻辑异常处理"""
        return JSONResponse(
            content=jsonable_encoder(response_fail(msg=e.message)),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(Exception)
    async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """自定义全局系统错误"""
        traceback.format_exc()
        return JSONResponse(
            content=jsonable_encoder(response_fail(msg=str(exc))),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
