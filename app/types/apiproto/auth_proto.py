from typing import Optional

from pydantic import BaseModel, Field


class Login(BaseModel):
    username: str = Field(description='用户名')
    password: str = Field(description='密码')


class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: Optional[str] = None
    avatar: Optional[str] = None
    admin: bool = True
    disabled: bool = False


class Token(BaseModel):
    x_token: str = Field(description='X-Token')
    expired: int = Field(description='有效期')


class TokenData(BaseModel):
    user_id: int
    username: str
