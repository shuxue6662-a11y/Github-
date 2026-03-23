"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # App
    APP_NAME: str = "RepoRhythm"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # GitHub
    GITHUB_TOKEN: str | None = None
    GITHUB_API_BASE: str = "https://api.github.com"
    MAX_COMMITS: int = 500  # 最大获取 commit 数
    
    # Music
    DEFAULT_BPM: int = 120
    DEFAULT_STYLE: str = "electronic"
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "https://reporhythm.vercel.app"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()