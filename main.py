import uvicorn
from uvicorn import Config

from app.bootstrap.initialize import register_app
from app.config.app_config import app_config

app = register_app()

Server = uvicorn.Server(Config(app, host=app_config.HOST, port=app_config.PORT))


if __name__ == "__main__":
    try:
        Server.run()
    except KeyboardInterrupt:
        print("Server shutdown gracefully")