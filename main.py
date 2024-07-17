from contextlib import asynccontextmanager

import uvicorn
from app.bootstrap import initialize
from app.config.app_config import app_config
from fastapi import FastAPI

from scheduler import Scheduler


@asynccontextmanager
async def lifespan(server: FastAPI):
    Scheduler()
    yield
    Scheduler().stop()


app = FastAPI(redoc_url=None, docs_url="/apidoc", title=app_config.NAME, lifespan=lifespan)
initialize.Init(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host=app_config.HOST, port=app_config.PORT)
