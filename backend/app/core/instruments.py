"""
乐器映射规则
"""
from typing import Dict, List, Tuple, Any
from app.models.enums import CommitType, MusicStyle


class GMInstruments:
    """General MIDI 乐器常量"""
    
    # Piano (0-7)
    ACOUSTIC_GRAND_PIANO = 0
    BRIGHT_ACOUSTIC_PIANO = 1
    ELECTRIC_GRAND_PIANO = 2
    HONKY_TONK_PIANO = 3
    ELECTRIC_PIANO_1 = 4
    ELECTRIC_PIANO_2 = 5
    HARPSICHORD = 6
    CLAVINET = 7
    
    # Chromatic Percussion (8-15)
    CELESTA = 8
    GLOCKENSPIEL = 9
    MUSIC_BOX = 10
    VIBRAPHONE = 11
    MARIMBA = 12
    XYLOPHONE = 13
    TUBULAR_BELLS = 14
    DULCIMER = 15
    
    # Organ (16-23)
    DRAWBAR_ORGAN = 16
    PERCUSSIVE_ORGAN = 17
    ROCK_ORGAN = 18
    CHURCH_ORGAN = 19
    REED_ORGAN = 20
    ACCORDION = 21
    HARMONICA = 22
    TANGO_ACCORDION = 23
    
    # Guitar (24-31)
    ACOUSTIC_GUITAR_NYLON = 24
    ACOUSTIC_GUITAR_STEEL = 25
    ELECTRIC_GUITAR_JAZZ = 26
    ELECTRIC_GUITAR_CLEAN = 27
    ELECTRIC_GUITAR_MUTED = 28
    OVERDRIVEN_GUITAR = 29
    DISTORTION_GUITAR = 30
    GUITAR_HARMONICS = 31
    
    # Bass (32-39)
    ACOUSTIC_BASS = 32
    ELECTRIC_BASS_FINGER = 33
    ELECTRIC_BASS_PICK = 34
    FRETLESS_BASS = 35
    SLAP_BASS_1 = 36
    SLAP_BASS_2 = 37
    SYNTH_BASS_1 = 38
    SYNTH_BASS_2 = 39
    
    # Strings (40-47)
    VIOLIN = 40
    VIOLA = 41
    CELLO = 42
    CONTRABASS = 43
    TREMOLO_STRINGS = 44
    PIZZICATO_STRINGS = 45
    ORCHESTRAL_HARP = 46
    TIMPANI = 47
    
    # Ensemble (48-55)
    STRING_ENSEMBLE_1 = 48
    STRING_ENSEMBLE_2 = 49
    SYNTH_STRINGS_1 = 50
    SYNTH_STRINGS_2 = 51
    CHOIR_AAHS = 52
    VOICE_OOHS = 53
    SYNTH_VOICE = 54
    ORCHESTRA_HIT = 55
    
    # Brass (56-63)
    TRUMPET = 56
    TROMBONE = 57
    TUBA = 58
    MUTED_TRUMPET = 59
    FRENCH_HORN = 60
    BRASS_SECTION = 61
    SYNTH_BRASS_1 = 62
    SYNTH_BRASS_2 = 63
    
    # Reed (64-71)
    SOPRANO_SAX = 64
    ALTO_SAX = 65
    TENOR_SAX = 66
    BARITONE_SAX = 67
    OBOE = 68
    ENGLISH_HORN = 69
    BASSOON = 70
    CLARINET = 71
    
    # Pipe (72-79)
    PICCOLO = 72
    FLUTE = 73
    RECORDER = 74
    PAN_FLUTE = 75
    BLOWN_BOTTLE = 76
    SHAKUHACHI = 77
    WHISTLE = 78
    OCARINA = 79
    
    # Synth Lead (80-87)
    LEAD_SQUARE = 80
    LEAD_SAWTOOTH = 81
    LEAD_CALLIOPE = 82
    LEAD_CHIFF = 83
    LEAD_CHARANG = 84
    LEAD_VOICE = 85
    LEAD_FIFTHS = 86
    LEAD_BASS_LEAD = 87
    
    # Synth Pad (88-95)
    PAD_NEW_AGE = 88
    PAD_WARM = 89
    PAD_POLYSYNTH = 90
    PAD_CHOIR = 91
    PAD_BOWED = 92
    PAD_METALLIC = 93
    PAD_HALO = 94
    PAD_SWEEP = 95
    
    # Synth Effects (96-103)
    FX_RAIN = 96
    FX_SOUNDTRACK = 97
    FX_CRYSTAL = 98
    FX_ATMOSPHERE = 99
    FX_BRIGHTNESS = 100
    FX_GOBLINS = 101
    FX_ECHOES = 102
    FX_SCI_FI = 103
    
    # Ethnic (104-111)
    SITAR = 104
    BANJO = 105
    SHAMISEN = 106
    KOTO = 107
    KALIMBA = 108
    BAGPIPE = 109
    FIDDLE = 110
    SHANAI = 111
    
    # Percussive (112-119)
    TINKLE_BELL = 112
    AGOGO = 113
    STEEL_DRUMS = 114
    WOODBLOCK = 115
    TAIKO_DRUM = 116
    MELODIC_TOM = 117
    SYNTH_DRUM = 118
    REVERSE_CYMBAL = 119
    
    # Sound Effects (120-127)
    GUITAR_FRET_NOISE = 120
    BREATH_NOISE = 121
    SEASHORE = 122
    BIRD_TWEET = 123
    TELEPHONE_RING = 124
    HELICOPTER = 125
    APPLAUSE = 126
    GUNSHOT = 127
    
    # 特殊标记
    DRUMS = 128


