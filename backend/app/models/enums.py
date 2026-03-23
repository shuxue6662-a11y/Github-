"""
枚举定义
"""
from enum import Enum


class MusicStyle(str, Enum):
    """音乐风格"""
    ELECTRONIC = "electronic"
    CLASSICAL = "classical"
    ROCK = "rock"
    JAZZ = "jazz"
    AMBIENT = "ambient"
    CHIPTUNE = "chiptune"
    LOFI = "lofi"
    ORCHESTRAL = "orchestral"


class CommitType(str, Enum):
    """Commit 类型"""
    FEATURE = "feature"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    STYLE = "style"
    TEST = "test"
    CHORE = "chore"
    MERGE = "merge"
    BREAKING = "breaking"
    PERFORMANCE = "performance"
    OTHER = "other"


class ScaleType(str, Enum):
    """音阶类型"""
    C_MAJOR = "C_MAJOR"
    A_MINOR = "A_MINOR"
    G_MAJOR = "G_MAJOR"
    E_MINOR = "E_MINOR"
    D_MAJOR = "D_MAJOR"
    B_MINOR = "B_MINOR"
    F_MAJOR = "F_MAJOR"
    D_MINOR = "D_MINOR"
    PENTATONIC_MAJOR = "PENTATONIC_MAJOR"
    PENTATONIC_MINOR = "PENTATONIC_MINOR"
    BLUES = "BLUES"
    DORIAN = "DORIAN"
    MIXOLYDIAN = "MIXOLYDIAN"