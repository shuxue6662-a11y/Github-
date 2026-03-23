"""
FastAPI 依赖注入
"""
from functools import lru_cache
from typing import Generator

from app.config import get_settings, Settings
from app.services.github_service import GitHubService


def get_config() -> Settings:
    """获取配置"""
    return get_settings()


@lru_cache
def get_github_service() -> GitHubService:
    """获取 GitHub 服务单例"""
    settings = get_settings()
    return GitHubService(token=settings.GITHUB_TOKEN)