import logging
import time
import traceback
from typing import Tuple, Optional
import qbittorrentapi

from app.helper.logger_helper import logger
from app.utils.singleton import Singleton
from app.utils.str import StringUtil
from app.config.app_config import app_config


class QBittorrentHelper(metaclass=Singleton):
    _client = None

    def __init__(self):
        self._client = qbittorrentapi.Client(
            host=app_config.QB_HOST,
            port=app_config.QB_PORT,
            username=app_config.QB_USERNAME,
            password=app_config.QB_PASSWORD
        )

    def add_torrent(self, torrent: bytes) -> Optional[str]:
        tmp_tag = StringUtil.alphanumeric_random(8)
        try:
            res = self._client.torrents_add(torrent_files=[torrent], tags=[tmp_tag, app_config.QB_TAG])
            if 'Ok' in res:
                torrents = self.get_torrent_by_tags(tmp_tag)
                torrent_hash = torrents[0].get('hash')
                self._client.torrents_delete_tags(torrent_hashes=[torrent_hash], tags=[tmp_tag])
                return torrent_hash
            else:
                logger.error(f'添加种子出错：{res}')
                return None
        except Exception as err:
            logger.error(f"添加种子出错：{str(err)} - {traceback.format_exc()}")
            return None

    def get_torrent_by_tags(self, tag: str):
        torrents = []
        for i in range(1, 3):
            time.sleep(3)
            results = self._client.torrents_info(tag=tag)
            if len(results) > 0:
                torrents.extend(results)
                break
        return torrents

    def get_torrent_by_hash(self, torrent_hash: str):
        return self._client.torrents_info(torrent_hashes=[torrent_hash])


if __name__ == '__main__':
    torrent = QBittorrentHelper().get_torrent_by_hash('5a5419741103fd4b430786f2ef71c7c8a0728fc4')
    print(torrent)
