from fastapi import Request
from app.config.app_config import app_config
from app.errors import AuthenticationError
from app.helper.jwt_helper import JwtHelper
from app.service.auth_service import AuthService
from app.types.apiproto import TokenData


async def get_current_user(request: Request):
    token = request.headers.get("x-token", "")
    token_info = JwtHelper(
        secret_key=app_config.JWT_SECRET_KEY,
        algorithm=app_config.JWT_ALGORITHM,
        expired=app_config.JWT_EXPIRED,
        iss=app_config.JWT_ISS,
    ).decode(token, TokenData)
    if not isinstance(token_info, TokenData):
        raise AuthenticationError(token_info)
    user = AuthService.get_user_by_id(token_info.user_id)
    if user.disabled:
        raise AuthenticationError('用户被禁用')
    return user