# GM 鼓组音符映射 (Channel 10)
class DrumNotes:
    """GM 鼓组音符"""
    ACOUSTIC_BASS_DRUM = 35
    BASS_DRUM_1 = 36
    SIDE_STICK = 37
    ACOUSTIC_SNARE = 38
    HAND_CLAP = 39
    ELECTRIC_SNARE = 40
    LOW_FLOOR_TOM = 41
    CLOSED_HI_HAT = 42
    HIGH_FLOOR_TOM = 43
    PEDAL_HI_HAT = 44
    LOW_TOM = 45
    OPEN_HI_HAT = 46
    LOW_MID_TOM = 47
    HI_MID_TOM = 48
    CRASH_CYMBAL_1 = 49
    HIGH_TOM = 50
    RIDE_CYMBAL_1 = 51
    CHINESE_CYMBAL = 52
    RIDE_BELL = 53
    TAMBOURINE = 54
    SPLASH_CYMBAL = 55
    COWBELL = 56
    CRASH_CYMBAL_2 = 57
    VIBRASLAP = 58
    RIDE_CYMBAL_2 = 59
    HI_BONGO = 60
    LOW_BONGO = 61
    MUTE_HI_CONGA = 62
    OPEN_HI_CONGA = 63
    LOW_CONGA = 64
    HIGH_TIMBALE = 65
    LOW_TIMBALE = 66
    HIGH_AGOGO = 67
    LOW_AGOGO = 68
    CABASA = 69
    MARACAS = 70
    SHORT_WHISTLE = 71
    LONG_WHISTLE = 72
    SHORT_GUIRO = 73
    LONG_GUIRO = 74
    CLAVES = 75
    HI_WOOD_BLOCK = 76
    LOW_WOOD_BLOCK = 77
    MUTE_CUICA = 78
    OPEN_CUICA = 79
    MUTE_TRIANGLE = 80
    OPEN_TRIANGLE = 81


# 文件类型 → 乐器
FILE_TYPE_INSTRUMENTS: Dict[str, int] = {
    # 前端
    ".js": GMInstruments.LEAD_SAWTOOTH,
    ".jsx": GMInstruments.LEAD_SAWTOOTH,
    ".ts": GMInstruments.LEAD_SQUARE,
    ".tsx": GMInstruments.LEAD_SQUARE,
    ".vue": GMInstruments.ELECTRIC_PIANO_1,
    ".svelte": GMInstruments.ELECTRIC_PIANO_2,
    ".css": GMInstruments.MUSIC_BOX,
    ".scss": GMInstruments.CELESTA,
    ".sass": GMInstruments.CELESTA,
    ".less": GMInstruments.GLOCKENSPIEL,
    ".html": GMInstruments.VIBRAPHONE,
    
    # 后端
    ".py": GMInstruments.ACOUSTIC_GRAND_PIANO,
    ".java": GMInstruments.CHURCH_ORGAN,
    ".kt": GMInstruments.ROCK_ORGAN,
    ".go": GMInstruments.MARIMBA,
    ".rs": GMInstruments.CELLO,
    ".rb": GMInstruments.ACOUSTIC_GUITAR_NYLON,
    ".php": GMInstruments.ELECTRIC_GUITAR_CLEAN,
    ".cs": GMInstruments.STRING_ENSEMBLE_1,
    ".swift": GMInstruments.FLUTE,
    ".scala": GMInstruments.CLARINET,
    
    # 系统
    ".c": GMInstruments.VIOLIN,
    ".cpp": GMInstruments.VIOLA,
    ".cc": GMInstruments.VIOLA,
    ".h": GMInstruments.PIZZICATO_STRINGS,
    ".hpp": GMInstruments.PIZZICATO_STRINGS,
    ".asm": GMInstruments.SYNTH_BASS_1,
    ".s": GMInstruments.SYNTH_BASS_2,
    
    # 脚本
    ".sh": GMInstruments.WOODBLOCK,
    ".bash": GMInstruments.WOODBLOCK,
    ".zsh": GMInstruments.WOODBLOCK,
    ".ps1": GMInstruments.STEEL_DRUMS,
    
    # 数据/配置
    ".json": GMInstruments.PAD_WARM,
    ".yaml": GMInstruments.PAD_NEW_AGE,
    ".yml": GMInstruments.PAD_NEW_AGE,
    ".toml": GMInstruments.PAD_POLYSYNTH,
    ".xml": GMInstruments.PAD_CHOIR,
    ".ini": GMInstruments.PAD_BOWED,
    
    # 文档
    ".md": GMInstruments.ORCHESTRAL_HARP,
    ".rst": GMInstruments.ORCHESTRAL_HARP,
    ".txt": GMInstruments.KALIMBA,
    
    # SQL
    ".sql": GMInstruments.TIMPANI,
    
    # 移动端
    ".dart": GMInstruments.XYLOPHONE,
    ".m": GMInstruments.OBOE,
    ".mm": GMInstruments.ENGLISH_HORN,
    
    # 默认
    "default": GMInstruments.ELECTRIC_PIANO_1,
}


