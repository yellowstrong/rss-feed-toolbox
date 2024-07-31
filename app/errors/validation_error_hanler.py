from fastapi import Request, status, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.encoders import jsonable_encoder
from app.config.validate_template_config import CUSTOM_VALIDATION_ERROR_MESSAGES
from app.utils.response import response_fail


async def _validation_exception_handler(_: Request, e: RequestValidationError | ValidationError):
    """数据验证异常处理"""
    errors = []
    for error in e.errors():
        custom_message = CUSTOM_VALIDATION_ERROR_MESSAGES.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            if not ctx:
                error['msg'] = custom_message
            else:
                error['msg'] = custom_message.format(**ctx)
                ctx_error = ctx.get('error')
                if ctx_error:
                    error['ctx']['error'] = (
                        ctx_error.__str__().replace("'", '"') if isinstance(ctx_error, Exception) else None
                    )
        errors.append(error)
    error = errors[0]
    if error.get('type') == 'json_invalid':
        message = 'json解析失败'
    else:
        error_input = error.get('input')
        field = str(error.get('loc')[-1])
        error_msg = error.get('msg')
        message = f'{error_msg}{field}，输入：{error_input}'
    msg = f'请求参数非法: {message}'
    return JSONResponse(
        content=jsonable_encoder(response_fail(msg=msg)),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def register_validation_error_handler(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """fastapi 数据验证异常处理"""
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """pydantic 数据验证异常处理"""
        return await _validation_exception_handler(request, exc)
