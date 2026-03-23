"""
辅助函数
"""
import re
import os
from typing import Tuple, Optional, List
from datetime import datetime


def parse_repo_url(url: str) -> Tuple[str, str]:
    """
    解析 GitHub URL 获取 owner 和 repo
    
    支持格式：
    - https://github.com/owner/repo
    - http://github.com/owner/repo
    - github.com/owner/repo
    - owner/repo
    - git@github.com:owner/repo.git
    
    Returns:
        (owner, repo) 元组
    
    Raises:
        ValueError: 无法解析的 URL
    """
    url = url.strip().rstrip('/')
    
    if not url:
        raise ValueError("Repository URL cannot be empty")
    
    # 尝试不同的模式
    patterns = [
        # SSH 格式
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
        # HTTPS 格式
        r'(?:https?://)?github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$',
        # 简短格式 owner/repo
        r'^([a-zA-Z0-9][-a-zA-Z0-9]*)/([a-zA-Z0-9._-]+)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            owner, repo = match.groups()
            # 清理 repo 名称
            repo = repo.replace('.git', '').split('/')[0].split('?')[0].split('#')[0]
            return owner, repo
    
    raise ValueError(f"Invalid GitHub repository URL: {url}")


def get_file_extension(filename: str) -> str:
    """获取文件扩展名（小写）"""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def extract_file_types(files: List[str]) -> List[str]:
    """从文件列表提取文件类型"""
    extensions = set()
    for f in files:
        ext = get_file_extension(f)
        if ext:
            extensions.add(ext)
    return list(extensions)


def format_duration(seconds: float) -> str:
    """格式化时长"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """限制值在范围内"""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """线性插值"""
    return a + (b - a) * clamp(t, 0, 1)


def map_range(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float,
    out_max: float,
) -> float:
    """将值从一个范围映射到另一个范围"""
    if in_max == in_min:
        return out_min
    t = (value - in_min) / (in_max - in_min)
    return lerp(out_min, out_max, t)


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """安全除法"""
    if b == 0:
        return default
    return a / b


def timestamp_to_datetime(ts: str) -> datetime:
    """ISO 时间戳转 datetime"""
    # 处理不同格式
    ts = ts.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        # 尝试其他格式
        for fmt in [
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S',
        ]:
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse timestamp: {ts}")