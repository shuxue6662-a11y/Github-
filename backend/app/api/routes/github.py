"""
GitHub 相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends

from app.models.schemas import (
    RepoRequest,
    AnalysisResponse,
    RepoInfoResponse,
    ErrorResponse,
)
from app.services.github_service import GitHubService
from app.services.commit_analyzer import CommitAnalyzer
from app.api.deps import get_github_service


router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repo(
    request: RepoRequest,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    分析 GitHub 仓库的 commit 历史
    """
    try:
        # 解析仓库 URL
        owner, repo = github_service.parse_repo_url(request.repo_url)
        
        # 获取仓库信息
        repo_info = await github_service.get_repo_info(owner, repo)
        
        # 获取 commits
        commits = await github_service.get_commits(
            owner, repo, 
            branch=request.branch,
            max_count=request.max_commits
        )
        
        # 分析 commits
        analyzer = CommitAnalyzer()
        analysis = analyzer.analyze(commits)
        
        return AnalysisResponse(
            repo_info=repo_info,
            analysis=analysis
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze repo: {str(e)}")


@router.get("/repo/{owner}/{repo}", response_model=RepoInfoResponse)
async def get_repo_info(
    owner: str,
    repo: str,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    获取仓库基本信息
    """
    try:
        return await github_service.get_repo_info(owner, repo)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Repository not found: {str(e)}")