from typing import Optional, TypeVar, Generic, List

from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseQuery(BaseModel):
    current: Optional[int] = Field(default=1, description="当前页", examples=["1"])
    pageSize: Optional[int] = Field(default=10, description="每页数量", examples=["10"])


class BasePaginationList(BaseModel, Generic[T]):
    record_total: int = Field(default=0, description="总量")
    record_list: List[T] = Field(default=[])
