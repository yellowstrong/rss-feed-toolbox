from app.dao.user_dao import UserDao
from app import models
from app.helper.database_helper import get_database_session
from app.helper.exception_helper import AuthenticationError, BizError
from app.helper.jwt_helper import JwtHelper
from app.config.app_config import app_config
from app.types import apiproto
from app.utils import hashing


class AuthService:

    @staticmethod
    def login(login_param: apiproto.Login) -> apiproto.Token:
        with get_database_session() as session:
            user = UserDao.get_user_by_username(session, login_param.username)
            if user is None:
                raise BizError('用户不存在')
            if not (login_param.password and hashing.verify_password(login_param.password, user.password)):
                raise BizError('密码错误')
            if user.disabled:
                raise BizError('用户状态异常')
            expired = app_config.JWT_EXPIRED
            jwt_util = JwtHelper(secret_key=app_config.JWT_SECRET_KEY,
                                 algorithm=app_config.JWT_ALGORITHM,
                                 expired=expired,
                                 iss=app_config.JWT_ISS)
            token = jwt_util.generate(apiproto.TokenData(user_id=user.id, username=user.username))
        return apiproto.Token(x_token=token, expired=expired)

    @staticmethod
    def register(user: apiproto.User):
        with get_database_session() as session:
            exist_user = UserDao.get_user_by_username(session, user.username)
            if exist_user is not None:
                raise BizError('用户名已存在')
            user_model = models.User(
                id=user.id,
                username=user.username,
                password=hashing.get_password_hash(user.password),
                avatar=user.avatar,
                admin=user.admin,
                disabled=user.disabled,
            )
            UserDao.create_user(session, user_model)

    @staticmethod
    def get_user_by_id(id: int) -> apiproto.User:
        with get_database_session() as session:
            user = UserDao.get_user_by_id(session, id)
            if user is None:
                raise BizError('用户不存在')
            return apiproto.User(
                username=user.username,
                avatar=user.avatar,
                admin=user.admin,
                disabled=user.disabled,
            )
