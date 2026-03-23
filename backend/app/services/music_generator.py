"""
音乐生成核心逻辑
"""
import random
from typing import List

from app.models.schemas import (
    CommitAnalysis,
    CommitData,
    CommitType,
    MusicData,
    TrackData,
    NoteEvent,
    MusicStyle,
)
from app.core.scales import Scale, get_scale_notes, quantize_to_scale, SCALE_INTERVALS
from app.core.instruments import (
    COMMIT_TYPE_MUSIC,
    STYLE_CONFIGS,
    GMInstruments,
)


class MusicGenerator:
    """根据 commit 分析生成音乐"""
    
    def __init__(
        self,
        style: MusicStyle = MusicStyle.ELECTRONIC,
        bpm: int = 120,
        scale: str = "C_MAJOR",
    ):
        self.style = style
        self.bpm = bpm
        self.scale = Scale[scale] if isinstance(scale, str) else scale
        self.style_config = STYLE_CONFIGS[style]
        
        # 获取音阶音符
        self.scale_notes = get_scale_notes(self.scale, octaves=3)
    
    def generate(self, analysis: CommitAnalysis) -> MusicData:
        """
        主生成入口
        
        映射规则：
        - 每个 commit 对应一个"小节"或几个音符
        - commit 类型决定乐器和音色
        - 修改量决定音符密度和力度
        - commit 时间间隔影响节奏
        """
        tracks: List[TrackData] = []
        
        # 1. 主旋律轨道（基于 commit 类型）
        melody_track = self._generate_melody_track(analysis.commits)
        tracks.append(melody_track)
        
        # 2. 和弦/Pad 轨道
        chord_track = self._generate_chord_track(analysis)
        tracks.append(chord_track)
        
        # 3. 贝斯轨道
        bass_track = self._generate_bass_track(analysis)
        tracks.append(bass_track)
        
        # 4. 可选：鼓轨道
        if self.style_config.get("use_drums", False):
            drum_track = self._generate_drum_track(analysis)
            tracks.append(drum_track)
        
        # 计算总时长
        max_time = max(
            max((n.start_time + n.duration for n in t.notes), default=0)
            for t in tracks
        )
        total_duration = (max_time / self.bpm) * 60  # 转换为秒
        
        return MusicData(
            bpm=self.bpm,
            time_signature=(4, 4),
            total_duration=total_duration,
            tracks=tracks,
        )
    
    def _generate_melody_track(self, commits: List[CommitData]) -> TrackData:
        """生成主旋律"""
        notes = []
        current_time = 0.0
        
        for i, commit in enumerate(commits):
            # 获取 commit 类型对应的音乐参数
            music_params = COMMIT_TYPE_MUSIC.get(
                commit.commit_type,
                COMMIT_TYPE_MUSIC[CommitType.OTHER]
            )
            
            # 基础音高（从音阶中选择）
            scale_index = i % len(self.scale_notes)
            base_pitch = self.scale_notes[scale_index]
            
            # 应用音高偏移
            pitch = base_pitch + music_params["pitch_offset"]
            pitch = max(24, min(108, pitch))  # 限制范围
            
            # 力度（基于修改量）
            changes = commit.additions + commit.deletions
            velocity_min, velocity_max = music_params["velocity_range"]
            velocity = min(velocity_max, velocity_min + int(changes / 10))
            
            # 时值
            duration = music_params["note_duration"]
            
            # 添加音符
            notes.append(NoteEvent(
                pitch=pitch,
                velocity=velocity,
                start_time=current_time,
                duration=duration,
                channel=0,
            ))
            
            # 大型 commit 添加和声
            if changes > 100:
                # 添加三度音
                harmony_pitch = self._get_harmony_note(pitch, 3)
                notes.append(NoteEvent(
                    pitch=harmony_pitch,
                    velocity=int(velocity * 0.7),
                    start_time=current_time,
                    duration=duration,
                    channel=0,
                ))
            
            # 更新时间
            current_time += self._calculate_time_step(commit, i, len(commits))
        
        return TrackData(
            name="Melody",
            instrument=self.style_config["primary_instruments"][0],
            notes=notes,
        )
    
    def _generate_chord_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成和弦/Pad 轨道"""
        notes = []
        
        # 和弦进行：每4个 commit 为一个和弦
        chord_degrees = [1, 5, 6, 4]  # I-V-vi-IV
        
        commits_per_chord = max(4, len(analysis.commits) // 8)
        chord_duration = commits_per_chord * 0.5  # 每个和弦的时长
        
        current_time = 0.0
        chord_index = 0
        
        total_chords = len(analysis.commits) // commits_per_chord + 1
        
        for i in range(total_chords):
            degree = chord_degrees[chord_index % len(chord_degrees)]
            chord_notes = self._get_chord_notes(degree)
            
            for pitch in chord_notes:
                notes.append(NoteEvent(
                    pitch=pitch,
                    velocity=60,
                    start_time=current_time,
                    duration=chord_duration * 0.9,
                    channel=1,
                ))
            
            current_time += chord_duration
            chord_index += 1
        
        return TrackData(
            name="Chords",
            instrument=self.style_config["primary_instruments"][2] 
                       if len(self.style_config["primary_instruments"]) > 2 
                       else GMInstruments.SYNTH_PAD_WARM,
            notes=notes,
        )
    
    def _generate_bass_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成贝斯轨道"""
        notes = []
        
        # 简单的根音贝斯
        bass_notes = get_scale_notes(self.scale, octaves=1)
        bass_notes = [n - 24 for n in bass_notes]  # 低两个八度
        
        current_time = 0.0
        step = 2.0  # 每2拍一个贝斯音
        
        total_steps = int(len(analysis.commits) * 0.5 / step) + 1
        
        for i in range(total_steps):
            pitch = bass_notes[i % len(bass_notes)]
            
            notes.append(NoteEvent(
                pitch=max(28, pitch),
                velocity=80,
                start_time=current_time,
                duration=step * 0.8,
                channel=2,
            ))
            
            current_time += step
        
        return TrackData(
            name="Bass",
            instrument=self.style_config["primary_instruments"][1]
                       if len(self.style_config["primary_instruments"]) > 1
                       else GMInstruments.SYNTH_BASS,
            notes=notes,
        )
    
    def _generate_drum_track(self, analysis: CommitAnalysis) -> TrackData:
        """生成鼓轨道"""
        notes = []
        
        # 鼓音符（GM 标准）
        KICK = 36
        SNARE = 38
        HIHAT_CLOSED = 42
        HIHAT_OPEN = 46
        
        # 根据 commit 密度决定节奏复杂度
        density = analysis.avg_commits_per_day
        
        current_time = 0.0
        total_beats = int(len(analysis.commits) * 0.5)
        
        for beat in range(total_beats):
            # Kick on 1 and 3
            if beat % 4 in [0, 2]:
                notes.append(NoteEvent(
                    pitch=KICK,
                    velocity=100,
                    start_time=current_time,
                    duration=0.5,
                    channel=9,  # 鼓通道
                ))
            
            # Snare on 2 and 4
            if beat % 4 in [1, 3]:
                notes.append(NoteEvent(
                    pitch=SNARE,
                    velocity=90,
                    start_time=current_time,
                    duration=0.25,
                    channel=9,
                ))
            
            # Hi-hat on every beat
            notes.append(NoteEvent(
                pitch=HIHAT_CLOSED,
                velocity=70,
                start_time=current_time,
                duration=0.25,
                channel=9,
            ))
            
            # 高密度时添加额外的 hi-hat
            if density > 3:
                notes.append(NoteEvent(
                    pitch=HIHAT_CLOSED,
                    velocity=50,
                    start_time=current_time + 0.5,
                    duration=0.25,
                    channel=9,
                ))
            
            current_time += 1.0
        
        return TrackData(
            name="Drums",
            instrument=GMInstruments.DRUMS,
            notes=notes,
        )
    
    def _calculate_time_step(
        self, 
        commit: CommitData, 
        index: int, 
        total: int
    ) -> float:
        """计算时间步长"""
        # 基础步长
        base_step = 0.5
        
        # 大 commit 后有更长的间隔
        changes = commit.additions + commit.deletions
        if changes > 500:
            return base_step * 2
        elif changes > 100:
            return base_step * 1.5
        
        return base_step
    
    def _get_harmony_note(self, root: int, interval: int) -> int:
        """获取和声音符"""
        # 简化：直接加半音数
        intervals = {3: 4, 5: 7}  # 大三度，纯五度
        semitones = intervals.get(interval, 4)
        return quantize_to_scale(root + semitones, self.scale)
    
    def _get_chord_notes(self, degree: int) -> List[int]:
        """获取和弦音符"""
        scale_notes = self.scale_notes
        root_idx = degree - 1
        
        if root_idx < len(scale_notes):
            root = scale_notes[root_idx]
            third = scale_notes[(root_idx + 2) % len(scale_notes)]
            fifth = scale_notes[(root_idx + 4) % len(scale_notes)]
            return [root, third, fifth]
        
        return [scale_notes[0], scale_notes[2], scale_notes[4]]