import configparser
import os
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class APIConfig:
    """API配置数据类"""
    api_type: str
    api_url: str
    api_key: str
    model: str
    
    def validate(self) -> List[str]:
        """验证配置有效性"""
        errors = []
        
        if not self.api_url.strip():
            errors.append(f"{self.api_type} API地址不能为空")
        
        if self.api_type in ['deepseek', 'openrouter'] and not self.api_key.strip():
            errors.append(f"{self.api_type} API密钥不能为空")
        
        if not self.model.strip():
            errors.append(f"{self.api_type} 模型名称不能为空")
        
        return errors


@dataclass
class UIConfig:
    """UI配置数据类"""
    default_theme: str = 'dark'


@dataclass
class LoggingConfig:
    """日志配置数据类"""
    level: str = 'INFO'
    file: str = 'logs/app.log'
    max_size: str = '10MB'
    backup_count: int = 5


@dataclass
class ServerConfig:
    """服务器配置数据类"""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = False


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = 'app/config/config.ini'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
        else:
            self.create_default_config()
    
    def create_default_config(self) -> None:
        """创建默认配置文件"""
        default_config = """
# DeepSeek安全分析平台配置文件

[api]
# API类型: deepseek, openrouter, ollama
type = openrouter

[deepseek]
api_url = https://api.deepseek.com/v1/chat/completions
api_key = 
model = deepseek-chat

[openrouter]
api_url = https://openrouter.ai/api/v1/chat/completions
api_key = 
model = moonshotai/moonlight-16b-a3b-instruct:free

[ollama]
api_url = http://localhost:11434/api/chat
model = qwen2.5-coder:14b

[ui]
default_theme = dark

[logging]
level = INFO
file = logs/app.log
max_size = 10MB
backup_count = 5

[server]
host = 0.0.0.0
port = 5000
debug = false
"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)
        self.config.read_string(default_config)
    
    def get_config_value(self, section: str, key: str, fallback: str = '') -> str:
        """获取配置值，支持环境变量覆盖"""
        # 优先级：环境变量 > ini文件 > 默认值
        env_key = f"{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value:
            return env_value
        return self.config.get(section, key, fallback=fallback)
    
    def get_api_config(self) -> APIConfig:
        """获取当前API配置"""
        api_type = self.get_config_value('api', 'type', 'openrouter')
        
        return APIConfig(
            api_type=api_type,
            api_url=self.get_config_value(api_type, 'api_url'),
            api_key=self.get_config_value(api_type, 'api_key'),
            model=self.get_config_value(api_type, 'model')
        )
    
    def get_ui_config(self) -> UIConfig:
        """获取UI配置"""
        return UIConfig(
            default_theme=self.get_config_value('ui', 'default_theme', 'dark')
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        return LoggingConfig(
            level=self.get_config_value('logging', 'level', 'INFO'),
            file=self.get_config_value('logging', 'file', 'logs/app.log'),
            max_size=self.get_config_value('logging', 'max_size', '10MB'),
            backup_count=int(self.get_config_value('logging', 'backup_count', '5'))
        )
    
    def get_server_config(self) -> ServerConfig:
        """获取服务器配置"""
        return ServerConfig(
            host=self.get_config_value('server', 'host', '127.0.0.1'),
            port=int(self.get_config_value('server', 'port', '5000')),
            debug=self.get_config_value('server', 'debug', 'false').lower() == 'true'
        )
    
    def save_config(self, section: str, key: str, value: str) -> None:
        """保存配置项"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def save_api_config(self, api_config: APIConfig) -> None:
        """保存API配置"""
        self.save_config('api', 'type', api_config.api_type)
        self.save_config(api_config.api_type, 'api_url', api_config.api_url)
        self.save_config(api_config.api_type, 'api_key', api_config.api_key)
        self.save_config(api_config.api_type, 'model', api_config.model)
    
    def validate_config(self) -> List[str]:
        """验证配置完整性"""
        errors = []
        
        # 验证API配置
        try:
            api_config = self.get_api_config()
            errors.extend(api_config.validate())
        except Exception as e:
            errors.append(f"API配置错误: {str(e)}")
        
        # 验证必需的节
        required_sections = ['api', 'ui', 'logging', 'server']
        for section in required_sections:
            if not self.config.has_section(section):
                errors.append(f"缺少必需的配置节: {section}")
        
        return errors
    
    def get_all_config(self) -> dict:
        """获取所有配置"""
        result = {}
        for section_name in self.config.sections():
            result[section_name] = dict(self.config.items(section_name))
        return result


# 全局配置管理器实例
config_manager = ConfigManager()
