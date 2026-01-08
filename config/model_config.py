"""
模型配置文件
支持多种模型供应商和模型配置
"""

# 默认模型配置
DEFAULT_MODEL_CONFIG = {
    "provider": "ollama",  # 默认供应商: ollama
    "models": {
        "ollama": {
            "base_url": "http://localhost:11434/api",
            "model_name": "qwen2:0.5b",
            "api_key": ""
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "api_key": ""
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1",
            "model_name": "claude-3-sonnet-20240229",
            "api_key": ""
        },
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "model_name": "qwen2.5-7b-instruct",
            "api_key": "sk-2ce1bb163bde443bbd959da078b33f3d"
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "api_key": ""
        }
    }
}

def get_model_config(provider=None):
    """
    获取模型配置
    
    Args:
        provider: 模型供应商名称，如果为None则返回默认供应商配置
        
    Returns:
        dict: 模型配置
    """
    if provider is None:
        provider = DEFAULT_MODEL_CONFIG["provider"]
    
    if provider in DEFAULT_MODEL_CONFIG["models"]:
        return DEFAULT_MODEL_CONFIG["models"][provider]
    
    return DEFAULT_MODEL_CONFIG["models"][DEFAULT_MODEL_CONFIG["provider"]]

def get_supported_providers():
    """
    获取支持的模型供应商列表
    
    Returns:
        list: 支持的供应商名称列表
    """
    return list(DEFAULT_MODEL_CONFIG["models"].keys())

def get_default_provider():
    """
    获取默认模型供应商
    
    Returns:
        str: 默认供应商名称
    """
    return DEFAULT_MODEL_CONFIG["provider"]