"""
音阶和乐理定义
"""
from typing import List, Dict, Tuple
from app.models.enums import ScaleType


# MIDI 音高基准
MIDI_C4 = 60
MIDI_A4 = 69

# 音名到 MIDI 的基础映射（C4 = 60）
NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'Fb': 4, 'E#': 5,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11, 'Cb': 11, 'B#': 0,
}

# MIDI 到音名
MIDI_TO_NOTE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# 音阶音程定义（相对于根音的半音数）
SCALE_INTERVALS: Dict[ScaleType, List[int]] = {
    # 自然大调
    ScaleType.C_MAJOR: [0, 2, 4, 5, 7, 9, 11],
    ScaleType.G_MAJOR: [0, 2, 4, 5, 7, 9, 11],
    ScaleType.D_MAJOR: [0, 2, 4, 5, 7, 9, 11],
    ScaleType.F_MAJOR: [0, 2, 4, 5, 7, 9, 11],
    
    # 自然小调
    ScaleType.A_MINOR: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.E_MINOR: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.B_MINOR: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.D_MINOR: [0, 2, 3, 5, 7, 8, 10],
    
    # 五声音阶
    ScaleType.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],
    ScaleType.PENTATONIC_MINOR: [0, 3, 5, 7, 10],
    
    # 蓝调音阶
    ScaleType.BLUES: [0, 3, 5, 6, 7, 10],
    
    # 调式
    ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
    ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
}

# 音阶根音（MIDI 编号）
SCALE_ROOTS: Dict[ScaleType, int] = {
    ScaleType.C_MAJOR: 60,
    ScaleType.A_MINOR: 57,
    ScaleType.G_MAJOR: 55,
    ScaleType.E_MINOR: 52,
    ScaleType.D_MAJOR: 50,
    ScaleType.B_MINOR: 59,
    ScaleType.F_MAJOR: 53,
    ScaleType.D_MINOR: 50,
    ScaleType.PENTATONIC_MAJOR: 60,
    ScaleType.PENTATONIC_MINOR: 57,
    ScaleType.BLUES: 60,
    ScaleType.DORIAN: 50,
    ScaleType.MIXOLYDIAN: 55,
}

# 和弦度数到音程
CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}

# 大调音阶的和弦类型（每个度数）
MAJOR_SCALE_CHORDS = ["major", "minor", "minor", "major", "major", "minor", "dim"]
MINOR_SCALE_CHORDS = ["minor", "dim", "major", "minor", "minor", "major", "major"]


def get_scale_notes(scale: ScaleType, octaves: int = 2, base_octave: int = 4) -> List[int]:
    """
    获取音阶的 MIDI 音高列表
    
    Args:
        scale: 音阶类型
        octaves: 跨越的八度数
        base_octave: 起始八度
    
    Returns:
        MIDI 音高列表
    """
    root = SCALE_ROOTS.get(scale, 60)
    intervals = SCALE_INTERVALS.get(scale, [0, 2, 4, 5, 7, 9, 11])
    
    # 调整到指定八度
    octave_diff = base_octave - 4
    root = root + (octave_diff * 12)
    
    notes = []
    for octave in range(octaves):
        for interval in intervals:
            note = root + interval + (octave * 12)
            if 0 <= note <= 127:
                notes.append(note)
    
    return notes


def quantize_to_scale(pitch: int, scale: ScaleType) -> int:
    """
    将任意音高量化到指定音阶
    """
    scale_notes = get_scale_notes(scale, octaves=10, base_octave=0)
    
    if not scale_notes:
        return pitch
    
    # 找最近的音阶音
    return min(scale_notes, key=lambda x: abs(x - pitch))


def get_chord_notes(root: int, chord_type: str = "major") -> List[int]:
    """
    获取和弦的音符
    
    Args:
        root: 根音 MIDI 编号
        chord_type: 和弦类型
    
    Returns:
        和弦音符列表
    """
    intervals = CHORD_INTERVALS.get(chord_type, [0, 4, 7])
    return [root + interval for interval in intervals]


def get_scale_chord(scale: ScaleType, degree: int, seventh: bool = False) -> Tuple[int, str]:
    """
    获取音阶的特定度数和弦
    
    Args:
        scale: 音阶
        degree: 度数 (1-7)
        seventh: 是否包含七音
    
    Returns:
        (根音, 和弦类型)
    """
    scale_notes = get_scale_notes(scale, octaves=1)
    
    if not scale_notes or degree < 1 or degree > len(scale_notes):
        return (60, "major")
    
    root = scale_notes[degree - 1]
    
    # 判断大调还是小调
    intervals = SCALE_INTERVALS.get(scale, [])
    is_minor = 3 in intervals  # 小三度
    
    chord_types = MINOR_SCALE_CHORDS if is_minor else MAJOR_SCALE_CHORDS
    chord_type = chord_types[(degree - 1) % 7]
    
    if seventh:
        if chord_type == "major":
            chord_type = "maj7" if degree in [1, 4] else "dom7"
        elif chord_type == "minor":
            chord_type = "min7"
    
    return (root, chord_type)


def midi_to_note_name(midi: int) -> str:
    """MIDI 编号转音名"""
    octave = (midi // 12) - 1
    note = MIDI_TO_NOTE[midi % 12]
    return f"{note}{octave}"


def note_name_to_midi(note: str, octave: int = 4) -> int:
    """音名转 MIDI 编号"""
    note_value = NOTE_TO_MIDI.get(note.upper(), 0)
    return (octave + 1) * 12 + note_value


# 常用和弦进行
CHORD_PROGRESSIONS = {
    "pop": [1, 5, 6, 4],           # I-V-vi-IV
    "rock": [1, 4, 5, 5],          # I-IV-V-V
    "jazz": [2, 5, 1, 1],          # ii-V-I-I
    "emotional": [6, 4, 1, 5],     # vi-IV-I-V
    "epic": [1, 3, 4, 4],          # I-iii-IV-IV
    "blues": [1, 1, 4, 1, 5, 4, 1, 5],  # 12-bar blues 简化
    "melancholy": [1, 6, 4, 5],    # I-vi-IV-V
    "uplifting": [4, 5, 6, 1],     # IV-V-vi-I (逆向流行)
    "dramatic": [6, 7, 1, 1],      # vi-VII-I-I
    "chill": [1, 6, 2, 5],         # I-vi-ii-V
}