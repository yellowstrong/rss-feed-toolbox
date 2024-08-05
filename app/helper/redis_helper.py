import sys

from redis.client import Redis
from redis.exceptions import AuthenticationError, TimeoutError

from app.config.app_config import app_config
from app.helper.logger_helper import logger


class RedisHelper(Redis):
    def __init__(self):
        super(RedisHelper, self).__init__(
            host=app_config.REDIS_HOST,
            port=app_config.REDIS_PORT,
            password=app_config.REDIS_PASSWORD,
            db=app_config.REDIS_DB,
            decode_responses=True,
        )

    def open(self):
        try:
            self.ping()
        except TimeoutError:
            logger.error('数据库 redis 连接超时')
            sys.exit()
        except AuthenticationError:
            logger.error('数据库 redis 连接认证失败')
            sys.exit()
        except Exception as e:
            logger.error('数据库 redis 连接异常 {}', e)
            sys.exit()

    def delete_prefix(self, prefix: str, exclude: str | list = None):
        keys = []
        for key in self.scan_iter(match=f'{prefix}*'):
            if isinstance(exclude, str):
                if key != exclude:
                    keys.append(key)
            elif isinstance(exclude, list):
                if key not in exclude:
                    keys.append(key)
            else:
                keys.append(key)
        for key in keys:
            self.delete(key)


redis_client = RedisHelper()
