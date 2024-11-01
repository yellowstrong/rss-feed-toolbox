from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.helper.database_helper import Base


class SubscribeHistory(Base):
    __tablename__ = 'subscribe_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscribe_id = Column(Integer,ForeignKey('subscribe.id'), nullable=False)
    rss_title = Column(String, nullable=False)
    rss_pubdate = Column(DateTime, nullable=False)
    downloader_id = Column(Integer, ForeignKey('downloader.id'), nullable=False)
    torrent_hash = Column(String, nullable=False)
    torrent_file = Column(String, nullable=False)
    create_at = Column(DateTime, nullable=False)
    deleted = Column(Boolean)

    subscribe = relationship('Subscribe', back_populates='subscribe_history')
    downloader = relationship('Downloader')
    transfer_record = relationship('TransferRecord', back_populates='subscribe_history')