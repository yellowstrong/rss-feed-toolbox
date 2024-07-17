from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TorrentInfo(BaseModel):
    title: Optional[str] = None
    enclosure: Optional[str] = None
    page_url: Optional[str] = None
    size: Optional[float] = None
    guid: Optional[str] = None
    pubdate: Optional[datetime] = None
    cookie: Optional[str] = None
    ua: Optional[str] = None
