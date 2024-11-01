from app.helper.qbittorrent_helper import QBittorrentHelper
from app.service.downloader_service import DownloaderService
from app.service.subscribe_service import SubscribeService


class TransferJob:

    def do_transfer(self):
        untransfer_list = SubscribeService.get_all_untransfer_history()
        for untransfer in untransfer_list:
            torrent_hash = untransfer.torrent_hash
            downloader = DownloaderService.get_downloader_by_id(untransfer.downloader_id)
            torrent_info = QBittorrentHelper(downloader).get_torrent_by_hash(torrent_hash)
            print(torrent_info)
