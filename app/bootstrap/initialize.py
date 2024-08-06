from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.config.app_config import app_config
from app.controller import register_routers
from app.models import User
from app.dao.user_dao import UserDao
from app.helper.database_helper import get_database_session
from app.helper.redis_helper import redis_client
from app.middleware import ExceptionsMiddleware
from app.middleware.jwt_auth_middleware import JwtAuthMiddleware
from app.errors import app_error_handler, http_error_handler, validation_error_hanler
from app.middleware.access_middleware import AccessMiddleware
from app.utils import hashing
from scheduler import Scheduler


@asynccontextmanager
async def register_init(app: FastAPI):
    init_super_user()
    redis_client.open()
    Scheduler()

    yield

    redis_client.close()
    Scheduler().stop()


def register_app():
    app = FastAPI(
        title=app_config.TITLE,
        docs_url=app_config.DOCS_URL,
        lifespan=register_init,
    )
    register_static_file(app)
    register_middleware(app)
    register_router(app)
    register_exception(app)
    return app


def register_static_file(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def register_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ExceptionsMiddleware)
    if app_config.JWT_ENABLE is False:
        app.add_middleware(JwtAuthMiddleware)
    app.add_middleware(AccessMiddleware)


def register_router(app: FastAPI):
    for router in register_routers:
        app.include_router(router.router)


def register_exception(app: FastAPI):
    http_error_handler.register_http_error_handler(app)
    app_error_handler.register_app_error_handle(app)
    validation_error_hanler.register_validation_error_handler(app)


def init_super_user():
    with get_database_session() as session:
        super_user = UserDao.get_user_by_username(session=session, username='admin')
        if not super_user:
            super_user_model = User(
                username='admin',
                password=hashing.get_password_hash('123456'),
            )
            UserDao.create_user(session, super_user_model)
