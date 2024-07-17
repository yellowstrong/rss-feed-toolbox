import re
from typing import Optional, Tuple
from datetime import datetime
from cachetools import cached, TTLCache

from app.helper.request_helper import RequestHelper
from app.helper.telegram_helper import TelegramHelper
from app.service.site_service import SiteService
from app.service.subscribe_service import SubscribeService
from app.types import apiproto
from app import types
from app.helper.logger_helper import logger
from app.helper.rss_helper import RssHelper
from app.constant.subscription_rule import SubscriptionRule
from app.helper.qbittorrent_helper import QBittorrentHelper


class SubscribeJob:

    def __init__(self):
        self.qbittorrent_helper = QBittorrentHelper()
        self.telegram_helper = TelegramHelper()

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

                    succeed, content, err_msg = self.download_torrent(t.enclosure, t.cookie, t.ua)
                    if not succeed:
                        logger.error(f'下载种子出错：{err_msg} - {content}')
                    else:
                        download_hash = self.qbittorrent_helper.add_torrent(content)
                        if download_hash:
                            SubscribeService.add_download_history(apiproto.DownloadHistory(
                                subscribe_id=subscribe.id,
                                rss_title=t.title,
                                rss_guid=t.guid,
                                torrent_hash=download_hash,
                                create_at=datetime.now()
                            ))
                            logger.info(f'种子：{t.title}，下载成功')
                            self.telegram_helper.send_msg(title='开始下载', text=f'{t.title}')
                        else:
                            self.telegram_helper.send_msg(title='下载出错', text=f'{t.title}')

    @staticmethod
    def download_torrent(enclosure: str, cookie: str = None, ua: str = None) -> \
            Tuple[bool, Optional[str | bytes], Optional[str]]:
        """
        :return: 成功状态、种子内容、错误原因
        """
        response = RequestHelper(cookies=cookie, ua=ua).get_res(enclosure, allow_redirects=False)
        while response.status_code in [301, 302]:
            req_url = response.headers['Location']
            response = RequestHelper(cookies=cookie, ua=ua).get_res(req_url, allow_redirects=False)
        if response and response.status_code == 200:
            if not response.content:
                return False, None, '未下载到任何数据'
            else:
                if 'x-bittorrent' in response.headers.get(
                        'Content-Type').lower() or 'octet-stream' in response.headers.get('Content-Type').lower():
                    return True, response.content, None
                else:
                    if 'text' in response.headers.get('Content-Type') or 'json' in response.headers.get('Content-Type'):
                        return False, response.content.decode('utf-8'), '下载出错，未下载到种子'
                    else:
                        return False, None, '下载出错，未下载到种子'
        elif response is None:
            return False, None, '无法打开链接'
        elif response.status_code == 429:
            return False, None, '触发站点流控，请稍后再试'
        else:
            return False, None, f'下载种子出错，状态码：{response.status_code}'

    @staticmethod
    def get_active_subscribe() -> tuple[Optional[list[apiproto.Subscribe]], Optional[list[apiproto.SiteRss]]]:
        active_subscribe = SubscribeService.get_active_subscribes()
        if active_subscribe is None:
            return None, None
        site_rss = [item.rss for item in active_subscribe]
        site_rss = list(set(site_rss))
        return active_subscribe, site_rss

    @staticmethod
    @cached(cache=TTLCache(maxsize=128, ttl=295))
    def rss(url: str, cookie: str, ua: str) -> list[types.TorrentInfo]:
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
