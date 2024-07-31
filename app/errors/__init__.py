class AuthenticationError(Exception):
    def __init__(self, message: str = '未认证'):
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    def __init__(self, message: str = '未授权'):
        self.message = message
        super().__init__(self.message)


class BizError(Exception):
    def __init__(self, message='错误请求'):
        self.message = message
        super().__init__(self.message)


class ImmediateException(Exception):
    pass
