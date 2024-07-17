from typing import Optional

import telebot

from app.config.app_config import app_config
from app.helper.logger_helper import logger
from app.utils.retry import retry
from app.utils.singleton import Singleton


class TelegramHelper(metaclass=Singleton):

    def __init__(self):
        self._telegram_token = app_config.TELEGRAM_BOT_TOKEN
        self._telegram_chat_id = app_config.TELEGRAM_CHAT_ID
        if self._telegram_token and self._telegram_chat_id:
            self._bot = telebot.TeleBot(self._telegram_token, parse_mode="Markdown")

    def send_msg(self, title: str = "", text: str = "") -> Optional[bool]:

        if not self._telegram_token or not self._telegram_chat_id:
            return False

        if not title:
            logger.warn("标题不能为空")
            return False

        try:
            if text:
                caption = f"*{title}*\n{text}"
            else:
                caption = f"*{title}*"

            chat_id = self._telegram_chat_id

            return self.__send_request(userid=chat_id, caption=caption)

        except Exception as msg_e:
            logger.error(f"发送消息失败：{msg_e}")
            return False

    @retry(Exception, logger=logger)
    def __send_request(self, userid: str, caption="") -> bool:
        ret = None
        if len(caption) > 4095:
            for i in range(0, len(caption), 4095):
                ret = self._bot.send_message(chat_id=userid or self._telegram_chat_id,
                                             text=caption[i:i + 4095],
                                             parse_mode="Markdown")
        else:
            ret = self._bot.send_message(chat_id=userid or self._telegram_chat_id,
                                         text=caption,
                                         parse_mode="Markdown")
        if ret is None:
            raise Exception("发送文本消息失败")
        return True if ret else False
