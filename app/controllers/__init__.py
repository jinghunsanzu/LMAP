"""控制器模块初始化"""

from .analysis_controller import analysis_bp
from .config_controller import config_bp

__all__ = ['analysis_bp', 'config_bp']