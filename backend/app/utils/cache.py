"""
缓存工具
"""
from typing import Any, Optional, Callable
from functools import wraps
from cachetools import TTLCache
import hashlib
import json

from app.config import get_settings


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        settings = get_settings()
        self._cache = TTLCache(
            maxsize=settings.CACHE_MAX_SIZE,
            ttl=settings.CACHE_TTL,
        )
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def has(self, key: str) -> bool:
        """检查是否存在"""
        return key in self._cache


# 全局缓存实例
cache = CacheManager()


def make_cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(prefix: str = ""):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator