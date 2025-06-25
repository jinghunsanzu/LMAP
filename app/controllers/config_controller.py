"""配置管理控制器"""

from flask import Blueprint, request, jsonify
from ..config import config_manager
from ..services import ai_service
from ..utils import handle_api_error, ErrorHandler, ConfigValidator

config_bp = Blueprint('config', __name__)


@config_bp.route('/get_config', methods=['GET'])
@handle_api_error
def get_config():
    """获取当前配置"""
    try:
        # 获取所有配置
        all_config = config_manager.get_all_config()
        
        # 隐藏敏感信息
        safe_config = {}
        for section, values in all_config.items():
            safe_config[section] = {}
            for key, value in values.items():
                if 'key' in key.lower() and value:
                    # 隐藏API密钥，只显示前4位和后4位
                    if len(value) > 8:
                        safe_config[section][key] = value[:4] + '*' * (len(value) - 8) + value[-4:]
                    else:
                        safe_config[section][key] = '*' * len(value)
                else:
                    safe_config[section][key] = value
        
        # 记录请求信息
        ErrorHandler.log_request_info(request)
        
        return jsonify({"config": safe_config})
        
    except Exception as e:
        return ErrorHandler.format_config_error(str(e)), 500


@config_bp.route('/save_config', methods=['POST'])
@handle_api_error
def save_config():
    """保存配置"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["配置数据不能为空"]), 400
    
    try:
        # 验证配置数据
        errors = []
        
        # 验证API配置
        if 'api' in data:
            api_type = data['api'].get('type', '')
            if api_type:
                # 获取对应API的配置
                api_config = data.get(api_type, {})
                api_url = api_config.get('api_url', '')
                api_key = api_config.get('api_key', '')
                model = api_config.get('model', '')
                
                validation_errors = ConfigValidator.validate_api_config(
                    api_type, api_url, api_key, model
                )
                errors.extend(validation_errors)
        
        # 验证主题配置
        if 'ui' in data:
            theme = data['ui'].get('default_theme', '')
            if theme:
                theme_errors = ConfigValidator.validate_theme(theme)
                errors.extend(theme_errors)
        
        if errors:
            return ErrorHandler.format_validation_errors(errors), 400
        
        # 保存配置
        for section, values in data.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    config_manager.save_config(section, key, str(value))
        
        # 重新加载AI服务配置
        ai_service.reload_config()
        
        # 记录请求信息
        ErrorHandler.log_request_info(request, {"sections_updated": list(data.keys())})
        
        return jsonify({"result": "配置保存成功"})
        
    except Exception as e:
        return ErrorHandler.format_config_error(str(e)), 500


@config_bp.route('/test_config', methods=['POST'])
@handle_api_error
def test_config():
    """测试API配置连接"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["测试配置数据不能为空"]), 400
    
    api_type = data.get('api_type', '')
    api_url = data.get('api_url', '')
    api_key = data.get('api_key', '')
    model = data.get('model', '')
    
    # 验证输入
    validation_errors = ConfigValidator.validate_api_config(
        api_type, api_url, api_key, model
    )
    if validation_errors:
        return ErrorHandler.format_validation_errors(validation_errors), 400
    
    try:
        # 临时保存当前配置
        original_config = config_manager.get_api_config()
        
        # 临时设置测试配置
        config_manager.save_config('api', 'type', api_type)
        config_manager.save_config(api_type, 'api_url', api_url)
        config_manager.save_config(api_type, 'api_key', api_key)
        config_manager.save_config(api_type, 'model', model)
        
        # 重新加载AI服务配置
        ai_service.reload_config()
        
        # 测试连接
        test_result = ai_service.test_connection()
        
        # 恢复原始配置
        config_manager.save_config('api', 'type', original_config.api_type)
        config_manager.save_config(original_config.api_type, 'api_url', original_config.api_url)
        config_manager.save_config(original_config.api_type, 'api_key', original_config.api_key)
        config_manager.save_config(original_config.api_type, 'model', original_config.model)
        
        # 重新加载原始配置
        ai_service.reload_config()
        
        # 记录请求信息
        ErrorHandler.log_request_info(request, {
            "test_api_type": api_type,
            "test_result": test_result['success']
        })
        
        return jsonify(test_result)
        
    except Exception as e:
        # 确保恢复原始配置
        try:
            ai_service.reload_config()
        except:
            pass
        
        return ErrorHandler.format_ai_service_error(str(e), api_type), 500


@config_bp.route('/get_api_info', methods=['GET'])
@handle_api_error
def get_api_info():
    """获取当前API信息"""
    try:
        api_info = ai_service.get_api_info()
        
        # 记录请求信息
        ErrorHandler.log_request_info(request)
        
        return jsonify(api_info)
        
    except Exception as e:
        return ErrorHandler.format_config_error(str(e)), 500


@config_bp.route('/validate_config', methods=['GET'])
@handle_api_error
def validate_config():
    """验证当前配置"""
    try:
        errors = config_manager.validate_config()
        
        # 记录请求信息
        ErrorHandler.log_request_info(request)
        
        return jsonify({
            "valid": len(errors) == 0,
            "errors": errors
        })
        
    except Exception as e:
        return ErrorHandler.format_config_error(str(e)), 500


@config_bp.route('/reset_config', methods=['POST'])
@handle_api_error
def reset_config():
    """重置配置为默认值"""
    try:
        # 创建默认配置
        config_manager.create_default_config()
        
        # 重新加载AI服务配置
        ai_service.reload_config()
        
        # 记录请求信息
        ErrorHandler.log_request_info(request)
        
        return jsonify({"result": "配置已重置为默认值"})
        
    except Exception as e:
        return ErrorHandler.format_config_error(str(e)), 500