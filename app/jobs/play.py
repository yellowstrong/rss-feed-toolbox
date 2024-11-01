import json
import logging
import math
import threading
from typing import Any, Optional

from app.config.app_config import app_config
from app.helper.qbittorrent_helper import QBittorrentHelper
from app.helper.redis_helper import RedisHelper
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
            return
        with self.lock:
            try:
                self.is_running = True
                if not app_config.EMBY_HOST and not app_config.EMBY_API_KEY:
                    logging.error('未配置EMBY服务...')
                    return
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
                    limit_bitrate = 26214400
                    if total_bitrate > 0:
                        limit_bitrate = limit_bitrate - total_bitrate
                    if limit_bitrate < 819200:
                        limit_bitrate = 819200
                    limit_bytes = math.trunc(limit_bitrate / 8)
                    downloaders = DownloaderService.get_downloaders_for_speed_limit()
                    message = ''
                    send_message_flag = False
                    for downloader in downloaders:
                        up, dw = QBittorrentHelper(downloader).get_transfer_limit()
                        if math.trunc(up / 1024) != math.trunc(limit_bytes / 1024) and total_bitrate != 0:
                            QBittorrentHelper(downloader).set_transfer_limit(limit_bytes, 0)
                            message += f'{downloader.name} 限速 {math.trunc(limit_bytes / 1024)} kb/s\n'
                            send_message_flag = True
                        elif math.trunc(up / 1024) != math.trunc(limit_bytes / 1024) and total_bitrate == 0:
                            QBittorrentHelper(downloader).set_transfer_limit(limit_bytes, 0)
                            message += f'{downloader.name} 限速 {math.trunc(limit_bytes / 1024)} kb/s\n'
                            send_message_flag = True
                    if send_message_flag:
                        TelegramHelper().send_msg(title='下载器限速', text=message)
            finally:
                self.is_running = False

    def play_notify(self, json_data: Any):
        event_type = json_data.get('Event', '')
        if event_type in self.events:
            redis = RedisHelper()
            session_id = json_data.get('Session', '')['Id'] or ''
            latest_request = redis.get(session_id)
            if latest_request:
                old_event_type = latest_request.get('event_type', '')
                if event_type == old_event_type:
                    return
            media_type = json_data.get('Item', '').get('Type', '') or ''
            media_id = json_data.get('Item', '').get('SeriesId', '') or '' \
                if media_type == 'Episode' else json_data.get('Item', '').get('Id', '') or ''
            media_name = json_data.get('Item', '').get('SeriesName', '') or '' \
                if media_type == 'Episode' else json_data.get('Item', '').get('Name', '') or ''
            media_year = json_data.get('Item', '').get('ProductionYear', '') or ''
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
            if media_type == 'Episode':
                title += f" 剧集 {media_name}"
            elif media_type == 'Movie':
                title += f" 电影 {media_name} ({media_year})"
            subject = f"摘要: {json_data.get('Item', '').get('Name', '') or ''}"
            user = f"用户: {json_data.get('User', '').get('Name', '') or ''}"
            device = f"设备: {json_data.get('Session', '').get('DeviceName', '') or ''}"
            client = f"应用: {json_data.get('Session', '').get('Client', '') or ''}"
            address = f"地址: {json_data.get('Session', '').get('RemoteEndPoint', '') or ''}"
            summary = f"剧情: {json_data.get('Item', '').get('Overview', '') or ''}"
            session_event_type = {
                "event_type": event_type,
            }
            redis.set(session_id, session_event_type)
            msg_content = f'{subject}\n{user}\n{device}\n{client}\n{address}\n{summary}'
            msg_img = None
            emby_media_images = f'{app_config.EMBY_HOST}/Items/{media_id}/Images?api_key={app_config.EMBY_API_KEY}'
            emby_backdrop_flag = False
            res = RequestHelper().get_res(url=emby_media_images)
            if res and res.status_code == 200:
                res_json = json.loads(res.content)
                for item in res_json:
                    if item.get('ImageType') == 'Backdrop':
                        msg_img = f'{app_config.EMBY_HOST}/Items/{media_id}/Images/Backdrop?api_key={app_config.EMBY_API_KEY}'
                        emby_backdrop_flag = True
                        break
            if emby_backdrop_flag is False:
                msg_img = self.get_backdrop(media_type, media_name, media_year)
            TelegramHelper().send_msg(title=title,
                                      text=msg_content,
                                      image=msg_img if msg_img is not None else 'https://ice.frostsky.com/2024/07/31/1e010b9c44aef058046f9808bf09cad4.png')
        self.polling_session()

    @staticmethod
    def get_backdrop(type: str, name: str, year: int) -> Optional[str]:
        req_url = app_config.TMDB_API_URL
        if type == 'Episode':
            req_url += '/3/search/tv'
        elif type == 'Movie':
            req_url += '/3/search/movie'
        req_params = {
            'api_key': app_config.TMDB_API_KEY,
            'language': 'zh',
            'query': name,
        }
        if type == 'Movie':
            req_params.update({'year': year})
        res = RequestHelper().get_res(url=req_url, params=req_params)
        if res and res.status_code == 200:
            res_json = json.loads(res.content)
            results = res_json.get('results', [])
            if len(results) > 0:
                backdrop_path = results[0].get('backdrop_path', None)
                if backdrop_path:
                    return f'{app_config.TMDB_IMG_URL}/t/p/original{backdrop_path}'
                else:
                    return None
            else:
                return None
        return None
