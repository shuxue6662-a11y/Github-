"""
健康检查路由
"""
from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import HealthResponse
from app.config import get_settings


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=datetime.utcnow(),
    )


@router.get("/")
async def root():
    """根路径"""
    return {
        "name": "RepoRhythm API",
        "version": get_settings().API_VERSION,
        "docs": "/docs",
    }