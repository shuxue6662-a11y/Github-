"""
Pydantic 数据模型
"""
from pydantic import BaseModel, Field, field_validator, HttpUrl
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

from app.models.enums import MusicStyle, CommitType, ScaleType


# ============ Request Models ============

class RepoRequest(BaseModel):
    """仓库请求"""
    repo_url: str = Field(
        ..., 
        min_length=1,
        example="https://github.com/facebook/react"
    )
    branch: str = Field(default="main", min_length=1)
    max_commits: int = Field(default=200, ge=10, le=500)
    
    @field_validator('repo_url')
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        v = v.strip().rstrip('/')
        if not v:
            raise ValueError("Repository URL cannot be empty")
        return v


class MusicGenerateRequest(BaseModel):
    """音乐生成请求"""
    repo_url: str = Field(..., min_length=1)
    style: MusicStyle = Field(default=MusicStyle.ELECTRONIC)
    bpm: int = Field(default=120, ge=60, le=200)
    scale: ScaleType = Field(default=ScaleType.C_MAJOR)
    max_commits: int = Field(default=200, ge=10, le=500)
    branch: str = Field(default="main")
    
    # 高级选项
    include_drums: bool = Field(default=True)
    include_bass: bool = Field(default=True)
    include_chords: bool = Field(default=True)
    melody_complexity: float = Field(default=0.5, ge=0.0, le=1.0)


# ============ Internal Models ============

class CommitData(BaseModel):
    """Commit 数据"""
    sha: str
    message: str
    author: str
    author_email: str = ""
    timestamp: datetime
    additions: int = 0
    deletions: int = 0
    files_changed: int = 0
    file_types: List[str] = Field(default_factory=list)
    commit_type: CommitType = CommitType.OTHER
    
    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions
    
    @property
    def impact_score(self) -> float:
        """计算提交影响分数 (0-1)"""
        changes = self.total_changes
        if changes == 0:
            return 0.1
        elif changes < 10:
            return 0.2
        elif changes < 50:
            return 0.4
        elif changes < 200:
            return 0.6
        elif changes < 500:
            return 0.8
        else:
            return 1.0


class ContributorStats(BaseModel):
    """贡献者统计"""
    name: str
    email: str = ""
    commits: int
    additions: int = 0
    deletions: int = 0
    percentage: float = 0.0


class CommitAnalysis(BaseModel):
    """Commit 分析结果"""
    total_commits: int
    date_range_days: int
    avg_commits_per_day: float
    total_additions: int
    total_deletions: int
    top_contributors: List[ContributorStats]
    commit_type_distribution: Dict[str, int]
    file_type_distribution: Dict[str, int]
    activity_hours: List[int]  # 24小时活跃度
    activity_weekdays: List[int]  # 7天活跃度
    commits: List[CommitData]
    
    # 派生特征
    activity_level: str = "moderate"  # low, moderate, high, intense
    dominant_type: str = "other"


class NoteEvent(BaseModel):
    """音符事件"""
    pitch: int = Field(ge=0, le=127)
    velocity: int = Field(ge=0, le=127)
    start_time: float = Field(ge=0)
    duration: float = Field(gt=0)
    channel: int = Field(default=0, ge=0, le=15)


class TrackData(BaseModel):
    """音轨数据"""
    name: str
    instrument: int = Field(ge=0)
    notes: List[NoteEvent]
    volume: float = Field(default=1.0, ge=0.0, le=1.0)
    pan: float = Field(default=0.0, ge=-1.0, le=1.0)  # -1 左, 0 中, 1 右


class MusicData(BaseModel):
    """音乐数据"""
    bpm: int
    time_signature: Tuple[int, int] = (4, 4)
    total_beats: float
    total_duration: float  # 秒
    scale: str
    style: str
    tracks: List[TrackData]
    
    # 元数据
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Response Models ============

class RepoInfoResponse(BaseModel):
    """仓库信息响应"""
    name: str
    full_name: str
    description: Optional[str] = None
    stars: int
    forks: int
    watchers: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    default_branch: str = "main"
    open_issues: int = 0
    license: Optional[str] = None


class AnalysisResponse(BaseModel):
    """分析结果响应"""
    repo_info: RepoInfoResponse
    analysis: CommitAnalysis


class MusicResponse(BaseModel):
    """音乐生成响应"""
    success: bool
    repo_name: str
    style: MusicStyle
    bpm: int
    scale: str
    duration: float
    total_tracks: int
    total_notes: int
    music_data: MusicData
    midi_base64: Optional[str] = None
    
    # 统计
    commits_processed: int
    generation_time_ms: float


class StyleInfo(BaseModel):
    """风格信息"""
    id: str
    name: str
    description: str
    emoji: str
    bpm_range: Tuple[int, int]


class StylesResponse(BaseModel):
    """风格列表响应"""
    styles: List[StyleInfo]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None