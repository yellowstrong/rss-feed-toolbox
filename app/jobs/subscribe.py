import os
import re
from pathlib import Path
from urllib.parse import unquote

from requests import Response
from typing import Optional, Tuple
from datetime import datetime
from cachetools import cached, TTLCache
from torrentool.torrent import Torrent

from app.config.app_config import app_config
from app.helper.request_helper import RequestHelper
from app.helper.telegram_helper import TelegramHelper
from app.service.downloader_service import DownloaderService
from app.service.site_service import SiteService
from app.service.subscribe_service import SubscribeService
from app.types import apiproto
from app import types
from app.helper.logger_helper import logger
from app.helper.rss_helper import RssHelper
from app.constant.subscription_rule import SubscriptionRule
from app.helper.qbittorrent_helper import QBittorrentHelper


class SubscribeJob:

    def refresh(self):
        subscribe, site_rss = self.get_active_subscribe()
        if site_rss is None:
            return
        torrents_cache = {}
        for item in site_rss:
            site = SiteService.get_site_by_id(item.site_id)
            torrents: list[types.TorrentInfo] = self.rss(item.url, site.cookie, site.user_agent)
            if torrents:
                torrents = [torrent for torrent in torrents if
                            item.latest_pub is None or torrent.pubdate.replace(tzinfo=None) > item.latest_pub]
                if torrents:
                    logger.info(f'{item.url} 有 {len(torrents)} 个新种子')
                    torrents_cache[item.id] = torrents
                    new_latest_pub = max((torrent.pubdate for torrent in torrents if torrent.pubdate is not None),
                                         default=None)
                    SiteService.update_rss_latest_pub(item.id, new_latest_pub)
                else:
                    logger.info(f'{item.url} 没有新种子')
                    continue
            else:
                logger.info(f'{item.url} 没有获取到种子')
        if torrents_cache:
            self.match(subscribe, torrents_cache)

    def match(self, subscribes: list[apiproto.Subscribe], torrents: dict[int, list[types.TorrentInfo]]):
        downloader = DownloaderService.get_default_downloader()
        if downloader is None:
            return
        qbittorrent = QBittorrentHelper(downloader)
        telegram = TelegramHelper()
        for subscribe in subscribes:
            logger.info(f'开始匹配订阅，标题：{subscribe.name} ...')
            sub_torrents = torrents.get(subscribe.site_rss_id) or []
            if len(sub_torrents) > 0:
                logger.debug(f'开始匹配订阅RSS：{subscribe.rss.alias}，本次新种子共计 {len(sub_torrents)} 个...')
                includes = subscribe.include.split(',')
                excludes = subscribe.exclude.split(',')
                for t in sub_torrents:
                    if not re.search(r'%s' % subscribe.match_title, t.title, re.I):
                        logger.info(f'种子标题：{t.title}，不符合匹配标题，排除...')
                        continue
                    if subscribe.match_season and not re.search(r'%s' % subscribe.match_season, t.title, re.I):
                        logger.info(f'种子标题：{t.title}，不符合匹配季，排除...')
                        continue
                    if subscribe.match_team and not re.search(r'%s' % subscribe.match_team, t.title, re.I):
                        logger.info(f'种子标题：{t.title}，不符合制作组，排除...')
                        continue
                    _match = SubscriptionRule.match_rule(t.title, includes, excludes)
                    if _match is False:
                        logger.info(f'种子标题：{t.title}，不符合过滤规则，排除...')
                        continue
                    logger.info(f'种子标题：{t.title}，匹配规则，开始下载...')

                    succeed, content, file_list, err_msg = self.download_torrent(t.enclosure, t.cookie, t.ua)
                    if not succeed:
                        logger.error(f'下载种子出错：{err_msg} - {content}')
                    else:
                        tmp = []
                        for file in file_list:
                            file_base, file_extension = os.path.splitext(file)
                            if file_extension in app_config.RMT_MEDIA_EXT:
                                tmp.append(file)
                        file_list = tmp
                        histories = SubscribeService.get_download_history_by_subscribe_id(subscribe.id)
                        for history in histories:
                            if history.torrent_list == ','.join(file_list):
                                logger.warn(f'检测到相同文件种子：{t.title}，删除原有种子：{history.torrent_hash}')
                                succeed = qbittorrent.delete_torrent(history.torrent_hash)
                                if succeed:
                                    logger.info(f'删除种子：{history.torrent_hash} 成功')
                                    SubscribeService.delete_download_history_by_id(history.id)
                        download_hash = qbittorrent.add_torrent(content)
                        if download_hash:
                            SubscribeService.add_download_history(apiproto.DownloadHistory(
                                subscribe_id=subscribe.id,
                                rss_title=t.title,
                                rss_guid=t.guid,
                                torrent_hash=download_hash,
                                torrent_list=','.join(file_list),
                                create_at=datetime.now()
                            ))
                            logger.info(f'种子：{t.title}，下载成功')
                            telegram.send_msg(title='开始下载', text=f'{t.title}')
                        else:
                            telegram.send_msg(title='下载出错', text=f'{t.title}')

    def download_torrent(self, enclosure: str, cookie: str = None, ua: str = None) -> \
            Tuple[bool, Optional[str | bytes], Optional[list[str]], Optional[str]]:
        """
        :return: 成功状态、种子内容、种子文件列表、错误原因
        """
        response = RequestHelper(cookies=cookie, ua=ua).get_res(enclosure, allow_redirects=False)
        while response.status_code in [301, 302]:
            req_url = response.headers['Location']
            response = RequestHelper(cookies=cookie, ua=ua).get_res(req_url, allow_redirects=False)
        if response and response.status_code == 200:
            if not response.content:
                return False, None, None, '未下载到任何数据'
            else:
                if 'x-bittorrent' in response.headers.get(
                        'Content-Type').lower() or 'octet-stream' in response.headers.get('Content-Type').lower():
                    file_name = self.get_url_filename(response, enclosure)
                    file_path = Path(app_config.TEMP_PATH) / file_name
                    file_path.write_bytes(response.content)
                    folder_name, file_list = self.get_torrent_info(file_path)
                    return True, response.content, file_list, None
                else:
                    if 'text' in response.headers.get('Content-Type') or 'json' in response.headers.get('Content-Type'):
                        return False, response.content.decode('utf-8'), None, '下载出错，未下载到种子'
                    else:
                        return False, None, None, '下载出错，未下载到种子'
        elif response is None:
            return False, None, None, '无法打开链接'
        elif response.status_code == 429:
            return False, None, None, '触发站点流控，请稍后再试'
        else:
            return False, None, None, f'下载种子出错，状态码：{response.status_code}'

    @staticmethod
    def get_torrent_info(torrent_path: Path) -> Tuple[str, list[str]]:
        if not torrent_path or not torrent_path.exists():
            return "", []
        try:
            torrent_info = Torrent.from_file(torrent_path)
            if (not torrent_info.files
                    or (len(torrent_info.files) == 1
                        and torrent_info.files[0].name == torrent_info.name)):
                folder_name = ""
                file_list = [torrent_info.name]
            else:
                folder_name = torrent_info.name
                file_list = []
                for file_info in torrent_info.files:
                    file_path = Path(file_info.name)
                    root_path = file_path.parts[0]
                    if root_path == folder_name:
                        file_list.append(str(file_path.relative_to(root_path)))
                    else:
                        file_list.append(file_info.name)
            logger.debug(f"解析种子：{torrent_path.name} => 目录：{folder_name}，文件清单：{file_list}")
            return folder_name, file_list
        except Exception as err:
            logger.error(f"种子文件解析失败：{str(err)}")
            return "", []

    @staticmethod
    def get_url_filename(response: Response, url: str) -> str:
        """获取种子文件名"""
        if not response:
            return ""
        disposition = response.headers.get('content-disposition') or ""
        file_name = re.findall(r"filename=\"?(.+)\"?", disposition)
        if file_name:
            file_name = unquote(str(file_name[0].encode('ISO-8859-1').decode()).split(";")[0].strip())
            if file_name.endswith('"'):
                file_name = file_name[:-1]
        elif url and url.endswith(".torrent"):
            file_name = unquote(url.split("/")[-1])
        else:
            file_name = str(datetime.now())
        return file_name

    @staticmethod
    def get_active_subscribe() -> tuple[Optional[list[apiproto.Subscribe]], Optional[list[apiproto.SiteRss]]]:
        """获取活动订阅"""
        active_subscribe = SubscribeService.get_active_subscribes()
        if active_subscribe is None:
            return None, None
        site_rss = [item.rss for item in active_subscribe]
        site_rss = list(set(site_rss))
        return active_subscribe, site_rss

    @staticmethod
    @cached(cache=TTLCache(maxsize=128, ttl=295))
    def rss(url: str, cookie: str, ua: str) -> list[types.TorrentInfo]:
        """获取RSS"""
        logger.info(f'开始获取 {url} RSS ...')
        rss_items = RssHelper.parse(url)
        if rss_items is None:
            return []
        if not rss_items:
            logger.error(f'{url} 未获取到RSS数据！')
            return []
        ret_torrents: list[types.TorrentInfo] = []
        for item in rss_items:
            if not item.get("title"):
                continue
            torrent_info = types.TorrentInfo(
                title=item.get("title"),
                enclosure=item.get("enclosure"),
                page_url=item.get("link"),
                size=item.get("size"),
                guid=item.get("guid"),
                pubdate=item.get("pubdate") if item.get("pubdate") else None,
                cookie=cookie,
                ua=ua
            )
            ret_torrents.append(torrent_info)
        return ret_torrents
