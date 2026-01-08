"""
平台配置文件
用于存放不同平台和不同类型处理器的配置信息
"""

# Bilibili 平台配置
BILIBILI = {
    "name": "Bilibili",
    "base_url": "https://www.bilibili.com",
    "supported_types": ["收藏夹", "视频"]
}

# YouTube 平台配置（预留）
YOUTUBE = {
    "name": "YouTube",
    "base_url": "https://www.youtube.com",
    "supported_types": ["播放列表", "视频"]
}

# 抖音平台配置（预留）
DOUYIN = {
    "name": "抖音",
    "base_url": "https://www.douyin.com",
    "supported_types": ["收藏夹", "视频"]
}

# 平台映射表
PLATFORMS = {
    "Bilibili": BILIBILI,
    "YouTube": YOUTUBE,
    "抖音": DOUYIN
}

# 获取平台配置
def get_platform_config(platform_name):
    """
    根据平台名称获取平台配置
    
    Args:
        platform_name: 平台名称（如 "Bilibili", "YouTube", "抖音"）
    
    Returns:
        dict: 平台配置信息
    """
    return PLATFORMS.get(platform_name, BILIBILI)

# 获取支持的平台列表
def get_supported_platforms():
    """
    获取所有支持的平台列表
    
    Returns:
        list: 平台名称列表
    """
    return list(PLATFORMS.keys())

# 检查平台是否支持指定类型
def is_type_supported(platform_name, type_name):
    """
    检查指定平台是否支持指定的类型
    
    Args:
        platform_name: 平台名称
        type_name: 类型名称
    
    Returns:
        bool: 是否支持
    """
    platform_config = get_platform_config(platform_name)
    return type_name in platform_config.get("supported_types", [])
