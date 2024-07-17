from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.utils.str import StringUtil


class Additional(BaseModel):
    """额外信息"""
    time: str
    trace_id: str


class HttpResponse(BaseModel):
    """http统一响应"""
    code: int = Field(default=200)  # 响应码
    msg: str = Field(default="处理成功")  # 响应信息
    data: Any = None  # 具体数据
    additional: Additional = None  # 额外信息


def response_success(resp: Any = 'ok') -> HttpResponse:
    """成功响应"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HttpResponse(
        data=resp,
        additional=Additional(
            time=current_time,
            trace_id=StringUtil.generate_md5(current_time),
        ))


def response_fail(msg: str, code: int = -1) -> HttpResponse:
    """响应失败"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HttpResponse(
        code=code,
        msg=msg,
        additional=Additional(
            time=current_time,
            trace_id=StringUtil.generate_md5(current_time),
        ))
