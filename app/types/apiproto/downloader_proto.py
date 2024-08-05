from typing import Optional

from pydantic import BaseModel, Field


class DownloaderQuery(BaseModel):
    current: Optional[int] = Field(default=1, description="当前页", examples=["1"])
    pageSize: Optional[int] = Field(default=10, description="每页数量", examples=["10"])


class Downloader(BaseModel):
    id: Optional[int] = None
    name: str
    host: str
    port: int
    username: str
    password: str
    default: Optional[bool] = None
