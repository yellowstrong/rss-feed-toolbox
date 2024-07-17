import hashlib
from datetime import datetime
import random
from typing import Any, Optional
import string
import dateutil.parser


class StringUtil:
    """
    字符串工具类
    """

    @staticmethod
    def generate_md5(data: str) -> str:
        """
        生成MD5
        :param data:
        :return:
        """
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode('utf-8'))
        return md5_hash.hexdigest()

    @staticmethod
    def get_time(date: Any) -> Optional[datetime]:
        try:
            return dateutil.parser.parse(date)
        except dateutil.parser.ParserError:
            return None

    @staticmethod
    def alphanumeric_random(length: int = 16) -> str:
        """
        生成指定长度的字母和数字的随机字符串
        """
        str_list = [random.choice(string.ascii_letters + string.digits) for i in range(length)]
        return ''.join(str_list)
