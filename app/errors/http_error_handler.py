from fastapi import status, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.utils.response import response_fail


def register_http_error_handler(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            # 处理404错误
            return JSONResponse(
                content=jsonable_encoder(response_fail("请求资源不存在")),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        elif exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            # 处理405错误
            return JSONResponse(
                content=jsonable_encoder(response_fail("请求方法错误")),
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        else:
            # 处理其他错误
            return JSONResponse(
                content=jsonable_encoder(response_fail(str(exc))),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
