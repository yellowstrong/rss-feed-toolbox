from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

from app.helper.system_helper import SystemHelper


class AppConfigSettings(BaseSettings):
    """应用配置"""

    """基础配置"""
    NAME: str = "RSS-Feed-Toolbox"
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True
    """jwt配置"""
    JWT_ENABLE: bool = True
    JWT_SECRET_KEY: str = "YDZre6YJOx9UMec"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRED: int = 30
    JWT_ISS: str = "iOk7a1aUf9XPHtW"
    JWT_NO_CHECK_URIS: str = "/auth/register,/auth/login,/apidoc,/openapi.json"
    """数据库配置"""
    DB_URL: str = "sqlite:///database.db"
    DB_ECHO_SQL: bool = False
    """订阅配置"""
    SUBSCRIBE_INTERVAL: int = 15
    """网络配置"""
    PROXY_HOST: Optional[str] = None
    """路径配置"""
    CONFIG_DIR: Optional[str] = None
    """下载器"""
    QB_HOST: str = "192.168.100.26"
    QB_PORT: int = 8080
    QB_USERNAME: str = "admin"
    QB_PASSWORD: str = "hq1998130"
    QB_TAG: str = "RSS-Feed-Toolbox"
    """消息通知"""
    TELEGRAM_BOT_TOKEN: str = '6680266790:AAF9nuP5PP8msGISqYxKxzTkQVCnI6RXkZs'
    TELEGRAM_CHAT_ID: str = '677469093'

    @property
    def PROXY(self):
        if self.PROXY_HOST:
            return {
                "http": self.PROXY_HOST,
                "https": self.PROXY_HOST,
            }
        return None

    @property
    def ROOT_PATH(self):
        return Path(__file__).parents[2]

    @property
    def CONFIG_PATH(self):
        if self.CONFIG_DIR:
            return Path(self.CONFIG_DIR)
        elif SystemHelper.is_docker():
            return Path("/config")
        return self.ROOT_PATH / "config"

    @property
    def TEMP_PATH(self):
        return self.CONFIG_PATH / "temp"

    @property
    def LOG_PATH(self):
        return self.CONFIG_PATH / "logs"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.CONFIG_PATH as p:
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
        with self.TEMP_PATH as p:
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
        with self.LOG_PATH as p:
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)

    class Config:
        env_prefix = 'APP_'
        env_file = ".env"
        env_file_encoding = 'utf-8'


app_config = AppConfigSettings()
