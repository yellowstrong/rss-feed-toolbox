from sqlalchemy import Column, Integer, String, Boolean

from app.helper.database_helper import Base


class Downloader(Base):
    __tablename__ = 'downloader'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    default = Column(Boolean)
