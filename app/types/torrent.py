from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TorrentInfo(BaseModel):
    title: Optional[str] = None
    enclosure: Optional[str] = None
    size: Optional[float] = None
    pubdate: Optional[datetime] = None