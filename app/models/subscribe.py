from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.helper.database_helper import Base


class Subscribe(Base):
    __tablename__ = 'subscribe'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    site_rss_id = Column(Integer, ForeignKey('site_rss.id'))
    match_title = Column(String, nullable=False)
    match_season = Column(String)
    match_team = Column(String)
    include = Column(String)
    exclude = Column(String)
    download_path = Column(String)
    transfer_path = Column(String)
    status = Column(Boolean, default=True)

    site_rss = relationship('SiteRss', back_populates='subscribe')
    download_history = relationship("DownloadHistory", back_populates="subscribe")
