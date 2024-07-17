from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.subscribe import Subscribe
from app.models.download_history import DownloadHistory


class SubscribeDao:

    @staticmethod
    def add_subscribe(session: Session, subscribe: Subscribe):
        session.add(subscribe)

    @staticmethod
    def get_subscribes(session: Session, page: int = 1, page_size: int = 10) -> (int, list[Subscribe]):
        query = session.query(Subscribe)
        total = query.count()
        offset = (page - 1) * page_size
        query = query.order_by(desc(Subscribe.id)).offset(offset).limit(page_size)
        result = query.all()
        return total, result

    @staticmethod
    def get_active_subscribes(session: Session) -> list[Subscribe]:
        query = session.query(Subscribe)
        result = query.all()
        return result

    @staticmethod
    def get_subscribe_by_id(session: Session, id: int) -> Subscribe:
        query = session.query(Subscribe).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def update_subscribe(session: Session, subscribe: Subscribe):
        session.merge(subscribe)

    @staticmethod
    def delete_subscribe(session: Session, subscribe: Subscribe):
        session.delete(subscribe)

    @staticmethod
    def get_download_history_by_subscribe_id(session: Session, subscribe_id: int) -> list[DownloadHistory]:
        query = session.query(DownloadHistory).filter_by(subscribe_id=subscribe_id)
        result = query.all()
        return result

    @staticmethod
    def add_download_history(session: Session, download_history: DownloadHistory):
        session.add(download_history)
