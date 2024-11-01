import json
from typing import Optional, Any
import redis
from redis.exceptions import TimeoutError, AuthenticationError
from app.config.app_config import app_config
from app.helper.logger_helper import logger


class RedisHelper:
    _conn = None

    def __init__(self,
                 host: str = app_config.REDIS_HOST,
                 port: int = app_config.REDIS_PORT,
                 password: str = app_config.REDIS_PASSWORD,
                 db: int = app_config.REDIS_DB):
        if host and port:
            if not db:
                db = 0
            self._conn = redis.Redis(host=host, port=port, password=password, db=db)
        else:
            logger.warn('Redis未配置...')

    def delete(self, key: str):
        self._execute_redis_operation(lambda: self._conn.delete(key))

    def set_string(self, key: str, value: str, ex: int = None):
        self._execute_redis_operation(lambda: self._conn.set(key, value, ex))

    def get_string(self, key: str) -> Optional[str]:
        return self._execute_redis_operation(lambda: self._conn.get(key))

    def set(self, key: str, value: Any, ex=None):
        self._execute_redis_operation(lambda: self._conn.set(key, json.dumps(value), ex))

    def get(self, key: str) -> Any:
        value = self._execute_redis_operation(lambda: self._conn.get(key))
        if value:
            return json.loads(str(value, 'utf-8'))
        else:
            return None

    def expire(self, key: str, ex: int):
        self._execute_redis_operation(lambda: self._conn.expire(key, ex))

    def _execute_redis_operation(self, operation):
        try:
            if self._conn:
                return operation()
            else:
                logger.warn('操作失败，Redis未配置...')
        except Exception as e:
            self._handle_redis_exception(e)

    @staticmethod
    def _handle_redis_exception(exception):
        if isinstance(exception, TimeoutError):
            logger.error('数据库 redis 连接超时')
        elif isinstance(exception, AuthenticationError):
            logger.error('数据库 redis 连接认证失败')
        else:
            logger.error('数据库 redis 连接异常 {}', exception)
