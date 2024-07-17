from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from app.helper.database_helper import Base


class DownloadHistory(Base):
    __tablename__ = 'download_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscribe_id = Column(Integer, ForeignKey('subscribe.id'), nullable=False)
    rss_title = Column(String, nullable=False)
    rss_guid = Column(String)
    torrent_hash = Column(String, nullable=False)
    create_at = Column(DateTime, nullable=False)

    subscribe = relationship('Subscribe', back_populates='download_history')
