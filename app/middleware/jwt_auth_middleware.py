from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.errors import AuthenticationError
from app.types.apiproto import TokenData
from app.config.app_config import app_config
from app.helper.jwt_helper import JwtHelper


class JwtAuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.jwtUtil = JwtHelper(
            secret_key=app_config.JWT_SECRET_KEY,
            algorithm=app_config.JWT_ALGORITHM,
            expired=app_config.JWT_EXPIRED,
            iss=app_config.JWT_ISS,
        )

    async def dispatch(self, request: Request, call_next):
        # 排除路由
        path = request.url.path
        no_check_token_path_list = app_config.JWT_NO_CHECK_URIS.split(",")
        if path in no_check_token_path_list:
            return await call_next(request)
        # token校验
        token = request.headers.get("x-token", "")
        token_info = self.jwtUtil.decode(token, TokenData)
        if not isinstance(token_info, TokenData):
            raise AuthenticationError(token_info)
        result = await call_next(request)
        return result
