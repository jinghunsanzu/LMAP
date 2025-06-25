"""错误处理装饰器和工具"""

import functools
import traceback
from flask import jsonify
from typing import Callable, Any
from .exceptions import APIException, ValidationError, ConfigurationError, AIServiceError
from .logger import get_logger

logger = get_logger('error_handler')


def handle_api_error(func: Callable) -> Callable:
    """API错误处理装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"验证错误: {e.message}", extra={'details': e.details})
            return jsonify({
                "error": e.message,
                "error_code": e.error_code or "VALIDATION_ERROR",
                "details": e.details
            }), 400
        except ConfigurationError as e:
            logger.error(f"配置错误: {e.message}", extra={'details': e.details})
            return jsonify({
                "error": e.message,
                "error_code": e.error_code or "CONFIG_ERROR",
                "details": e.details
            }), 500
        except AIServiceError as e:
            logger.error(f"AI服务错误: {e.message}", extra={'details': e.details})
            return jsonify({
                "error": e.message,
                "error_code": e.error_code or "AI_SERVICE_ERROR",
                "details": e.details
            }), 503
        except APIException as e:
            logger.error(f"API异常: {e.message}", extra={'details': e.details})
            return jsonify({
                "error": e.message,
                "error_code": e.error_code or "API_ERROR",
                "details": e.details
            }), 500
        except Exception as e:
            logger.error(f"未预期的错误: {str(e)}", extra={
                'traceback': traceback.format_exc(),
                'function': func.__name__
            })
            return jsonify({
                "error": "内部服务器错误",
                "error_code": "INTERNAL_ERROR"
            }), 500
    
    return wrapper


def handle_service_error(func: Callable) -> Callable:
    """服务层错误处理装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except APIException:
            # 重新抛出API异常，让上层处理
            raise
        except Exception as e:
            logger.error(f"服务层错误: {str(e)}", extra={
                'traceback': traceback.format_exc(),
                'function': func.__name__,
                'function_args': str(args),
                'function_kwargs': str(kwargs)
            })
            raise APIException(f"服务处理失败: {str(e)}")
    
    return wrapper


class ErrorHandler:
    """错误处理工具类"""
    
    @staticmethod
    def format_validation_errors(errors: list) -> dict:
        """格式化验证错误"""
        return {
            "error": "输入验证失败",
            "error_code": "VALIDATION_FAILED",
            "details": {
                "validation_errors": errors
            }
        }
    
    @staticmethod
    def format_config_error(message: str) -> dict:
        """格式化配置错误"""
        return {
            "error": f"配置错误: {message}",
            "error_code": "CONFIG_ERROR",
            "details": {
                "suggestion": "请检查配置文件或联系管理员"
            }
        }
    
    @staticmethod
    def format_ai_service_error(message: str, api_type: str = None) -> dict:
        """格式化AI服务错误"""
        details = {"suggestion": "请检查网络连接和API配置"}
        if api_type:
            details["api_type"] = api_type
        
        return {
            "error": f"AI服务错误: {message}",
            "error_code": "AI_SERVICE_ERROR",
            "details": details
        }
    
    @staticmethod
    def log_request_info(request, additional_info: dict = None):
        """记录请求信息"""
        info = {
            "method": request.method,
            "url": request.url,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', '')
        }
        
        if additional_info:
            info.update(additional_info)
        
        logger.info("API请求", extra=info)


def create_error_response(message: str, error_code: str = None, status_code: int = 500, details: dict = None):
    """创建标准错误响应"""
    response_data = {
        "error": message,
        "error_code": error_code or "UNKNOWN_ERROR"
    }
    
    if details:
        response_data["details"] = details
    
    return jsonify(response_data), status_code