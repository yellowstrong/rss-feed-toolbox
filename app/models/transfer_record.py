from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from app.helper.database_helper import Base


class TransferRecord(Base):
    __tablename__ = 'transfer_record'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscribe_history_id = Column(Integer, ForeignKey('subscribe_history.id'), nullable=False)
    source_file_path = Column(String, nullable=False)
    target_file_path = Column(String, nullable=False)
    transfer_time = Column(DateTime, nullable=False)

    subscribe_history = relationship("SubscribeHistory", back_populates="transfer_record")