# Commit 类型 → 音乐特征
COMMIT_TYPE_MUSIC: Dict[CommitType, Dict[str, Any]] = {
    CommitType.FEATURE: {
        "instrument": GMInstruments.LEAD_SAWTOOTH,
        "velocity_range": (85, 115),
        "pitch_offset": 12,
        "note_duration_range": (0.75, 1.5),
        "add_harmony": True,
        "energy": 0.8,
    },
    CommitType.FIX: {
        "instrument": GMInstruments.SYNTH_BASS_1,
        "velocity_range": (60, 85),
        "pitch_offset": -12,
        "note_duration_range": (0.25, 0.75),
        "add_harmony": False,
        "energy": 0.5,
    },
    CommitType.MERGE: {
        "instrument": GMInstruments.STRING_ENSEMBLE_1,
        "velocity_range": (95, 127),
        "pitch_offset": 0,
        "note_duration_range": (1.5, 3.0),
        "add_harmony": True,
        "energy": 1.0,
    },
    CommitType.DOCS: {
        "instrument": GMInstruments.MUSIC_BOX,
        "velocity_range": (40, 70),
        "pitch_offset": 24,
        "note_duration_range": (0.125, 0.375),
        "add_harmony": False,
        "energy": 0.2,
    },
    CommitType.REFACTOR: {
        "instrument": GMInstruments.ELECTRIC_PIANO_1,
        "velocity_range": (65, 95),
        "pitch_offset": 0,
        "note_duration_range": (0.5, 1.0),
        "add_harmony": True,
        "energy": 0.6,
    },
    CommitType.CHORE: {
        "instrument": GMInstruments.VIBRAPHONE,
        "velocity_range": (50, 75),
        "pitch_offset": 12,
        "note_duration_range": (0.25, 0.5),
        "add_harmony": False,
        "energy": 0.3,
    },
    CommitType.TEST: {
        "instrument": GMInstruments.MARIMBA,
        "velocity_range": (55, 85),
        "pitch_offset": 0,
        "note_duration_range": (0.125, 0.5),
        "add_harmony": False,
        "energy": 0.4,
    },
    CommitType.STYLE: {
        "instrument": GMInstruments.CELESTA,
        "velocity_range": (45, 70),
        "pitch_offset": 12,
        "note_duration_range": (0.25, 0.75),
        "add_harmony": False,
        "energy": 0.25,
    },
    CommitType.BREAKING: {
        "instrument": GMInstruments.DISTORTION_GUITAR,
        "velocity_range": (100, 127),
        "pitch_offset": -24,
        "note_duration_range": (1.0, 2.0),
        "add_harmony": True,
        "energy": 1.0,
    },
    CommitType.PERFORMANCE: {
        "instrument": GMInstruments.LEAD_SQUARE,
        "velocity_range": (75, 105),
        "pitch_offset": 7,
        "note_duration_range": (0.25, 0.75),
        "add_harmony": False,
        "energy": 0.7,
    },
    CommitType.OTHER: {
        "instrument": GMInstruments.ACOUSTIC_GRAND_PIANO,
        "velocity_range": (60, 90),
        "pitch_offset": 0,
        "note_duration_range": (0.375, 0.75),
        "add_harmony": False,
        "energy": 0.5,
    },
}


