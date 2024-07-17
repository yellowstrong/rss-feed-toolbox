from sqlalchemy import Column, String, Boolean, Integer
from app.helper.database_helper import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String)
    admin = Column(Boolean, default=True)
    disabled = Column(Boolean, default=False)
