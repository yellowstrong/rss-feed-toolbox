from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class SiteQuery(BaseModel):
    page: Optional[int] = Field(default=1, description="当前页", examples=["1"])
    page_size: Optional[int] = Field(default=10, description="每页数量", examples=["10"])


class SiteRss(BaseModel):
    id: Optional[int] = None
    site_id: Optional[int] = None
    alias: str
    url: str
    latest_pub: Optional[datetime] = None

    def __hash__(self):
        return hash((self.id, self.site_id, self.alias, self.url, self.latest_pub))

    class Config:
        frozen = True


class Site(BaseModel):
    id: Optional[int] = None
    name: str
    url: str
    cookie: str
    time_out: Optional[int] = None
    user_agent: Optional[str] = None
    site_rss: list[SiteRss] = []

    class Config:
        from_attributes = True


class SiteList(BaseModel):
    record_total: int = Field(default=0, description="总量")
    record_list: list[Site] = Field(default=[])
