"""自定义异常类"""


class APIException(Exception):
    """API异常基类"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(APIException):
    """配置错误"""
    pass


class ValidationError(APIException):
    """验证错误"""
    pass


class AIServiceError(APIException):
    """AI服务错误"""
    pass


class AuthenticationError(APIException):
    """认证错误"""
    pass


class RateLimitError(APIException):
    """请求限制错误"""
    pass