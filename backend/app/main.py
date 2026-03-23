"""
FastAPI 应用入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import get_settings
from app.api.routes import github, music, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    settings = get_settings()
    print(f"🎵 RepoRhythm API v{settings.API_VERSION} starting...")
    print(f"   Debug mode: {settings.DEBUG}")
    print(f"   GitHub token: {'configured' if settings.GITHUB_TOKEN else 'not set'}")
    
    yield
    
    # Shutdown
    print("🎵 RepoRhythm shutting down...")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="""
        🎵 **RepoRhythm** - Transform GitHub commit history into music!
        
        This API analyzes GitHub repositories and generates unique musical compositions
        based on commit patterns, contributor activity, and code changes.
        
        ## Features
        - 🎹 Multiple music styles (Electronic, Classical, Rock, Jazz, etc.)
        - 🎼 Intelligent melody generation based on commit types
        - 🥁 Dynamic drum patterns matching activity levels
        - 📥 MIDI file download support
        
        ## Quick Start
        1. Use `/api/v1/music/generate` with your repo URL
        2. Get back music data for web playback
        3. Download MIDI file for DAW import
        """,
        version=settings.API_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 请求计时中间件
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        return response
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if settings.DEBUG else None,
            }
        )
    
    # 注册路由
    app.include_router(health.router, tags=["Health"])
    app.include_router(
        github.router, 
        prefix="/api/v1/github", 
        tags=["GitHub"]
    )
    app.include_router(
        music.router, 
        prefix="/api/v1/music", 
        tags=["Music"]
    )
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )