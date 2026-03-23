"""
音阶和乐理定义
"""
from enum import Enum
from typing import List


class Scale(Enum):
    """音阶类型"""
    C_MAJOR = "C_MAJOR"
    A_MINOR = "A_MINOR"
    G_MAJOR = "G_MAJOR"
    E_MINOR = "E_MINOR"
    D_MAJOR = "D_MAJOR"
    B_MINOR = "B_MINOR"
    PENTATONIC_MAJOR = "PENTATONIC_MAJOR"
    PENTATONIC_MINOR = "PENTATONIC_MINOR"
    BLUES = "BLUES"


# MIDI 音高基准（C4 = 60）
MIDI_C4 = 60

# 音阶音程定义（相对于根音的半音数）
SCALE_INTERVALS = {
    Scale.C_MAJOR: [0, 2, 4, 5, 7, 9, 11],          # C D E F G A B
    Scale.A_MINOR: [0, 2, 3, 5, 7, 8, 10],          # A B C D E F G
    Scale.G_MAJOR: [0, 2, 4, 5, 7, 9, 11],          # 移调到 G
    Scale.E_MINOR: [0, 2, 3, 5, 7, 8, 10],          # 移调到 E
    Scale.D_MAJOR: [0, 2, 4, 5, 7, 9, 11],          # 移调到 D
    Scale.B_MINOR: [0, 2, 3, 5, 7, 8, 10],          # 移调到 B
    Scale.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],        # 五声大调
    Scale.PENTATONIC_MINOR: [0, 3, 5, 7, 10],       # 五声小调
    Scale.BLUES: [0, 3, 5, 6, 7, 10],               # 蓝调音阶
}

# 音阶根音（MIDI 编号）
SCALE_ROOTS = {
    Scale.C_MAJOR: 60,       # C4
    Scale.A_MINOR: 57,       # A3
    Scale.G_MAJOR: 55,       # G3
    Scale.E_MINOR: 52,       # E3
    Scale.D_MAJOR: 50,       # D3
    Scale.B_MINOR: 59,       # B3
    Scale.PENTATONIC_MAJOR: 60,
    Scale.PENTATONIC_MINOR: 57,
    Scale.BLUES: 60,
}


def get_scale_notes(scale: Scale, octaves: int = 2) -> List[int]:
    """
    获取音阶的 MIDI 音高列表
    
    Args:
        scale: 音阶类型
        octaves: 跨越的八度数
    
    Returns:
        MIDI 音高列表
    """
    root = SCALE_ROOTS[scale]
    intervals = SCALE_INTERVALS[scale]
    
    notes = []
    for octave in range(octaves):
        for interval in intervals:
            note = root + interval + (octave * 12)
            if 0 <= note <= 127:
                notes.append(note)
    
    return notes


def quantize_to_scale(pitch: int, scale: Scale) -> int:
    """
    将任意音高量化到指定音阶
    """
    scale_notes = get_scale_notes(scale, octaves=8)
    
    # 找最近的音阶音
    return min(scale_notes, key=lambda x: abs(x - pitch))


# 和弦进行（度数表示）
CHORD_PROGRESSIONS = {
    "pop": [1, 5, 6, 4],           # I-V-vi-IV (经典流行)
    "rock": [1, 4, 5, 5],          # I-IV-V-V
    "jazz": [2, 5, 1, 1],          # ii-V-I-I
    "emotional": [6, 4, 1, 5],     # vi-IV-I-V
    "epic": [1, 3, 4, 4],          # I-iii-IV-IV
}