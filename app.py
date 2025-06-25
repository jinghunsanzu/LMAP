"""主应用文件"""

import os
from flask import Flask, render_template, jsonify
from app.config import ConfigManager
from app.controllers import analysis_bp, config_bp
from app.utils import setup_logger, get_logger, create_error_response
from app.services import ai_service

# 初始化配置管理器
config_manager = ConfigManager('app/config/config.ini')

# 设置日志
setup_logger()

logger = get_logger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置应用
    server_config = config_manager.get_server_config()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # 注册蓝图
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(config_bp, url_prefix='/api')
    
    # 主页路由
    @app.route('/')
    def index():
        """主页"""
        try:
            ui_config = config_manager.get_ui_config()
            # 定义可用的主题列表
            available_themes = ['浅色主题', '深色主题']
            return render_template('index.html', 
                                 default_theme=ui_config.default_theme,
                                 themes=available_themes)
        except Exception as e:
            logger.error(f"渲染主页失败: {e}")
            return create_error_response("页面加载失败", 500)
    
    # Chrome开发者工具支持
    @app.route('/.well-known/appspecific/com.chrome.devtools.json')
    def chrome_devtools():
        """Chrome开发者工具配置"""
        return jsonify({
            "type": "node",
            "title": "DeepSeek安全工具",
            "description": "Web安全分析工具",
            "url": "/"
        })
    
    # 健康检查
    @app.route('/health')
    def health_check():
        """健康检查"""
        try:
            # 检查配置
            config_errors = config_manager.validate_config()
            
            # 检查AI服务
            api_info = ai_service.get_api_info()
            
            return jsonify({
                "status": "healthy" if len(config_errors) == 0 else "warning",
                "config_valid": len(config_errors) == 0,
                "config_errors": config_errors,
                "api_info": api_info
            })
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 500
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return create_error_response("页面未找到", 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        logger.error(f"内部服务器错误: {error}")
        return create_error_response("内部服务器错误", 500)
    
    @app.errorhandler(413)
    def too_large(error):
        """文件过大错误处理"""
        return create_error_response("上传文件过大，最大支持16MB", 413)
    
    logger.info("Flask应用创建成功")
    return app

def main():
    """主函数"""
    try:
        # 验证配置
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.warning(f"配置验证警告: {config_errors}")
            print("配置验证警告:")
            for error in config_errors:
                print(f"  - {error}")
            print()
        
        # 创建应用
        app = create_app()
        
        # 获取服务器配置
        server_config = config_manager.get_server_config()
        
        logger.info(f"启动服务器: {server_config.host}:{server_config.port}")
        print(f"DeepSeek安全工具启动成功!")
        print(f"访问地址: http://{server_config.host}:{server_config.port}")
        print(f"调试模式: {server_config.debug}")
        print()
        
        # 启动服务器
        app.run(
            host=server_config.host,
            port=server_config.port,
            debug=server_config.debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        print(f"应用启动失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())