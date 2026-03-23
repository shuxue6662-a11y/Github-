"""
GitHub API 服务
"""
import re
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
from cachetools import TTLCache

from app.config import get_settings
from app.models.schemas import RepoInfoResponse, CommitData
from app.models.enums import CommitType
from app.utils.helpers import parse_repo_url, get_file_extension


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
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _get_client(self) -> httpx.AsyncClient:
        """创建 HTTP 客户端"""
        return httpx.AsyncClient(
            timeout=30.0,
            headers=self.headers,
            follow_redirects=True,
        )
    
    async def get_repo_info(self, owner: str, repo: str) -> RepoInfoResponse:
        """获取仓库基本信息"""
        cache_key = f"repo:{owner}/{repo}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        async with self._get_client() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}"
            )
            
            if response.status_code == 404:
                raise ValueError(f"Repository not found: {owner}/{repo}")
            elif response.status_code == 403:
                raise ValueError("API rate limit exceeded. Please try again later.")
            
            response.raise_for_status()
            data = response.json()
        
        result = RepoInfoResponse(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            language=data.get("language"),
            topics=data.get("topics", []),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            default_branch=data.get("default_branch", "main"),
            open_issues=data.get("open_issues_count", 0),
            license=data.get("license", {}).get("name") if data.get("license") else None,
        )
        
        self.cache[cache_key] = result
        return result
    
    async def get_commits(
        self, 
        owner: str, 
        repo: str, 
        branch: str = "main",
        max_count: int = 200,
    ) -> List[CommitData]:
        """
        获取 commit 列表
        """
        commits = []
        page = 1
        per_page = min(100, max_count)
        
        async with self._get_client() as client:
            while len(commits) < max_count:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/commits",
                    params={
                        "sha": branch,
                        "per_page": per_page,
                        "page": page,
                    },
                )
                
                # 处理 branch 不存在的情况
                if response.status_code == 404:
                    if branch == "main":
                        # 尝试 master 分支
                        return await self.get_commits(owner, repo, "master", max_count)
                    raise ValueError(f"Branch not found: {branch}")
                elif response.status_code == 409:
                    # Empty repository
                    return []
                elif response.status_code == 403:
                    raise ValueError("API rate limit exceeded")
                
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                # 批量获取 commit 详情
                tasks = [
                    self._fetch_commit_detail(client, owner, repo, item)
                    for item in data[:max_count - len(commits)]
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, CommitData):
                        commits.append(result)
                
                if len(data) < per_page:
                    break
                
                page += 1
        
        return commits
    
    async def _fetch_commit_detail(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        item: Dict[str, Any],
    ) -> CommitData:
        """获取单个 commit 的详细信息"""
        commit = item["commit"]
        sha = item["sha"]
        message = commit.get("message", "")
        
        # 获取 commit 详情（包含修改统计）
        try:
            detail_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
            )
            
            if detail_response.status_code == 200:
                detail = detail_response.json()
                stats = detail.get("stats", {})
                files = detail.get("files", [])
                file_types = list(set(
                    get_file_extension(f.get("filename", ""))
                    for f in files
                    if get_file_extension(f.get("filename", ""))
                ))
            else:
                stats = {}
                files = []
                file_types = []
        except Exception:
            stats = {}
            files = []
            file_types = []
        
        # 解析作者信息
        author_info = commit.get("author") or {}
        author_name = author_info.get("name", "Unknown")
        author_email = author_info.get("email", "")
        
        # 解析时间戳
        timestamp_str = author_info.get("date", "")
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            timestamp = datetime.utcnow()
        
        return CommitData(
            sha=sha,
            message=message,
            author=author_name,
            author_email=author_email,
            timestamp=timestamp,
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            files_changed=len(files),
            file_types=file_types,
            commit_type=self._classify_commit(message),
        )
    
    def _classify_commit(self, message: str) -> CommitType:
        """根据 commit message 分类"""
        if not message:
            return CommitType.OTHER
        
        message_lower = message.lower().strip()
        first_line = message_lower.split('\n')[0]
        
        # 按优先级匹配
        patterns = [
            # Merge commits
            (CommitType.MERGE, [
                r'^merge\s',
                r'^merge\s+pull\s+request',
                r'^merge\s+branch',
                r"^merged?\s+(?:in\s+)?['\"]",
            ]),
            # Breaking changes
            (CommitType.BREAKING, [
                r'breaking[\s\-_]?change',
                r'!:',
                r'\bBREAKING\b',
            ]),
            # Features
            (CommitType.FEATURE, [
                r'^feat[\s:\(]',
                r'^feature[\s:\(]',
                r'^add[\s:\(]',
                r'^added?\s',
                r'^implement',
                r'^new\s',
                r'^create[sd]?\s',
                r'^support\s',
            ]),
            # Bug fixes
            (CommitType.FIX, [
                r'^fix[\s:\(]',
                r'^bug[\s:\(]',
                r'^patch[\s:\(]',
                r'^resolve[sd]?\s',
                r'^close[sd]?\s+#',
                r'^hotfix',
                r'^repair',
            ]),
            # Performance
            (CommitType.PERFORMANCE, [
                r'^perf[\s:\(]',
                r'^performance',
                r'^optimi[sz]e',
                r'^speed\s*up',
                r'^faster',
            ]),
            # Refactoring
            (CommitType.REFACTOR, [
                r'^refactor[\s:\(]',
                r'^restructure',
                r'^reorgani[sz]e',
                r'^rewrite',
                r'^rework',
                r'^simplif',
                r'^clean[\s\-]?up',
            ]),
            # Documentation
            (CommitType.DOCS, [
                r'^docs?[\s:\(]',
                r'^documentation',
                r'^readme',
                r'^\[docs?\]',
                r'^comment',
                r'^update\s+readme',
            ]),
            # Tests
            (CommitType.TEST, [
                r'^test[\s:\(]',
                r'^tests?[\s:\(]',
                r'^spec[\s:\(]',
                r'^coverage',
                r'^\[test',
                r'^add\s+test',
            ]),
            # Style/formatting
            (CommitType.STYLE, [
                r'^style[\s:\(]',
                r'^format[\s:\(]',
                r'^lint[\s:\(]',
                r'^prettier',
                r'^eslint',
                r'^whitespace',
                r'^indent',
            ]),
            # Chores
            (CommitType.CHORE, [
                r'^chore[\s:\(]',
                r'^build[\s:\(]',
                r'^ci[\s:\(]',
                r'^bump[\s:\(]',
                r'^release[\s:\(]',
                r'^version[\s:\(]',
                r'^update\s+dep',
                r'^upgrade',
                r'^deps[\s:\(]',
                r'^\[skip',
                r'^config',
            ]),
        ]
        
        for commit_type, keywords in patterns:
            for keyword in keywords:
                if re.search(keyword, first_line):
                    return commit_type
        
        return CommitType.OTHER