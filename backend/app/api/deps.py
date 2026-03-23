"""
FastAPI 依赖注入
"""
from functools import lru_cache

from app.config import get_settings
from app.services.github_service import GitHubService


@lru_cache
def get_github_service() -> GitHubService:
    """获取 GitHub 服务单例"""
    settings = get_settings()
    return GitHubService(token=settings.GITHUB_TOKEN)