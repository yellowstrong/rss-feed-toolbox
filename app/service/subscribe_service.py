from typing import Optional

from app import models
from app.errors import BizError
from app.types import apiproto
from app.dao.subscribe_dao import SubscribeDao

from app.helper.database_helper import get_database_session


class SubscribeService:

    @staticmethod
    def get_subscribes(query: apiproto.SubscribeQuery) -> apiproto.SubscribeList:
        with get_database_session() as session:
            total, result = SubscribeDao.get_subscribes(session, query.page, query.page_size)
            if total == 0:
                return apiproto.SubscribeList()
            record_list: list[apiproto.Subscribe] = []
            for record in result:
                tmp = apiproto.Subscribe(
                    id=record.id,
                    media_name=record.media_name,
                    media_tmdb_id=record.media_tmdb_id,
                    site_rss_id=record.site_rss_id,
                    match_title=record.match_title,
                    match_season=record.match_season,
                    match_team=record.match_team,
                    include=record.include,
                    exclude=record.exclude,
                    status=record.status,
                    rss=apiproto.SiteRss(
                        id=record.site_rss.id,
                        site_id=record.site_rss.site_id,
                        alias=record.site_rss.alias,
                        url=record.site_rss.url,
                        latest_pub=record.site_rss.latest_pub,
                    ),
                )
                record_list.append(tmp)
        return apiproto.SubscribeList(record_total=total, record_list=record_list)

    @staticmethod
    def get_subscribe_by_id(id: int) -> apiproto.Subscribe:
        with get_database_session() as session:
            result = SubscribeDao.get_subscribe_by_id(session, id)
            if result is None:
                raise BizError('订阅不存在')
            return apiproto.Subscribe(
                id=result.id,
                media_name=result.media_name,
                media_tmdb_id=result.media_tmdb_id,
                site_rss_id=result.site_rss_id,
                match_title=result.match_title,
                match_season=result.match_season,
                match_team=result.match_team,
                include=result.include,
                exclude=result.exclude,
                status=result.status,
                rss=apiproto.SiteRss(
                    id=result.site_rss.id,
                    site_id=result.site_rss.site_id,
                    alias=result.site_rss.alias,
                    url=result.site_rss.url,
                ),
            )

    @staticmethod
    def add_subscribe(subscribe: apiproto.Subscribe):
        with get_database_session() as session:
            subscribe_model = models.Subscribe(
                media_name=subscribe.media_name,
                media_tmdb_id=subscribe.media_tmdb_id,
                site_rss_id=subscribe.site_rss_id,
                match_title=subscribe.match_title,
                match_season=subscribe.match_season,
                match_team=subscribe.match_team,
                include=subscribe.include,
                exclude=subscribe.exclude,
                status=subscribe.status,
            )
            SubscribeDao.add_subscribe(session, subscribe_model)

    @staticmethod
    def update_subscribe(subscribe: apiproto.Subscribe):
        with get_database_session() as session:
            subscribe_model = SubscribeDao.get_subscribe_by_id(session, subscribe.id)
            if subscribe_model is None:
                raise BizError('订阅不存在')
            subscribe_model.media_name = subscribe.media_name
            subscribe_model.media_tmdb_id = subscribe.media_tmdb_id
            subscribe_model.site_rss_id = subscribe.site_rss_id
            subscribe_model.match_title = subscribe.match_title
            subscribe_model.match_season = subscribe.match_season
            subscribe_model.match_team = subscribe.match_team
            subscribe_model.include = subscribe.include
            subscribe_model.exclude = subscribe.exclude
            subscribe_model.status = subscribe.status
            SubscribeDao.update_subscribe(session, subscribe_model)

    @staticmethod
    def delete_subscribe(id: int):
        with get_database_session() as session:
            subscribe_model = SubscribeDao.get_subscribe_by_id(session, id)
            if subscribe_model is None:
                raise BizError('订阅不存在')
            SubscribeDao.delete_subscribe(session, subscribe_model)

    @staticmethod
    def get_active_subscribes() -> Optional[list[apiproto.Subscribe]]:
        with get_database_session() as session:
            result = SubscribeDao.get_active_subscribes(session)
            if len(result) == 0:
                return None
            return [apiproto.Subscribe(
                id=record.id,
                media_name=record.media_name,
                media_tmdb_id=record.media_tmdb_id,
                site_rss_id=record.site_rss_id,
                match_title=record.match_title,
                match_season=record.match_season,
                match_team=record.match_team,
                include=record.include,
                exclude=record.exclude,
                status=record.status,
                rss=apiproto.SiteRss(
                    id=record.site_rss.id,
                    site_id=record.site_rss.site_id,
                    alias=record.site_rss.alias,
                    url=record.site_rss.url,
                    latest_pub=record.site_rss.latest_pub
                )
            ) for record in result]

    @staticmethod
    def get_subscribe_history_by_subscribe_id(subscribe_id: int) -> Optional[list[apiproto.SubscribeHistory]]:
        with get_database_session() as session:
            result = SubscribeDao.get_subscribe_history_by_subscribe_id(session, subscribe_id)
            if result is None:
                return None
            return [apiproto.SubscribeHistory(
                id=record.id,
                subscribe_id=record.subscribe_id,
                rss_title=record.rss_title,
                rss_pubdate=record.rss_pubdate,
                downloader_id=record.downloader_id,
                torrent_hash=record.torrent_hash,
                torrent_file=record.torrent_file,
                create_at=record.create_at,
            ) for record in result]

    @staticmethod
    def add_subscribe_history(subscribe_history: apiproto.SubscribeHistory):
        with get_database_session() as session:
            history_model = models.SubscribeHistory(
                id=subscribe_history.id,
                subscribe_id=subscribe_history.subscribe_id,
                rss_title=subscribe_history.rss_title,
                rss_pubdate=subscribe_history.rss_pubdate,
                downloader_id=subscribe_history.downloader_id,
                torrent_hash=subscribe_history.torrent_hash,
                torrent_file=subscribe_history.torrent_file,
                create_at=subscribe_history.create_at,
            )
            SubscribeDao.add_subscribe_history(session, history_model)

    @staticmethod
    def delete_subscribe_history_by_id(id: int):
        with get_database_session() as session:
            exist = SubscribeDao.get_subscribe_history_by_id(session, id)
            if exist:
                exist.deleted = True
                SubscribeDao.delete_subscribe_history(session, exist)

    @staticmethod
    def get_all_untransfer_history() -> Optional[list[apiproto.SubscribeHistory]]:
        with get_database_session() as session:
            result = SubscribeDao.get_all_untransfer_history(session)
            if len(result) == 0:
                return []
            else:
                record_list: list[apiproto.SubscribeHistory] = []
                for record in result:
                    tmp = apiproto.SubscribeHistory(
                        id=record.id,
                        subscribe_id=record.subscribe_id,
                        rss_title=record.rss_title,
                        rss_pubdate=record.rss_pubdate,
                        downloader_id=record.downloader_id,
                        torrent_hash=record.torrent_hash,
                        torrent_file=record.torrent_file,
                        create_at=record.create_at,
                        subscribe=record.subscribe
                    )
                    record_list.append(tmp)
                return record_list
