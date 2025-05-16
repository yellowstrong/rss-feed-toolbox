from sqlalchemy import Column, Integer, String

from app.helper.database_helper import Base


class CloudSyncStrm(Base):
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_dir = Column(String,nullable=False)
    target_dir = Column(String,nullable=False)
    