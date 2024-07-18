from sqlalchemy.orm import Session
from app.models import User


class UserDao:

    @staticmethod
    def create_user(session: Session, user: User):
        session.add(user)

    @staticmethod
    def get_user_by_id(session: Session, id: int):
        query = session.query(User).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def get_user_by_username(session: Session, username: str):
        query = session.query(User).filter_by(username=username)
        result = query.first()
        return result
