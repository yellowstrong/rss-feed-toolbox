from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.errors import app_error, http_error, validation_error
from app import middleware
from app.controller import RegisterRouterList


def Init(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app_error.register_app_error_handle(app)
    http_error.register_http_error_handler(app)
    validation_error.register_validation_error_handler(app)
    middleware.registerMiddlewareHandle(app)
    for item in RegisterRouterList:
        app.include_router(item.router)
