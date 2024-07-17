from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.helper.database_helper import Base


class Site(Base):
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    cookie = Column(String, nullable=False)
    time_out = Column(Integer)
    user_agent = Column(String)

    site_rss = relationship("SiteRss", back_populates="site", cascade='all, delete-orphan')
