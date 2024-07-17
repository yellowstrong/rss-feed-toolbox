from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.helper.database_helper import Base


class SiteRss(Base):
    __tablename__ = 'site_rss'

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('site.id'), nullable=False)
    alias = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    latest_pub = Column(DateTime)

    site = relationship("Site", back_populates="site_rss")
    subscribe = relationship("Subscribe", back_populates="site_rss")
