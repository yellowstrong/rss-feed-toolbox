import time
import traceback
from typing import Optional, Tuple
import qbittorrentapi

from app.helper.logger_helper import logger
from app.types.apiproto.downloader_proto import Downloader
from app.utils.str import StringUtil
from app.config.app_config import app_config


class QBittorrentHelper:
    _client = None

    def __init__(self, downloader: Downloader):
        self._client = qbittorrentapi.Client(
            host=downloader.host,
            port=downloader.port,
            username=downloader.username,
            password=downloader.password
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

    def delete_torrent(self, hash: str, delete_file=False) -> bool:
        try:
            self._client.torrents_delete(delete_files=delete_file, torrent_hashes=[hash])
            return True
        except Exception as err:
            logger.error(f'删除种子出错：{str(err)} - {traceback.format_exc()}')
            return False

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

    def get_transfer_limit(self) -> Tuple[int, int]:
        upload_limit = self._client.transfer_upload_limit()
        download_limit = self._client.transfer_download_limit()
        return upload_limit, download_limit

    def set_transfer_limit(self, upload_limit: int, download_limit: int) -> bool:
        self._client.transfer_set_upload_limit(upload_limit)
        self._client.transfer_set_download_limit(download_limit)
        return True


if __name__ == '__main__':
    torrent = QBittorrentHelper(Downloader(name='test', host='192.168.100.26', port=8080, username='admin',
                                           password='hq1998130')).set_transfer_limit(1,1)
    print(torrent)
