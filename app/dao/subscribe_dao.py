from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.subscribe import Subscribe
from app.models.subscribe_history import SubscribeHistory
from app.models.transfer_record import TransferRecord


class SubscribeDao:

    @staticmethod
    def get_subscribes(session: Session, page: int = 1, page_size: int = 10) -> (int, list[Subscribe]):
        query = session.query(Subscribe)
        total = query.count()
        offset = (page - 1) * page_size
        query = query.order_by(desc(Subscribe.id)).offset(offset).limit(page_size)
        result = query.all()
        return total, result

    @staticmethod
    def get_subscribe_by_id(session: Session, id: int) -> Subscribe:
        query = session.query(Subscribe).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def add_subscribe(session: Session, subscribe: Subscribe):
        session.add(subscribe)

    @staticmethod
    def update_subscribe(session: Session, subscribe: Subscribe):
        session.merge(subscribe)

    @staticmethod
    def delete_subscribe(session: Session, subscribe: Subscribe):
        session.delete(subscribe)

    @staticmethod
    def get_active_subscribes(session: Session) -> list[Subscribe]:
        query = session.query(Subscribe)
        result = query.all()
        return result

    @staticmethod
    def get_subscribe_history_by_subscribe_id(session: Session, subscribe_id: int) -> list[SubscribeHistory]:
        query = session.query(SubscribeHistory).filter(SubscribeHistory.subscribe_id == subscribe_id,
                                                       SubscribeHistory.deleted != True)
        result = query.all()
        return result

    @staticmethod
    def add_subscribe_history(session: Session, subscribe_history: SubscribeHistory):
        session.add(subscribe_history)

    @staticmethod
    def get_subscribe_history_by_id(session: Session, id: int):
        query = session.query(SubscribeHistory).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def delete_subscribe_history(session: Session, exist: SubscribeHistory):
        session.merge(exist)

    @staticmethod
    def get_all_untransfer_history(session: Session) -> list[SubscribeHistory]:
        query = (session.query(SubscribeHistory)
                 .outerjoin(TransferRecord, TransferRecord.subscribe_history_id == SubscribeHistory.id)
                 .filter(TransferRecord.id == None))
        result = query.all()
        return result
