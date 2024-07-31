from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from pydantic import BaseModel

from app.utils.timezone import timezone


class JwtTokenBody(BaseModel):
    jti: str
    iss: str
    iat: datetime
    exp: datetime
    data: Any


TokenErrorTimeOut = "TokenTimeOut|token过期"
TokenErrorInvalid = "TokenInvalid|token非法"


class JwtHelper(object):

    def __init__(self,
                 secret_key: str,
                 algorithm: str = "HS256",
                 expired: int = 60,
                 china_time_zone=timezone.tz_info,
                 iss: str = ''):

        self.secretKey = secret_key
        self.algorithm = algorithm
        self.expired = expired
        self.iss = iss
        self.chinaTimeZone = china_time_zone

    def generate(self, payload: BaseModel) -> str:

        current_time = datetime.now(self.chinaTimeZone)
        jwt_data = JwtTokenBody(
            jti=current_time.strftime("%Y%m%d%H%M%f"),
            iss=self.iss,
            iat=current_time,
            exp=current_time + timedelta(minutes=self.expired),
            data=payload
        )
        # 生成 JWT
        return jwt.encode(jwt_data.model_dump(), self.secretKey, algorithm=self.algorithm)

    def decode(self, jwt_token: str, decode_pydantic_model: Any) -> BaseModel | str:

        try:
            decoded_payload = jwt.decode(jwt_token, self.secretKey, algorithms=[self.algorithm])
            result = JwtTokenBody(**decoded_payload)
            return decode_pydantic_model.parse_obj(result.data)
        except jwt.ExpiredSignatureError:
            return TokenErrorTimeOut
        except (jwt.JWTError, jwt.JWTClaimsError):
            return TokenErrorInvalid
        except Exception as e:
            return str(e)
