from fastapi import Request, status, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import validate_template_config
from fastapi.encoders import jsonable_encoder

from app.utils.response import response_fail


def register_validation_error_handler(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """自定义参数验证异常错误"""
        err_msg = ""
        for error in exc.errors():
            field_name = ".".join(error.get("loc"))
            err_type = error.get("type")
            if err_type in validate_template_config.validateChineseDict:
                # 在定义错误模版中，并翻译出内容
                translate_msg = translate(field_name, err_type, error.get("ctx")) + "; "
                if translate_msg:
                    err_msg += translate_msg
            else:
                # 不在定义模型，显示原始错误
                err_msg += (
                        ".".join(error.get("loc"))
                        + "["
                        + error.get("type")
                        + "]:"
                        + error.get("msg")
                        + "; "
                )

        # 替换body.
        err_msg = err_msg.replace("body.", "")
        # 返回
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(response_fail(err_msg)),
        )

    def translate(field_name: str, err_type: str, limit_dict: dict) -> str:
        """翻译错误信息"""
        # 先判断是否满足关键词错误
        for k, v in validate_template_config.keyErrorChineseDict.items():
            if field_name.find(k) != -1:
                return v

        limit_val_list = limit_dict.values()
        try:
            return validate_template_config.validateChineseDict.get(err_type).format(field_name, *limit_val_list)
        except Exception as e:
            return ""
