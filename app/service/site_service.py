from datetime import datetime

from app.errors import BizError
from app.types import apiproto
from app import models
from app.helper.database_helper import get_database_session
from app.dao.site_dao import SiteDao


class SiteService:

    @staticmethod
    def get_sites(query: apiproto.SiteQuery) -> apiproto.SiteList:
        with get_database_session() as session:
            total, result = SiteDao.get_sites(session, query.current, query.pageSize)
            if total == 0:
                return apiproto.SiteList()
            records_list: list[apiproto.Site] = []
            for record in result:
                tmp = apiproto.Site(
                    id=record.id,
                    name=record.name,
                    url=record.url,
                    cookie=record.cookie,
                    time_out=record.time_out,
                    user_agent=record.user_agent,
                    site_rss=[apiproto.SiteRss(
                        id=rss_item.id,
                        site_id=rss_item.site_id,
                        alias=rss_item.alias,
                        url=rss_item.url,
                        latest_pub=rss_item.latest_pub,
                    ) for rss_item in record.site_rss],
                )
                records_list.append(tmp)
        return apiproto.SiteList(record_total=total, record_list=records_list)

    @staticmethod
    def get_site_by_id(id: int) -> apiproto.Site:
        with get_database_session() as session:
            result = SiteDao.get_site_by_id(session, id)
            if result is None:
                raise BizError('站点不存在')
            return apiproto.Site(
                id=result.id,
                name=result.name,
                url=result.url,
                cookie=result.cookie,
                time_out=result.time_out,
                user_agent=result.user_agent,
                site_rss=[apiproto.SiteRss(
                    id=rss_item.id,
                    site_id=rss_item.site_id,
                    alias=rss_item.alias,
                    url=rss_item.url,
                    latest_pub=rss_item.latest_pub
                ) for rss_item in result.site_rss]
            )

    @staticmethod
    def add_site(site: apiproto.Site):
        with get_database_session() as session:
            site_model = models.Site(
                name=site.name,
                url=site.url,
                cookie=site.cookie,
                time_out=site.time_out,
                user_agent=site.user_agent
            )
            site_rss_model = [models.SiteRss(alias=item.alias, url=item.url) for item in site.site_rss]
            SiteDao.add_site(session, site_model, site_rss_model)

    @staticmethod
    def update_site(site: apiproto.Site):
        with get_database_session() as session:
            site_model = SiteDao.get_site_by_id(session, site.id)
            if site_model is None:
                raise BizError('站点不存在')
            site_model.name = site.name
            site_model.url = site.url
            site_model.cookie = site.cookie
            site_model.time_out = site.time_out
            site_model.user_agent = site.user_agent
            site_rss_model = [models.SiteRss(
                id=item.id,
                site_id=item.site_id if item.site_id else site.id,
                alias=item.alias,
                url=item.url,
            ) for item in site.site_rss]
            SiteDao.update_site(session, site_model, site_rss_model)

    @staticmethod
    def delete_site(id: int):
        with get_database_session() as session:
            site = SiteDao.get_site_by_id(session, id)
            if site is None:
                raise BizError('站点不存在')
            SiteDao.delete_site(session, site)

    @staticmethod
    def get_site_rss(site_id: int = None) -> list[apiproto.SiteRss]:
        with get_database_session() as session:
            result = SiteDao.get_site_rss(session, site_id)
            return [apiproto.SiteRss(
                id=item.id,
                site_id=item.site_id,
                alias=item.alias,
                url=item.url,
                latest_pub=item.latest_pub,
            ) for item in result]

    @staticmethod
    def update_rss_latest_pub(site_rss_id: int, latest_pub: datetime):
        with get_database_session() as session:
            site_rss_model = SiteDao.get_site_rss_by_id(session, site_rss_id)
            site_rss_model.latest_pub = latest_pub
            SiteDao.update_rss_latest_pub(session, site_rss_model)