# 风格配置
STYLE_CONFIGS: Dict[MusicStyle, Dict[str, Any]] = {
    MusicStyle.ELECTRONIC: {
        "primary_instruments": [
            GMInstruments.LEAD_SAWTOOTH,
            GMInstruments.SYNTH_BASS_1,
            GMInstruments.PAD_WARM,
        ],
        "bpm_range": (118, 140),
        "default_bpm": 128,
        "note_density": 1.5,
        "use_drums": True,
        "swing": 0.0,
        "chord_voicing": "spread",
        "scale_preference": ["PENTATONIC_MINOR", "DORIAN", "A_MINOR"],
    },
    MusicStyle.CLASSICAL: {
        "primary_instruments": [
            GMInstruments.ACOUSTIC_GRAND_PIANO,
            GMInstruments.STRING_ENSEMBLE_1,
            GMInstruments.VIOLIN,
        ],
        "bpm_range": (65, 100),
        "default_bpm": 80,
        "note_density": 0.8,
        "use_drums": False,
        "swing": 0.0,
        "chord_voicing": "close",
        "scale_preference": ["C_MAJOR", "A_MINOR", "G_MAJOR"],
    },
    MusicStyle.ROCK: {
        "primary_instruments": [
            GMInstruments.DISTORTION_GUITAR,
            GMInstruments.ELECTRIC_BASS_PICK,
            GMInstruments.OVERDRIVEN_GUITAR,
        ],
        "bpm_range": (100, 145),
        "default_bpm": 120,
        "note_density": 1.2,
        "use_drums": True,
        "swing": 0.0,
        "chord_voicing": "power",
        "scale_preference": ["E_MINOR", "A_MINOR", "BLUES"],
    },
    MusicStyle.JAZZ: {
        "primary_instruments": [
            GMInstruments.ELECTRIC_PIANO_1,
            GMInstruments.ACOUSTIC_BASS,
            GMInstruments.VIBRAPHONE,
        ],
        "bpm_range": (75, 130),
        "default_bpm": 110,
        "note_density": 1.0,
        "use_drums": True,
        "swing": 0.6,
        "chord_voicing": "extended",
        "scale_preference": ["DORIAN", "MIXOLYDIAN", "BLUES"],
    },
    MusicStyle.AMBIENT: {
        "primary_instruments": [
            GMInstruments.PAD_CHOIR,
            GMInstruments.FX_ATMOSPHERE,
            GMInstruments.ORCHESTRAL_HARP,
        ],
        "bpm_range": (55, 80),
        "default_bpm": 65,
        "note_density": 0.4,
        "use_drums": False,
        "swing": 0.0,
        "chord_voicing": "spread",
        "scale_preference": ["PENTATONIC_MAJOR", "C_MAJOR", "F_MAJOR"],
    },
    MusicStyle.CHIPTUNE: {
        "primary_instruments": [
            GMInstruments.LEAD_SQUARE,
            GMInstruments.SYNTH_BASS_2,
            GMInstruments.LEAD_SAWTOOTH,
        ],
        "bpm_range": (125, 170),
        "default_bpm": 145,
        "note_density": 2.0,
        "use_drums": True,
        "swing": 0.0,
        "chord_voicing": "simple",
        "scale_preference": ["C_MAJOR", "A_MINOR", "PENTATONIC_MAJOR"],
    },
    MusicStyle.LOFI: {
        "primary_instruments": [
            GMInstruments.ELECTRIC_PIANO_2,
            GMInstruments.ACOUSTIC_BASS,
            GMInstruments.PAD_WARM,
        ],
        "bpm_range": (70, 95),
        "default_bpm": 85,
        "note_density": 0.7,
        "use_drums": True,
        "swing": 0.3,
        "chord_voicing": "jazzy",
        "scale_preference": ["DORIAN", "PENTATONIC_MINOR", "A_MINOR"],
    },
    MusicStyle.ORCHESTRAL: {
        "primary_instruments": [
            GMInstruments.STRING_ENSEMBLE_1,
            GMInstruments.FRENCH_HORN,
            GMInstruments.TIMPANI,
        ],
        "bpm_range": (60, 120),
        "default_bpm": 90,
        "note_density": 0.9,
        "use_drums": False,
        "swing": 0.0,
        "chord_voicing": "orchestral",
        "scale_preference": ["D_MAJOR", "C_MAJOR", "G_MAJOR"],
    },
}


def get_instrument_for_file(filename: str) -> int:
    """根据文件名获取乐器"""
    import os
    ext = os.path.splitext(filename)[1].lower()
    return FILE_TYPE_INSTRUMENTS.get(ext, FILE_TYPE_INSTRUMENTS["default"])


def get_style_config(style: MusicStyle) -> Dict[str, Any]:
    """获取风格配置"""
    return STYLE_CONFIGS.get(style, STYLE_CONFIGS[MusicStyle.ELECTRONIC])