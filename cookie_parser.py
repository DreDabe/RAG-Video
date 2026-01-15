import json
import re
from typing import Dict, List, Optional


class CookieFormat:
    NETSCAPE = "netscape"
    JSON = "json"
    HEADER_STRING = "header_string"
    UNKNOWN = "unknown"


def detect_cookie_format(cookie_text: str) -> str:
    """
    检测Cookie格式
    
    Args:
        cookie_text: Cookie文本内容
    
    Returns:
        Cookie格式类型
    """
    if not cookie_text or not cookie_text.strip():
        return CookieFormat.UNKNOWN
    
    cookie_text = cookie_text.strip()
    
    # 检测JSON格式
    if cookie_text.startswith('[') or cookie_text.startswith('{'):
        try:
            json.loads(cookie_text)
            return CookieFormat.JSON
        except json.JSONDecodeError:
            pass
    
    # 检测Header String格式 (格式: name1=value1; name2=value2; ...)
    # 检查是否包含分号分隔的键值对
    if '=' in cookie_text and ';' in cookie_text:
        # 检查是否匹配典型的header string模式
        # 例如: bili_jct=xxx; SESSDATA=yyy
        pattern = r'^[\w\-]+\s*=\s*[^;\s]+(\s*;\s*[\w\-]+\s*=\s*[^;\s]+)*$'
        if re.match(pattern, cookie_text):
            return CookieFormat.HEADER_STRING
    
    # 检测NetScape格式
    # NetScape格式通常是制表符分隔的多行，每行包含多个字段
    lines = cookie_text.split('\n')
    if len(lines) > 0:
        # 检查是否有非注释行包含制表符分隔的多个字段
        # NetScape格式: domain, flag, path, secure, expiration, name, value
        for line in lines:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            # 检查是否包含制表符分隔的多个字段
            if '\t' in line and line.count('\t') >= 5:
                return CookieFormat.NETSCAPE
            # 也检查空格分隔的情况（有些格式可能用空格）
            if '  ' in line and len(line.split()) >= 7:
                return CookieFormat.NETSCAPE
    
    return CookieFormat.UNKNOWN


def parse_header_string(cookie_text: str) -> List[Dict[str, str]]:
    """
    解析Header String格式的Cookie
    
    Args:
        cookie_text: Header String格式的Cookie文本
    
    Returns:
        Cookie字典列表
    """
    cookies = []
    if not cookie_text:
        return cookies
    
    # 分割键值对
    pairs = [pair.strip() for pair in cookie_text.split(';') if pair.strip()]
    
    for pair in pairs:
        if '=' in pair:
            name, value = pair.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '',
                'path': '/',
                'flag': 'TRUE',
                'secure': 'FALSE',
                'expiration': '0'
            })
    
    return cookies


def parse_json_cookie(cookie_text: str) -> List[Dict[str, str]]:
    """
    解析JSON格式的Cookie
    
    Args:
        cookie_text: JSON格式的Cookie文本
    
    Returns:
        Cookie字典列表
    """
    try:
        data = json.loads(cookie_text)
        
        # 如果是数组
        if isinstance(data, list):
            return data
        
        # 如果是单个对象
        if isinstance(data, dict):
            return [data]
        
        return []
    except json.JSONDecodeError:
        return []


def parse_netscape_cookie(cookie_text: str) -> List[Dict[str, str]]:
    """
    解析NetScape格式的Cookie
    
    Args:
        cookie_text: NetScape格式的Cookie文本
    
    Returns:
        Cookie字典列表
    """
    cookies = []
    if not cookie_text:
        return cookies
    
    lines = cookie_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行和注释行
        if not line or line.startswith('#'):
            continue
        
        # NetScape格式: domain, flag, path, secure, expiration, name, value
        fields = line.split('\t')
        
        if len(fields) >= 7:
            cookies.append({
                'domain': fields[0].strip(),
                'flag': fields[1].strip(),
                'path': fields[2].strip(),
                'secure': fields[3].strip(),
                'expiration': fields[4].strip(),
                'name': fields[5].strip(),
                'value': fields[6].strip()
            })
    
    return cookies


def convert_to_netscape(cookies: List[Dict[str, str]], default_domain: Optional[str] = None) -> str:
    """
    将Cookie字典列表转换为NetScape格式字符串
    
    Args:
        cookies: Cookie字典列表
        default_domain: 默认域名（当cookie没有domain字段时使用）
    
    Returns:
        NetScape格式的Cookie字符串
    """
    if not cookies:
        return ""
    
    # 添加Netscape文件头
    lines = ["# Netscape HTTP Cookie File"]
    
    for cookie in cookies:
        # 获取字段，提供默认值
        domain = cookie.get('domain', '')
        flag = cookie.get('flag', 'TRUE')
        path = cookie.get('path', '/')
        secure = cookie.get('secure', 'FALSE')
        expiration = cookie.get('expiration', '0')
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        
        # 如果没有domain，使用默认域名
        if not domain:
            domain = default_domain if default_domain else ''
        
        # 构建NetScape格式的行
        line = f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}"
        lines.append(line)
    
    return '\n'.join(lines)


def normalize_cookie(cookie_text: str, target_domain: Optional[str] = None) -> str:
    """
    将任意格式的Cookie转换为NetScape格式
    
    Args:
        cookie_text: 任意格式的Cookie文本
        target_domain: 目标域名（可选，用于Header String格式）
    
    Returns:
        NetScape格式的Cookie字符串
    """
    if not cookie_text:
        return ""
    
    format_type = detect_cookie_format(cookie_text)
    
    if format_type == CookieFormat.NETSCAPE:
        # 已经是NetScape格式，直接返回
        return cookie_text
    
    cookies = []
    
    if format_type == CookieFormat.JSON:
        cookies = parse_json_cookie(cookie_text)
    elif format_type == CookieFormat.HEADER_STRING:
        cookies = parse_header_string(cookie_text)
        # 为Header String格式的cookie设置默认domain
        if target_domain:
            for cookie in cookies:
                if not cookie.get('domain'):
                    cookie['domain'] = target_domain
    else:
        # 未知格式，尝试作为NetScape格式处理
        return cookie_text
    
    if not cookies:
        return ""
    
    return convert_to_netscape(cookies, default_domain=target_domain)


def get_cookie_format_name(format_type: str) -> str:
    """
    获取Cookie格式的中文名称
    
    Args:
        format_type: Cookie格式类型
    
    Returns:
        格式中文名称
    """
    names = {
        CookieFormat.NETSCAPE: "NetScape格式",
        CookieFormat.JSON: "JSON格式",
        CookieFormat.HEADER_STRING: "Header String格式",
        CookieFormat.UNKNOWN: "未知格式"
    }
    return names.get(format_type, "未知格式")
