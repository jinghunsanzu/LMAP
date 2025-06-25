"""日志配置模块"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from ..config import config_manager


def setup_logger(app=None, logger_name: str = 'app') -> logging.Logger:
    """设置日志配置"""
    # 获取日志配置
    log_config = config_manager.get_logging_config()
    
    # 创建日志目录
    log_dir = os.path.dirname(log_config.file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    )
    
    # 文件处理器
    try:
        # 解析文件大小
        max_bytes = parse_size(log_config.max_size)
        file_handler = RotatingFileHandler(
            log_config.file,
            maxBytes=max_bytes,
            backupCount=log_config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"设置文件日志处理器失败: {e}")
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果传入了Flask app，也为app设置日志
    if app:
        app.logger.handlers = logger.handlers
        app.logger.setLevel(logger.level)
    
    return logger


def parse_size(size_str: str) -> int:
    """解析文件大小字符串"""
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # 默认按字节处理
        return int(size_str)


def get_logger(name: str = 'app') -> logging.Logger:
    """获取logger实例"""
    return logging.getLogger(name)


class LoggerMixin:
    """日志混入类"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取logger"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger