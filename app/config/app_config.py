from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

from app.helper.system_helper import SystemHelper


class AppConfigSettings(BaseSettings):
    """应用配置"""

    """基础配置"""
    TITLE: str = "RSS-Feed-Toolbox"
    HOST: str = "localhost"
    PORT: int = 8000
    ENVIRONMENT: str = 'dev'
    DEBUG: bool = True
    DOCS_URL: str = '/apidoc'
    DATETIME_ZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | <lvl>{message}</>'
    LOG_STDOUT_FILENAME: str = 'fba_access.log'
    LOG_STDERR_FILENAME: str = 'fba_error.log'
    """jwt配置"""
    JWT_ENABLE: bool = True
    JWT_SECRET_KEY: str = "YDZre6YJOx9UMec"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRED: int = 30
    JWT_ISS: str = "iOk7a1aUf9XPHtW"
    JWT_NO_CHECK_URIS: str = "/auth/register,/auth/login,/apidoc,/openapi.json,/webhook/emby"
    """数据库配置"""
    DB_URL: str = "sqlite:///database.db"
    DB_ECHO_SQL: bool = False
    REDIS_HOST: str = '192.168.100.6'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DB: int = 0
    """调度配置"""
    SUBSCRIBE_INTERVAL: int = 15
    PLAY_LIMIT_INTERVAL: int = 5
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
    """媒体"""
    RMT_MEDIA_EXT: list = ['.mp4', '.mkv', '.ts', '.iso',
                           '.rmvb', '.avi', '.mov', '.mpeg',
                           '.mpg', '.wmv', '.3gp', '.asf',
                           '.m4v', '.flv', '.m2ts', '.strm',
                           '.tp', '.f4v']
    """媒体库"""
    EMBY_HOST: str = 'http://192.168.100.6:8096'
    EMBY_API_KEY: str = '39326b4d92e446fb9f14b0df94a794a5'

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
