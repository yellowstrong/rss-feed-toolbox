import logging
from typing import Optional

from app.dao.downloader_dao import DownloaderDao
from app.errors import BizError
from app.types import apiproto
from app import models
from app.helper.database_helper import get_database_session


class DownloaderService:
    @staticmethod
    def get_downloaders(query: apiproto.BaseQuery) -> apiproto.BasePaginationList:
        with get_database_session() as session:
            total, result = DownloaderDao.get_downloaders(session, query.current, query.pageSize)
            if total == 0:
                return apiproto.BasePaginationList()
            records_list: list[apiproto.Downloader] = []
            for record in result:
                tmp = apiproto.Downloader(
                    id=record.id,
                    name=record.name,
                    host=record.host,
                    port=record.port,
                    username=record.username,
                    password=record.password,
                    default=record.default,
                )
                records_list.append(tmp)
        return apiproto.BasePaginationList(record_total=total, record_list=records_list)

    @staticmethod
    def get_downloaders_for_speed_limit() -> list[apiproto.Downloader]:
        with get_database_session() as session:
            downloaders = DownloaderDao.get_downloaders_for_speed_limit(session)
            return [apiproto.Downloader(
                name=downloader.name,
                host=downloader.host,
                port=downloader.port,
                username=downloader.username,
                password=downloader.password,
            ) for downloader in downloaders]

    @staticmethod
    def get_downloader_by_id(id: int) -> apiproto.Downloader:
        with get_database_session() as session:
            result = DownloaderDao.get_downloader_by_id(session, id)
            if result is None:
                raise BizError('下载器不存在')
            return apiproto.Downloader(
                id=result.id,
                name=result.name,
                host=result.host,
                port=result.port,
                username=result.username,
                password=result.password,
                default=result.default,
            )

    @staticmethod
    def get_default_downloader() -> Optional[apiproto.Downloader]:
        with get_database_session() as session:
            result = DownloaderDao.get_default_downloader(session)
            if result is None:
                logging.error('未设置默认下载器，请先设置默认下载器...')
                return None
            return apiproto.Downloader(
                name=result.name,
                host=result.host,
                port=result.port,
                username=result.username,
                password=result.password,
            )

    @staticmethod
    def add_downloader(downloader: apiproto.Downloader):
        with get_database_session() as session:
            downloader_model = models.Downloader(
                name=downloader.name,
                host=downloader.host,
                port=downloader.port,
                username=downloader.username,
                password=downloader.password,
            )
            DownloaderDao.add_downloader(session, downloader_model)

    @staticmethod
    def update_downloader(downloader: apiproto.Downloader):
        with get_database_session() as session:
            downloader_model = DownloaderDao.get_downloader_by_id(session, downloader.id)
            if downloader_model is None:
                raise BizError('下载器不存在')
            downloader_model.name = downloader.name
            downloader_model.host = downloader.host
            downloader_model.port = downloader.port
            downloader_model.username = downloader.username
            downloader_model.password = downloader.password
            DownloaderDao.update_downloader(session, downloader_model)

    @staticmethod
    def set_default_downloader(id: int):
        with get_database_session() as session:
            DownloaderDao.set_default_downloader(session, id)

    @staticmethod
    def delete_downloader(id: int):
        with get_database_session() as session:
            downloader_model = DownloaderDao.get_downloader_by_id(session, id)
            if downloader_model is None:
                raise BizError('下载器不存在')
            elif downloader_model.default:
                raise BizError('默认下载器不可删除')
            DownloaderDao.delete_downloader(session, downloader_model)
