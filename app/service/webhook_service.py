import json

from typing import Any

from app.helper.redis_helper import redis_client
from app.helper.telegram_helper import TelegramHelper


class WebhookService:

    def __init__(self):
        self.telegram_helper = TelegramHelper()

    limit_events = ["playback.start", "playback.unpause"]
    un_limit_events = ["playback.pause", "playback.stop"]

    def do_webhook(self, json_data: Any):
        event_type = json_data.get('Event', '')
        if event_type in self.limit_events or event_type in self.un_limit_events:
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
            media_type = json_data.get('Item', '')['Type'] or ''
            if media_type == 'Episode':
                title += f" 剧集 {json_data.get('Item', '')['SeriesName'] or ''}"
            elif media_type == 'Movie':
                title += f" 电影 {json_data.get('Item', '')['Name'] or ''} ({json_data.get('Item', '')['ProductionYear'] or ''})"
            subject = f"摘要: {json_data.get('Item', '')['Name'] or ''}"
            user = f"用户: {json_data.get('User', '')['Name'] or ''}"
            device = f"设备: {json_data.get('Session', '')['DeviceName'] or ''}"
            client = f"应用: {json_data.get('Session', '')['Client'] or ''}"
            address = f"地址: {json_data.get('Session', '')['RemoteEndPoint'] or ''}"
            summary = f"剧情: {json_data.get('Item', '')['Overview'] or ''}"
            session_event_type = {
                "event_type": event_type,
            }
            redis_client.set(session_id, json.dumps(session_event_type))
            msg_content = f'{subject}\n{user}\n{device}\n{client}\n{address}\n{summary}'
            self.telegram_helper.send_msg(title=title,
                                          text=msg_content,
                                          image='https://ice.frostsky.com/2024/07/31/1e010b9c44aef058046f9808bf09cad4.png')
