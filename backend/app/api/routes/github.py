"""
GitHub 相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from app.models.schemas import (
    RepoRequest,
    AnalysisResponse,
    RepoInfoResponse,
)
from app.services.github_service import GitHubService
from app.services.commit_analyzer import CommitAnalyzer
from app.api.deps import get_github_service
from app.utils.helpers import parse_repo_url


router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repo(
    request: RepoRequest,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    分析 GitHub 仓库的 commit 历史
    
    - **repo_url**: GitHub 仓库 URL 或 owner/repo 格式
    - **branch**: 分支名称（默认 main）
    - **max_commits**: 最大 commit 数量（10-500）
    """
    try:
        # 解析仓库 URL
        owner, repo = parse_repo_url(request.repo_url)
        
        # 获取仓库信息
        repo_info = await github_service.get_repo_info(owner, repo)
        
        # 获取 commits
        commits = await github_service.get_commits(
            owner, repo, 
            branch=request.branch,
            max_count=request.max_commits
        )
        
        if not commits:
            raise HTTPException(
                status_code=404,
                detail=f"No commits found in {owner}/{repo} on branch {request.branch}"
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze repo: {str(e)}"
        )


@router.get("/repo/{owner}/{repo}", response_model=RepoInfoResponse)
async def get_repo_info(
    owner: str,
    repo: str,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    获取仓库基本信息
    
    - **owner**: 仓库所有者
    - **repo**: 仓库名称
    """
    try:
        return await github_service.get_repo_info(owner, repo)
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Repository not found: {owner}/{repo}"
        )


@router.get("/validate")
async def validate_repo(
    url: str = Query(..., description="GitHub repository URL"),
    github_service: GitHubService = Depends(get_github_service),
):
    """
    验证仓库 URL 是否有效
    """
    try:
        owner, repo = parse_repo_url(url)
        info = await github_service.get_repo_info(owner, repo)
        return {
            "valid": True,
            "owner": owner,
            "repo": repo,
            "full_name": info.full_name,
            "stars": info.stars,
        }
    except ValueError as e:
        return {
            "valid": False,
            "error": str(e),
        }
    except Exception:
        return {
            "valid": False,
            "error": "Repository not found or not accessible",
        }