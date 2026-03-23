"""
音乐生成核心逻辑
"""
import random
from typing import List, Optional
from datetime import datetime

from app.models.schemas import (
    CommitAnalysis,
    CommitData,
    MusicData,
    TrackData,
    NoteEvent,
)
from app.models.enums import MusicStyle, CommitType, ScaleType
from app.core.scales import (
    get_scale_notes, 
    quantize_to_scale,
    get_chord_notes,
    get_scale_chord,
    CHORD_PROGRESSIONS,
)
from app.core.instruments import (
    COMMIT_TYPE_MUSIC,
    STYLE_CONFIGS,
    GMInstruments,
    DrumNotes,
    get_style_config,
)
from app.core.rhythm_patterns import get_drum_pattern, DrumPattern
from app.core.music_theory import (
    MelodyGenerator,
    ChordProgressionGenerator,
    VoiceLeading,
    humanize_timing,
    humanize_velocity,
)
from app.utils.helpers import clamp, map_range


class MusicGenerator:
    """根据 commit 分析生成音乐"""
    
    def __init__(
        self,
        style: MusicStyle = MusicStyle.ELECTRONIC,
        bpm: int = 120,
        scale: ScaleType = ScaleType.C_MAJOR,
        include_drums: bool = True,
        include_bass: bool = True,
        include_chords: bool = True,
        melody_complexity: float = 0.5,
    ):
        self.style = style
        self.scale = scale
        self.include_drums = include_drums
        self.include_bass = include_bass
        self.include_chords = include_chords
        self.melody_complexity = clamp(melody_complexity, 0, 1)
        
        # 获取风格配置
        self.style_config = get_style_config(style)
        
        # 设置 BPM（使用风格默认或用户指定）
        bpm_range = self.style_config.get("bpm_range", (100, 140))
        self.bpm = clamp(bpm, bpm_range[0], bpm_range[1])
        
        # 初始化音阶
        self.scale_notes = get_scale_notes(scale, octaves=3)
        
        # 乐理工具
        self.melody_gen = MelodyGenerator(scale, complexity=melody_complexity)
        self.chord_gen = ChordProgressionGenerator(scale, progression_type="pop")
    
    def generate(self, analysis: CommitAnalysis) -> MusicData:
        """
        主生成入口
        
        映射规则：
        - 每个 commit 对应若干音符
        - commit 类型决定乐器和音色
        - 修改量决定音符密度和力度
        - commit 时间间隔影响节奏
        - 活跃度影响整体能量
        """
        tracks: List[TrackData] = []
        
        # 1. 主旋律轨道
        melody_track = self._generate_melody_track(analysis)
        tracks.append(melody_track)
        
        # 2. 和弦/Pad 轨道
        if self.include_chords:
            chord_track = self._generate_chord_track(analysis)
            tracks.append(chord_track)
        
        # 3. 贝斯轨道
        if self.include_bass:
            bass_track = self._generate_bass_track(analysis)
            tracks.append(bass_track)
        
        # 4. 鼓轨道
        if self.include_drums and self.style_config.get("use_drums", True):
            drum_track = self._generate_drum_track(analysis)
            if drum_track.notes:
                tracks.append(drum_track)
        
        # 5. 计算总时长
        max_beats = 0.0
        for track in tracks:
            for note in track.notes:
                end_time = note.start_time + note.duration
                if end_time > max_beats:
                    max_beats = end_time
        
        # 添加结尾留白
        max_beats += 4.0
        
        # 转换为秒
        total_duration = (max_beats / self.bpm) * 60
        
        return MusicData(
            bpm=self.bpm,
            time_signature=(4, 4),
            total_beats=max_beats,
            total_duration=total_duration,
            scale=self.scale.value,
            style=self.style.value,
            tracks=tracks,
        )
    
    def _generate_melody_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成主旋律"""
        notes: List[NoteEvent] = []
        current_time = 0.0
        
        commits = analysis.commits
        self.melody_gen.reset()
        
        # 根据活跃度调整密度
        density_multiplier = {
            "low": 0.7,
            "moderate": 1.0,
            "high": 1.3,
            "intense": 1.6,
        }.get(analysis.activity_level, 1.0)
        
        for i, commit in enumerate(commits):
            # 获取 commit 类型的音乐参数
            music_params = COMMIT_TYPE_MUSIC.get(
                commit.commit_type,
                COMMIT_TYPE_MUSIC[CommitType.OTHER]
            )
            
            # 能量级别
            energy = commit.impact_score * music_params["energy"]
            
            # 生成音符数量（基于修改量和能量）
            base_notes = 1 + int(energy * 3 * density_multiplier)
            num_notes = min(6, base_notes)
            
            # 时值范围
            dur_min, dur_max = music_params["note_duration_range"]
            
            for j in range(num_notes):
                # 生成音高
                pitch = self.melody_gen.generate_note(energy=energy)
                pitch = pitch + music_params["pitch_offset"]
                pitch = clamp(pitch, 36, 96)
                
                # 量化到音阶
                pitch = quantize_to_scale(int(pitch), self.scale)
                
                # 力度
                vel_min, vel_max = music_params["velocity_range"]
                base_velocity = int(map_range(energy, 0, 1, vel_min, vel_max))
                velocity = humanize_velocity(base_velocity, amount=8)
                
                # 时值
                duration = random.uniform(dur_min, dur_max)
                
                # 添加音符
                notes.append(NoteEvent(
                    pitch=pitch,
                    velocity=velocity,
                    start_time=humanize_timing(current_time, 0.02),
                    duration=duration,
                    channel=0,
                ))
                
                # 添加和声（大型 commit）
                if music_params.get("add_harmony") and commit.total_changes > 100:
                    harmony_pitch = quantize_to_scale(pitch + 4, self.scale)
                    notes.append(NoteEvent(
                        pitch=harmony_pitch,
                        velocity=int(velocity * 0.7),
                        start_time=current_time,
                        duration=duration * 0.9,
                        channel=0,
                    ))
                
                current_time += duration * 0.6
            
            # commit 之间的间隔
            current_time += self._calculate_gap(commit, i, len(commits))
        
        return TrackData(
            name="Melody",
            instrument=self.style_config["primary_instruments"][0],
            notes=notes,
            volume=0.85,
        )
    
    def _generate_chord_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成和弦轨道"""
        notes: List[NoteEvent] = []
        
        # 每 N 个 commit 一个和弦
        commits_per_chord = max(2, len(analysis.commits) // 16)
        chord_duration = commits_per_chord * 0.75
        
        current_time = 0.0
        self.chord_gen.reset()
        prev_chord_notes: List[int] = []
        
        total_chords = min(32, len(analysis.commits) // commits_per_chord + 1)
        
        for i in range(total_chords):
            # 获取下一个和弦
            root, chord_type, chord_notes = self.chord_gen.get_next_chord(
                use_seventh=(random.random() < 0.3)
            )
            
            # 声部进行优化
            if prev_chord_notes:
                chord_notes = VoiceLeading.smooth_chord_transition(
                    prev_chord_notes, chord_notes
                )
            
            # 力度变化（乐句结构）
            phrase_position = (i % 8) / 8
            base_velocity = 55 + int(phrase_position * 20)
            
            for pitch in chord_notes:
                velocity = humanize_velocity(base_velocity, amount=5)
                
                notes.append(NoteEvent(
                    pitch=pitch,
                    velocity=velocity,
                    start_time=current_time,
                    duration=chord_duration * 0.95,
                    channel=1,
                ))
            
            prev_chord_notes = chord_notes
            current_time += chord_duration
        
        # 选择 Pad 乐器
        pad_instruments = self.style_config["primary_instruments"]
        pad_instrument = (
            pad_instruments[2] if len(pad_instruments) > 2 
            else GMInstruments.PAD_WARM
        )
        
        return TrackData(
            name="Chords",
            instrument=pad_instrument,
            notes=notes,
            volume=0.6,
            pan=-0.2,
        )
    
    def _generate_bass_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成贝斯轨道"""
        notes: List[NoteEvent] = []
        
        # 获取低音区音阶
        bass_scale = get_scale_notes(self.scale, octaves=1, base_octave=2)
        
        current_time = 0.0
        step = 1.0  # 每拍一个贝斯音
        
        # 根据风格调整节奏
        if self.style == MusicStyle.ELECTRONIC:
            pattern = [1.0, 0, 0.5, 0]  # 典型 four-on-floor
        elif self.style == MusicStyle.JAZZ:
            pattern = [1.0, 0.7, 0.8, 0.7]  # Walking bass 风格
        elif self.style == MusicStyle.ROCK:
            pattern = [1.0, 0, 1.0, 0.5]
        else:
            pattern = [1.0, 0, 0.8, 0]
        
        total_steps = int(len(analysis.commits) * 0.6)
        note_index = 0
        
        for i in range(total_steps):
            pattern_value = pattern[i % len(pattern)]
            
            if pattern_value > 0:
                pitch = bass_scale[note_index % len(bass_scale)]
                velocity = int(70 * pattern_value) + random.randint(-5, 10)
                
                notes.append(NoteEvent(
                    pitch=pitch,
                    velocity=clamp(velocity, 40, 100),
                    start_time=humanize_timing(current_time, 0.01),
                    duration=step * 0.8,
                    channel=2,
                ))
                
                # 偶尔换音
                if random.random() < 0.3:
                    note_index += random.choice([-1, 1, 2])
            
            current_time += step
        
        # 选择贝斯乐器
        bass_instruments = self.style_config["primary_instruments"]
        bass_instrument = (
            bass_instruments[1] if len(bass_instruments) > 1 
            else GMInstruments.SYNTH_BASS_1
        )
        
        return TrackData(
            name="Bass",
            instrument=bass_instrument,
            notes=notes,
            volume=0.75,
        )
    
    def _generate_drum_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成鼓轨道"""
        notes: List[NoteEvent] = []
        
        # 获取风格对应的鼓点模式
        pattern = get_drum_pattern(self.style)
        
        if not pattern:
            return TrackData(name="Drums", instrument=GMInstruments.DRUMS, notes=[])
        
        # 计算总小节数
        total_bars = min(64, len(analysis.commits) // 3 + 4)
        beats_per_bar = pattern.beats
        
        current_time = 0.0
        
        for bar in range(total_bars):
            # 是否加 fill（每 8 小节或最后一小节）
            use_fill = (bar > 0 and bar % 8 == 7)
            
            for hit in pattern.hits:
                hit_time = current_time + hit.time * beats_per_bar
                velocity = humanize_velocity(hit.velocity, amount=10)
                
                notes.append(NoteEvent(
                    pitch=hit.note,
                    velocity=velocity,
                    start_time=humanize_timing(hit_time, 0.005),
                    duration=hit.duration,
                    channel=9,  # 鼓通道
                ))
            
            current_time += beats_per_bar
        
        return TrackData(
            name="Drums",
            instrument=GMInstruments.DRUMS,
            notes=notes,
            volume=0.8,
        )
    
    def _calculate_gap(
        self, 
        commit: CommitData, 
        index: int, 
        total: int,
    ) -> float:
        """计算 commit 之间的时间间隔"""
        base_gap = 0.5
        
        # 大 commit 后稍长间隔
        if commit.total_changes > 500:
            return base_gap * 1.5
        elif commit.total_changes > 200:
            return base_gap * 1.25
        
        # Merge commit 后有较长间隔
        if commit.commit_type == CommitType.MERGE:
            return base_gap * 2.0
        
        return base_gap