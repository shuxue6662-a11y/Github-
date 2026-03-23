"""
节奏模式定义
"""
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass

from app.models.enums import MusicStyle
from app.core.instruments import DrumNotes


@dataclass
class DrumHit:
    """鼓击事件"""
    note: int
    time: float  # 拍内位置 (0-1)
    velocity: int
    duration: float = 0.1


@dataclass
class DrumPattern:
    """一小节的鼓点模式"""
    name: str
    beats: int  # 拍数
    hits: List[DrumHit]
    
    def get_hits_at_beat(self, beat: int) -> List[DrumHit]:
        """获取指定拍的所有鼓击"""
        return [h for h in self.hits if int(h.time * self.beats) == beat]


# 基础节奏模式
DRUM_PATTERNS: Dict[str, DrumPattern] = {
    # Electronic / House
    "four_on_floor": DrumPattern(
        name="Four on the Floor",
        beats=4,
        hits=[
            # Kick on every beat
            DrumHit(DrumNotes.BASS_DRUM_1, 0.0, 100),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.25, 100),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.5, 100),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.75, 100),
            # Snare on 2 and 4
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.25, 90),
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.75, 90),
            # Hi-hat on every eighth
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.0, 70),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.125, 50),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.25, 70),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.375, 50),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.5, 70),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.625, 50),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.75, 70),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.875, 50),
        ]
    ),
    
    # Basic Rock
    "rock_basic": DrumPattern(
        name="Basic Rock",
        beats=4,
        hits=[
            # Kick on 1 and 3
            DrumHit(DrumNotes.BASS_DRUM_1, 0.0, 100),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.5, 95),
            # Snare on 2 and 4
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.25, 100),
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.75, 100),
            # Hi-hat
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.0, 80),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.125, 60),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.25, 80),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.375, 60),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.5, 80),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.625, 60),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.75, 80),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.875, 60),
        ]
    ),
    
    # Jazz Swing
    "jazz_swing": DrumPattern(
        name="Jazz Swing",
        beats=4,
        hits=[
            # Ride cymbal with swing
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.0, 80),
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.17, 50),  # Swing
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.25, 70),
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.42, 50),
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.5, 80),
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.67, 50),
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.75, 70),
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.92, 50),
            # Hi-hat pedal on 2 and 4
            DrumHit(DrumNotes.PEDAL_HI_HAT, 0.25, 60),
            DrumHit(DrumNotes.PEDAL_HI_HAT, 0.75, 60),
        ]
    ),
    
    # Lo-fi Hip Hop
    "lofi_beat": DrumPattern(
        name="Lo-fi Beat",
        beats=4,
        hits=[
            # Kick
            DrumHit(DrumNotes.BASS_DRUM_1, 0.0, 90),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.375, 70),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.5, 85),
            # Snare
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.25, 85),
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.75, 90),
            # Hi-hat
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.0, 60),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.125, 40),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.25, 55),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.375, 45),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.5, 60),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.625, 40),
            DrumHit(DrumNotes.OPEN_HI_HAT, 0.75, 50),
            DrumHit(DrumNotes.CLOSED_HI_HAT, 0.875, 45),
        ]
    ),
    
    # Chiptune / 8-bit
    "chiptune": DrumPattern(
        name="Chiptune",
        beats=4,
        hits=[
            # Simple kick and snare
            DrumHit(DrumNotes.BASS_DRUM_1, 0.0, 100),
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.25, 95),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.5, 90),
            DrumHit(DrumNotes.BASS_DRUM_1, 0.625, 80),
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.75, 100),
        ]
    ),
    
    # Ambient (minimal)
    "ambient": DrumPattern(
        name="Ambient",
        beats=4,
        hits=[
            # Very sparse
            DrumHit(DrumNotes.RIDE_CYMBAL_1, 0.0, 40),
            DrumHit(DrumNotes.RIDE_BELL, 0.5, 30),
        ]
    ),
    
    # Fill pattern
    "fill_basic": DrumPattern(
        name="Basic Fill",
        beats=4,
        hits=[
            DrumHit(DrumNotes.ACOUSTIC_SNARE, 0.0, 90),
            DrumHit(DrumNotes.HIGH_TOM, 0.125, 85),
            DrumHit(DrumNotes.HIGH_TOM, 0.25, 90),
            DrumHit(DrumNotes.HI_MID_TOM, 0.375, 85),
            DrumHit(DrumNotes.HI_MID_TOM, 0.5, 90),
            DrumHit(DrumNotes.LOW_TOM, 0.625, 85),
            DrumHit(DrumNotes.LOW_TOM, 0.75, 100),
            DrumHit(DrumNotes.CRASH_CYMBAL_1, 0.875, 110),
        ]
    ),
}


# 风格对应的鼓点模式
STYLE_DRUM_PATTERNS: Dict[MusicStyle, List[str]] = {
    MusicStyle.ELECTRONIC: ["four_on_floor"],
    MusicStyle.CLASSICAL: [],  # No drums
    MusicStyle.ROCK: ["rock_basic"],
    MusicStyle.JAZZ: ["jazz_swing"],
    MusicStyle.AMBIENT: ["ambient"],
    MusicStyle.CHIPTUNE: ["chiptune"],
    MusicStyle.LOFI: ["lofi_beat"],
    MusicStyle.ORCHESTRAL: [],  # No drums (use timpani separately)
}


def get_drum_pattern(style: MusicStyle) -> DrumPattern | None:
    """获取风格对应的鼓点模式"""
    pattern_names = STYLE_DRUM_PATTERNS.get(style, [])
    if not pattern_names:
        return None
    return DRUM_PATTERNS.get(pattern_names[0])


# 节奏型（旋律用）
RHYTHM_PATTERNS: Dict[str, List[Tuple[float, float]]] = {
    # (start_time, duration) 相对于一小节
    "quarter_notes": [
        (0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)
    ],
    "eighth_notes": [
        (0.0, 0.5), (0.5, 0.5), (1.0, 0.5), (1.5, 0.5),
        (2.0, 0.5), (2.5, 0.5), (3.0, 0.5), (3.5, 0.5)
    ],
    "syncopated": [
        (0.0, 1.0), (1.5, 0.5), (2.0, 1.5), (3.5, 0.5)
    ],
    "dotted": [
        (0.0, 1.5), (1.5, 0.5), (2.0, 1.5), (3.5, 0.5)
    ],
    "waltz": [
        (0.0, 1.0), (1.0, 1.0), (2.0, 1.0)
    ],
    "offbeat": [
        (0.5, 0.5), (1.5, 0.5), (2.5, 0.5), (3.5, 0.5)
    ],
}