import uvicorn
from app.bootstrap.initialize import register_app
from app.config.app_config import app_config

app = register_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host=app_config.HOST, port=app_config.PORT)
