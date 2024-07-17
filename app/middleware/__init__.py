from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .exceptions_middleware import ExceptionsMiddleware
from .usetime_middleware import UseTimeMiddleware
from .jwt_middleware import JwtMiddleware
from app.config.app_config import app_config

# 定义注册顺序
middlewareList = [
    ExceptionsMiddleware,
    JwtMiddleware,
    # UseTimeMiddleware,
]


def registerMiddlewareHandle(app: FastAPI):
    """ 注册中间件 """

    if app_config.JWT_ENABLE is False:
        middlewareList.remove(JwtMiddleware)

    middlewareList.reverse()
    # 遍历注册
    for _middleware in middlewareList:
        app.add_middleware(_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
