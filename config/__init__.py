"""
配置包初始化文件
"""
from .platform_config import get_platform_config, is_type_supported, get_supported_platforms

__all__ = [
    'get_platform_config',
    'is_type_supported',
    'get_supported_platforms'
]
