"""
乐器映射规则
"""
from app.models.schemas import CommitType, MusicStyle


# General MIDI 乐器编号
# https://en.wikipedia.org/wiki/General_MIDI#Program_change_events

class GMInstruments:
    """General MIDI 乐器常量"""
    
    # Piano
    ACOUSTIC_GRAND_PIANO = 0
    ELECTRIC_PIANO = 4
    
    # Chromatic Percussion
    CELESTA = 8
    MUSIC_BOX = 10
    VIBRAPHONE = 11
    MARIMBA = 12
    
    # Organ
    CHURCH_ORGAN = 19
    
    # Guitar
    ACOUSTIC_GUITAR_NYLON = 24
    ELECTRIC_GUITAR_CLEAN = 27
    ELECTRIC_GUITAR_DISTORTION = 30
    
    # Bass
    ACOUSTIC_BASS = 32
    ELECTRIC_BASS_FINGER = 33
    SLAP_BASS = 36
    SYNTH_BASS = 38
    
    # Strings
    VIOLIN = 40
    VIOLA = 41
    CELLO = 42
    STRINGS = 48
    ORCHESTRAL_HARP = 46
    
    # Brass
    TRUMPET = 56
    FRENCH_HORN = 60
    
    # Synth Lead
    SYNTH_LEAD_SQUARE = 80
    SYNTH_LEAD_SAW = 81
    
    # Synth Pad
    SYNTH_PAD_WARM = 89
    SYNTH_PAD_CHOIR = 91
    
    # Synth Effects
    SYNTH_FX_RAIN = 96
    SYNTH_FX_CRYSTAL = 98
    
    # Percussion (Channel 10)
    DRUMS = 128  # 特殊标记


# 文件类型 → 乐器
FILE_TYPE_INSTRUMENTS = {
    # 前端
    ".js": GMInstruments.SYNTH_LEAD_SAW,
    ".ts": GMInstruments.SYNTH_LEAD_SQUARE,
    ".jsx": GMInstruments.SYNTH_LEAD_SAW,
    ".tsx": GMInstruments.SYNTH_LEAD_SQUARE,
    ".vue": GMInstruments.ELECTRIC_PIANO,
    ".css": GMInstruments.MUSIC_BOX,
    ".scss": GMInstruments.CELESTA,
    ".html": GMInstruments.VIBRAPHONE,
    
    # 后端
    ".py": GMInstruments.ACOUSTIC_GRAND_PIANO,
    ".java": GMInstruments.CHURCH_ORGAN,
    ".go": GMInstruments.MARIMBA,
    ".rs": GMInstruments.CELLO,
    ".rb": GMInstruments.ACOUSTIC_GUITAR_NYLON,
    ".php": GMInstruments.ELECTRIC_GUITAR_CLEAN,
    
    # 系统
    ".c": GMInstruments.STRINGS,
    ".cpp": GMInstruments.VIOLIN,
    ".h": GMInstruments.VIOLA,
    
    # 数据/配置
    ".json": GMInstruments.SYNTH_PAD_WARM,
    ".yaml": GMInstruments.SYNTH_PAD_WARM,
    ".yml": GMInstruments.SYNTH_PAD_WARM,
    ".toml": GMInstruments.SYNTH_PAD_WARM,
    ".md": GMInstruments.ORCHESTRAL_HARP,
    
    # 默认
    "default": GMInstruments.ELECTRIC_PIANO,
}


# Commit 类型 → 乐器/音色特征
COMMIT_TYPE_MUSIC = {
    CommitType.FEATURE: {
        "instrument": GMInstruments.SYNTH_LEAD_SAW,
        "velocity_range": (90, 120),     # 明亮有力
        "pitch_offset": 12,               # 高一个八度
        "note_duration": 1.0,
    },
    CommitType.FIX: {
        "instrument": GMInstruments.SYNTH_BASS,
        "velocity_range": (60, 90),      # 低沉稳重
        "pitch_offset": -12,              # 低一个八度
        "note_duration": 0.5,
    },
    CommitType.MERGE: {
        "instrument": GMInstruments.STRINGS,
        "velocity_range": (100, 127),    # 高潮
        "pitch_offset": 0,
        "note_duration": 2.0,             # 长音
    },
    CommitType.DOCS: {
        "instrument": GMInstruments.MUSIC_BOX,
        "velocity_range": (40, 70),      # 轻柔
        "pitch_offset": 24,               # 高两个八度
        "note_duration": 0.25,
    },
    CommitType.REFACTOR: {
        "instrument": GMInstruments.ELECTRIC_PIANO,
        "velocity_range": (70, 100),
        "pitch_offset": 0,
        "note_duration": 0.75,
    },
    CommitType.CHORE: {
        "instrument": GMInstruments.VIBRAPHONE,
        "velocity_range": (50, 80),
        "pitch_offset": 12,
        "note_duration": 0.5,
    },
    CommitType.TEST: {
        "instrument": GMInstruments.MARIMBA,
        "velocity_range": (60, 90),
        "pitch_offset": 0,
        "note_duration": 0.25,
    },
    CommitType.STYLE: {
        "instrument": GMInstruments.CELESTA,
        "velocity_range": (40, 70),
        "pitch_offset": 12,
        "note_duration": 0.5,
    },
    CommitType.OTHER: {
        "instrument": GMInstruments.ACOUSTIC_GRAND_PIANO,
        "velocity_range": (60, 90),
        "pitch_offset": 0,
        "note_duration": 0.5,
    },
}


# 风格 → 整体配置
STYLE_CONFIGS = {
    MusicStyle.ELECTRONIC: {
        "primary_instruments": [
            GMInstruments.SYNTH_LEAD_SAW,
            GMInstruments.SYNTH_BASS,
            GMInstruments.SYNTH_PAD_WARM,
        ],
        "bpm_range": (120, 140),
        "note_density": 1.5,
        "use_drums": True,
    },
    MusicStyle.CLASSICAL: {
        "primary_instruments": [
            GMInstruments.ACOUSTIC_GRAND_PIANO,
            GMInstruments.STRINGS,
            GMInstruments.VIOLIN,
        ],
        "bpm_range": (70, 100),
        "note_density": 0.8,
        "use_drums": False,
    },
    MusicStyle.ROCK: {
        "primary_instruments": [
            GMInstruments.ELECTRIC_GUITAR_DISTORTION,
            GMInstruments.ELECTRIC_BASS_FINGER,
            GMInstruments.ACOUSTIC_GRAND_PIANO,
        ],
        "bpm_range": (100, 130),
        "note_density": 1.2,
        "use_drums": True,
    },
    MusicStyle.JAZZ: {
        "primary_instruments": [
            GMInstruments.ELECTRIC_PIANO,
            GMInstruments.ACOUSTIC_BASS,
            GMInstruments.VIBRAPHONE,
        ],
        "bpm_range": (80, 120),
        "note_density": 1.0,
        "use_drums": True,
    },
    MusicStyle.AMBIENT: {
        "primary_instruments": [
            GMInstruments.SYNTH_PAD_CHOIR,
            GMInstruments.SYNTH_FX_CRYSTAL,
            GMInstruments.ORCHESTRAL_HARP,
        ],
        "bpm_range": (60, 80),
        "note_density": 0.5,
        "use_drums": False,
    },
    MusicStyle.CHIPTUNE: {
        "primary_instruments": [
            GMInstruments.SYNTH_LEAD_SQUARE,
            GMInstruments.SYNTH_BASS,
            GMInstruments.MUSIC_BOX,
        ],
        "bpm_range": (130, 160),
        "note_density": 2.0,
        "use_drums": True,
    },
}