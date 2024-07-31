from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.types import apiproto


class SubscribeQuery(BaseModel):
    page: Optional[int] = Field(default=1, description="当前页", examples=["1"])
    page_size: Optional[int] = Field(default=10, description="每页数量", examples=["10"])


class Subscribe(BaseModel):
    id: Optional[int] = Field(default=None, description='id')
    name: str = Field(description='订阅名称')
    site_rss_id: int = Field(description='关联RSS')

    match_title: str = Field(description='匹配标题')
    match_season: Optional[str] = Field(default=None, description='匹配季')
    match_team: Optional[str] = Field(default=None, description='制作组')
    include: Optional[str] = Field(default=None, description='包含')
    exclude: Optional[str] = Field(default=None, description='排除')

    download_path: Optional[str] = Field(default=None, description='下载路径')
    transfer_path: Optional[str] = Field(default=None, description='转移路径')

    status: bool = Field(default=True, description='状态')

    rss: Optional[apiproto.SiteRss] = Field(default=None, description='rss')

    class Config:
        from_attributes = True


class SubscribeList(BaseModel):
    record_total: int = Field(default=0, description="总量")
    record_list: list[Subscribe] = Field(default=[])


class DownloadHistory(BaseModel):
    id: Optional[int] = Field(default=None, description='id')
    subscribe_id: int = Field(description='关联订阅')
    rss_title: str = Field(description='rss标题')
    rss_guid: str = Field(default='', description='rss唯一编号')
    torrent_hash: str = Field(description='种子哈希')
    torrent_list: str = Field(description='种子文件清单')
    create_at: datetime = Field(description='创建时间')
