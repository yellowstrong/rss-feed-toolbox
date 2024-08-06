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
    """jwt配置"""
    JWT_ENABLE: bool = True
    JWT_SECRET_KEY: str = "YDZre6YJOx9UMec"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRED: int = 60 * 24 * 8
    JWT_ISS: str = "iOk7a1aUf9XPHtW"
    JWT_NO_CHECK_URIS: str = "/auth/register,/auth/login,/apidoc,/openapi.json,/webhook/emby"
    """数据库配置"""
    DB_ECHO_SQL: bool = False
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: Optional[int] = None
    """调度配置"""
    SUBSCRIBE_INTERVAL: Optional[int] = None
    PLAY_LIMIT_INTERVAL: Optional[int] = None
    """网络配置"""
    PROXY_HOST: Optional[str] = None
    """路径配置"""
    CONFIG_DIR: Optional[str] = None
    """下载器"""
    QB_TAG: Optional[str] = None
    """消息通知"""
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[int] = None
    """媒体类型"""
    RMT_MEDIA_EXT: list = ['.mp4', '.mkv', '.ts', '.iso',
                           '.rmvb', '.avi', '.mov', '.mpeg',
                           '.mpg', '.wmv', '.3gp', '.asf',
                           '.m4v', '.flv', '.m2ts', '.strm',
                           '.tp', '.f4v']
    """媒体库"""
    EMBY_HOST: Optional[str] = None
    EMBY_API_KEY: Optional[str] = None
    LIMIT_IP: Optional[str] = None

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


app_config = AppConfigSettings(
    _env_file=AppConfigSettings().CONFIG_PATH / "app.env",
    _env_file_encoding="utf-8"
)
