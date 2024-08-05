import json
import math
import threading
from typing import Any

from app.config.app_config import app_config
from app.helper.qbittorrent_helper import QBittorrentHelper
from app.helper.redis_helper import redis_client
from app.helper.request_helper import RequestHelper
from app.helper.telegram_helper import TelegramHelper
from app.service.downloader_service import DownloaderService


class PlayJob:
    limit_url = ['192.168.100.2', '192.168.100.8']
    events = ["playback.start", "playback.unpause", "playback.pause", "playback.stop"]

    def __init__(self):
        self.lock = threading.Lock()
        self.is_running = False

    def polling_session(self):
        if self.lock.locked():
            print("任务正在执行中...")
            return
        with self.lock:
            try:
                self.is_running = True
                print("任务执行开始")
                req_url = f'{app_config.EMBY_HOST}/emby/Sessions?api_key={app_config.EMBY_API_KEY}'
                res = RequestHelper().get_res(req_url)
                if res and res.status_code == 200:
                    total_bitrate = 0
                    sessions = res.json()
                    for session in sessions:
                        if session.get('RemoteEndPoint', '') in self.limit_url:
                            if session.get('PlayState', {}).get('IsPaused', '') is not True:
                                bitrate = session.get('NowPlayingItem', {}).get('Bitrate', 0)
                                total_bitrate += bitrate
                    if total_bitrate == 0:
                        limit = 3276800
                    else:
                        limit = math.trunc((32000000 - total_bitrate) / 8)
                    if limit < 102400:
                        limit = 102400
                    if limit > 3276800:
                        limit = 3276800
                    downloaders = DownloaderService.get_downloaders_for_speed_limit()
                    message = ''
                    send_message_flag = False
                    for downloader in downloaders:
                        up, dw = QBittorrentHelper(downloader).get_transfer_limit()
                        if math.trunc(up / 1024) != math.trunc(limit / 1024) and total_bitrate != 0:
                            QBittorrentHelper(downloader).set_transfer_limit(limit, 0)
                            message += f'{downloader.name} 限速 {math.trunc(limit / 1024)} Kb/s\n'
                            send_message_flag = True
                        elif math.trunc(up / 1024) != math.trunc(limit / 1024) and total_bitrate == 0:
                            QBittorrentHelper(downloader).set_transfer_limit(limit, 0)
                            message += f'{downloader.name} 限速 {math.trunc(limit / 1024)} Kb/s\n'
                            send_message_flag = True
                    if send_message_flag:
                        TelegramHelper().send_msg(title='下载器限速', text=message)
            finally:
                self.is_running = False
                print("任务执行结束")

    def play_notify(self, json_data: Any):
        event_type = json_data.get('Event', '')
        if event_type in self.events:
            session_id = json_data.get('Session', '')['Id'] or ''
            latest_request = redis_client.get(session_id)
            if latest_request:
                old_event_type = eval(latest_request).get('event_type', '')
                if event_type == old_event_type:
                    return
            title = ''
            match event_type:
                case 'playback.start':
                    title += '开始播放'
                case 'playback.pause':
                    title += '暂停播放'
                case 'playback.unpause':
                    title += '恢复播放'
                case 'playback.stop':
                    title += '停止播放'
            media_type = json_data.get('Item', '').get('Type', '') or ''
            if media_type == 'Episode':
                title += f" 剧集 {json_data.get('Item', '').get('SeriesName', '') or ''}"
            elif media_type == 'Movie':
                title += f" 电影 {json_data.get('Item', '').get('Name', '') or ''} ({json_data.get('Item', '').get('ProductionYear', '') or ''})"
            subject = f"摘要: {json_data.get('Item', '').get('Name', '') or ''}"
            user = f"用户: {json_data.get('User', '').get('Name', '') or ''}"
            device = f"设备: {json_data.get('Session', '').get('DeviceName', '') or ''}"
            client = f"应用: {json_data.get('Session', '').get('Client', '') or ''}"
            address = f"地址: {json_data.get('Session', '').get('RemoteEndPoint', '') or ''}"
            summary = f"剧情: {json_data.get('Item', '').get('Overview', '') or ''}"
            session_event_type = {
                "event_type": event_type,
            }
            redis_client.set(session_id, json.dumps(session_event_type))
            msg_content = f'{subject}\n{user}\n{device}\n{client}\n{address}\n{summary}'
            TelegramHelper().send_msg(title=title,
                                      text=msg_content,
                                      image='https://ice.frostsky.com/2024/07/31/1e010b9c44aef058046f9808bf09cad4.png')
        self.polling_session()
