"""
Pydantic 数据模型
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


# ============ Enums ============

class MusicStyle(str, Enum):
    """音乐风格"""
    ELECTRONIC = "electronic"
    CLASSICAL = "classical"
    ROCK = "rock"
    JAZZ = "jazz"
    AMBIENT = "ambient"
    CHIPTUNE = "chiptune"


class CommitType(str, Enum):
    """Commit 类型（通过消息分析）"""
    FEATURE = "feature"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    STYLE = "style"
    TEST = "test"
    CHORE = "chore"
    MERGE = "merge"
    OTHER = "other"


# ============ Request Models ============

class RepoRequest(BaseModel):
    """仓库请求"""
    repo_url: str = Field(..., example="https://github.com/facebook/react")
    style: MusicStyle = MusicStyle.ELECTRONIC
    max_commits: int = Field(default=200, ge=10, le=500)
    branch: str = "main"


class MusicGenerateRequest(BaseModel):
    """音乐生成请求"""
    repo_url: str
    style: MusicStyle = MusicStyle.ELECTRONIC
    bpm: int = Field(default=120, ge=60, le=200)
    scale: str = "C_MAJOR"
    max_commits: int = Field(default=200, ge=10, le=500)


# ============ Internal Models ============

class CommitData(BaseModel):
    """Commit 数据"""
    sha: str
    message: str
    author: str
    timestamp: datetime
    additions: int
    deletions: int
    files_changed: int
    commit_type: CommitType


class CommitAnalysis(BaseModel):
    """Commit 分析结果"""
    total_commits: int
    date_range_days: int
    avg_commits_per_day: float
    top_contributors: list[dict]
    commit_type_distribution: dict[str, int]
    activity_hours: list[int]  # 24小时活跃度分布
    commits: list[CommitData]


class NoteEvent(BaseModel):
    """音符事件"""
    pitch: int          # MIDI 音高 (0-127)
    velocity: int       # 力度 (0-127)
    start_time: float   # 开始时间（拍）
    duration: float     # 持续时间（拍）
    channel: int = 0    # MIDI 通道


class TrackData(BaseModel):
    """音轨数据"""
    name: str
    instrument: int     # MIDI 乐器编号
    notes: list[NoteEvent]


class MusicData(BaseModel):
    """音乐数据（供前端 Tone.js 使用）"""
    bpm: int
    time_signature: tuple[int, int] = (4, 4)
    total_duration: float  # 秒
    tracks: list[TrackData]


# ============ Response Models ============

class RepoInfoResponse(BaseModel):
    """仓库信息响应"""
    name: str
    full_name: str
    description: str | None
    stars: int
    forks: int
    language: str | None
    created_at: datetime
    updated_at: datetime


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
    duration: float
    music_data: MusicData
    midi_base64: str | None = None  # Base64 编码的 MIDI 文件


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: str | None = None