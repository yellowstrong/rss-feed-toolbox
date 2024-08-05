from typing import Tuple

from sqlalchemy.orm import Session

from app.models import Downloader


class DownloaderDao:

    @staticmethod
    def get_downloaders(session: Session, current: int, page_size: int) -> Tuple[int, list[Downloader]]:
        query = session.query(Downloader)
        total = query.count()
        offset = (current - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = query.all()
        return total, result

    @staticmethod
    def get_downloaders_for_speed_limit(session: Session) -> list[Downloader]:
        query = session.query(Downloader)
        result = query.all()
        return result

    @staticmethod
    def get_downloader_by_id(session, id: int) -> Downloader:
        query = session.query(Downloader).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def get_default_downloader(session: Session) -> Downloader:
        query = session.query(Downloader).filter_by(default=True)
        result = query.first()
        return result

    @staticmethod
    def add_downloader(session, downloader: Downloader):
        session.add(downloader)

    @staticmethod
    def update_downloader(session, downloader: Downloader):
        session.merge(downloader)

    @staticmethod
    def set_default_downloader(session, id: int):
        session.query(Downloader).update({'default': None})
        session.flush()
        session.query(Downloader).filter_by(id=id).update({'default': True})

    @staticmethod
    def delete_downloader(session, downloader: Downloader):
        session.delete(downloader)
