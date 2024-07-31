import time
from typing import Any

from app.errors import ImmediateException


def retry(ExceptionToCheck: Any, tries: int = 3, delay: int = 3, backoff: int = 2, logger: Any = None):
    """
    :param ExceptionToCheck: 需要捕获的异常
    :param tries: 重试次数
    :param delay: 延迟时间
    :param backoff: 延迟倍数
    :param logger: 日志对象
    """

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return f(*args, **kwargs)
                except ImmediateException:
                    raise
                except ExceptionToCheck as e:
                    msg = f"{str(e)}, {m_delay} 秒后重试 ..."
                    if logger:
                        logger.warn(msg)
                    else:
                        print(msg)
                    time.sleep(m_delay)
                    m_tries -= 1
                    m_delay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry
