"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # App
    APP_NAME: str = "RepoRhythm"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # GitHub
    GITHUB_TOKEN: str | None = Field(default=None, env="GITHUB_TOKEN")
    GITHUB_API_BASE: str = "https://api.github.com"
    MAX_COMMITS: int = 500
    
    # Music
    DEFAULT_BPM: int = 120
    DEFAULT_STYLE: str = "electronic"
    MIN_BPM: int = 60
    MAX_BPM: int = 200
    
    # Cache
    CACHE_TTL: int = 3600
    CACHE_MAX_SIZE: int = 100
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://reporhythm.vercel.app",
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()