"""
GitHub API 服务
"""
import re
from datetime import datetime
from typing import Optional
import httpx
from cachetools import TTLCache

from app.config import get_settings
from app.models.schemas import RepoInfoResponse, CommitData, CommitType


class GitHubService:
    """GitHub 数据获取服务"""
    
    def __init__(self, token: Optional[str] = None):
        settings = get_settings()
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = settings.GITHUB_API_BASE
        self.cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)
        
        # HTTP headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoRhythm/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def parse_repo_url(self, url: str) -> tuple[str, str]:
        """
        解析 GitHub URL 获取 owner 和 repo
        
        支持格式：
        - https://github.com/owner/repo
        - github.com/owner/repo
        - owner/repo
        """
        # 清理 URL
        url = url.strip().rstrip('/')
        
        # 匹配模式
        patterns = [
            r'github\.com/([^/]+)/([^/]+)',  # 完整 URL
            r'^([^/]+)/([^/]+)$',             # owner/repo 格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                # 移除 .git 后缀
                repo = repo.replace('.git', '')
                return owner, repo
        
        raise ValueError(f"Invalid GitHub repository URL: {url}")
    
    async def get_repo_info(self, owner: str, repo: str) -> RepoInfoResponse:
        """获取仓库基本信息"""
        cache_key = f"repo:{owner}/{repo}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
        
        result = RepoInfoResponse(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            language=data.get("language"),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
        )
        
        self.cache[cache_key] = result
        return result
    
    async def get_commits(
        self, 
        owner: str, 
        repo: str, 
        branch: str = "main",
        max_count: int = 200
    ) -> list[CommitData]:
        """
        获取 commit 列表
        """
        commits = []
        page = 1
        per_page = 100
        
        async with httpx.AsyncClient() as client:
            while len(commits) < max_count:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/commits",
                    params={
                        "sha": branch,
                        "per_page": min(per_page, max_count - len(commits)),
                        "page": page,
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                
                # 处理 branch 不存在的情况
                if response.status_code == 404:
                    # 尝试 master 分支
                    if branch == "main":
                        return await self.get_commits(owner, repo, "master", max_count)
                    raise ValueError(f"Branch not found: {branch}")
                
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                for item in data:
                    commit_data = await self._parse_commit(client, owner, repo, item)
                    commits.append(commit_data)
                
                page += 1
        
        return commits
    
    async def _parse_commit(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        item: dict
    ) -> CommitData:
        """解析单个 commit"""
        commit = item["commit"]
        sha = item["sha"]
        
        # 获取 commit 详情（包含修改统计）
        detail_response = await client.get(
            f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}",
            headers=self.headers,
            timeout=30.0
        )
        detail = detail_response.json() if detail_response.status_code == 200 else {}
        stats = detail.get("stats", {})
        
        message = commit["message"]
        
        return CommitData(
            sha=sha,
            message=message,
            author=commit["author"]["name"] if commit.get("author") else "Unknown",
            timestamp=datetime.fromisoformat(
                commit["author"]["date"].replace("Z", "+00:00")
            ),
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            files_changed=len(detail.get("files", [])),
            commit_type=self._classify_commit(message),
        )
    
    def _classify_commit(self, message: str) -> CommitType:
        """根据 commit message 分类"""
        message_lower = message.lower()
        
        patterns = {
            CommitType.MERGE: [r'^merge', r'merge pull request', r'merge branch'],
            CommitType.FEATURE: [r'^feat', r'add ', r'new ', r'implement'],
            CommitType.FIX: [r'^fix', r'bug', r'patch', r'resolve', r'close #'],
            CommitType.REFACTOR: [r'^refactor', r'restructure', r'reorganize'],
            CommitType.DOCS: [r'^docs', r'readme', r'documentation', r'comment'],
            CommitType.STYLE: [r'^style', r'format', r'lint', r'prettier'],
            CommitType.TEST: [r'^test', r'spec', r'coverage'],
            CommitType.CHORE: [r'^chore', r'bump', r'release', r'version', r'update dep'],
        }
        
        for commit_type, keywords in patterns.items():
            for keyword in keywords:
                if re.search(keyword, message_lower):
                    return commit_type
        
        return CommitType.OTHER