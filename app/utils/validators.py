"""输入验证器"""

import re
from typing import List, Optional
from .exceptions import ValidationError


class Validator:
    """通用验证器"""
    
    @staticmethod
    def validate_required(value: str, field_name: str) -> None:
        """验证必填字段"""
        if not value or not value.strip():
            raise ValidationError(f"{field_name}不能为空")
    
    @staticmethod
    def validate_url(url: str, field_name: str = "URL") -> None:
        """验证URL格式"""
        if not url:
            raise ValidationError(f"{field_name}不能为空")
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise ValidationError(f"{field_name}格式不正确")
    
    @staticmethod
    def validate_api_key(api_key: str, api_type: str) -> None:
        """验证API密钥格式"""
        if not api_key or not api_key.strip():
            raise ValidationError(f"{api_type} API密钥不能为空")
        
        # 基本长度检查
        if len(api_key.strip()) < 10:
            raise ValidationError(f"{api_type} API密钥长度不足")
        
        # 特定格式检查
        if api_type == "deepseek" and not api_key.startswith("sk-"):
            raise ValidationError("DeepSeek API密钥应以'sk-'开头")
        
        if api_type == "openrouter" and not api_key.startswith("sk-or-"):
            raise ValidationError("OpenRouter API密钥应以'sk-or-'开头")
    
    @staticmethod
    def validate_model_name(model: str, field_name: str = "模型名称") -> None:
        """验证模型名称"""
        if not model or not model.strip():
            raise ValidationError(f"{field_name}不能为空")
        
        # 基本格式检查
        if len(model.strip()) < 3:
            raise ValidationError(f"{field_name}长度不足")
    
    @staticmethod
    def validate_api_type(api_type: str) -> None:
        """验证API类型"""
        valid_types = ['deepseek', 'openrouter', 'ollama']
        if api_type not in valid_types:
            raise ValidationError(f"API类型必须是以下之一: {', '.join(valid_types)}")
    
    @staticmethod
    def validate_file_content(content: str, max_length: int = 1000000) -> None:
        """验证文件内容"""
        if not content:
            raise ValidationError("文件内容不能为空")
        
        if len(content) > max_length:
            raise ValidationError(f"文件内容过长，最大支持{max_length}字符")
    
    @staticmethod
    def validate_http_data(http_data: str) -> None:
        """验证HTTP数据格式"""
        if not http_data or not http_data.strip():
            raise ValidationError("HTTP数据不能为空")
        
        # 基本HTTP请求格式检查
        lines = http_data.strip().split('\n')
        if not lines:
            raise ValidationError("HTTP数据格式不正确")
        
        # 检查是否包含HTTP方法
        first_line = lines[0].strip()
        http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']
        if not any(method in first_line.upper() for method in http_methods):
            raise ValidationError("HTTP数据应包含有效的HTTP方法")
    
    @staticmethod
    def validate_js_code(js_code: str) -> None:
        """验证JavaScript代码"""
        if not js_code or not js_code.strip():
            raise ValidationError("JavaScript代码不能为空")
        
        # 基本长度检查
        if len(js_code.strip()) < 10:
            raise ValidationError("JavaScript代码内容过短")
    
    @staticmethod
    def validate_process_data(process_data: str) -> None:
        """验证进程数据"""
        if not process_data or not process_data.strip():
            raise ValidationError("进程数据不能为空")
        
        # 检查是否包含进程信息的基本特征
        lines = process_data.strip().split('\n')
        if len(lines) < 2:
            raise ValidationError("进程数据格式不正确，应包含多行进程信息")
    
    @staticmethod
    def validate_text_input(text: str, field_name: str = "文本", max_length: int = 10000) -> None:
        """验证文本输入"""
        if not text or not text.strip():
            raise ValidationError(f"{field_name}不能为空")
        
        if len(text.strip()) > max_length:
            raise ValidationError(f"{field_name}长度不能超过{max_length}字符")
        
        # 检查是否包含有效内容（不只是空白字符）
        if len(text.strip()) < 2:
            raise ValidationError(f"{field_name}内容过短")


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_api_config(api_type: str, api_url: str, api_key: str, model: str) -> List[str]:
        """验证API配置"""
        errors = []
        
        try:
            Validator.validate_api_type(api_type)
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            Validator.validate_url(api_url, f"{api_type} API地址")
        except ValidationError as e:
            errors.append(str(e))
        
        if api_type in ['deepseek', 'openrouter']:
            try:
                Validator.validate_api_key(api_key, api_type)
            except ValidationError as e:
                errors.append(str(e))
        
        try:
            Validator.validate_model_name(model, f"{api_type} 模型名称")
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @staticmethod
    def validate_theme(theme: str) -> List[str]:
        """验证主题配置"""
        errors = []
        valid_themes = ['light', 'dark']
        
        if theme not in valid_themes:
            errors.append(f"主题必须是以下之一: {', '.join(valid_themes)}")
        
        return errors