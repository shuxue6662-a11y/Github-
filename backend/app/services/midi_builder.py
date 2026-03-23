"""
MIDI 文件构建
"""
from io import BytesIO
from typing import List
from midiutil import MIDIFile

from app.models.schemas import MusicData, TrackData, NoteEvent
from app.core.instruments import GMInstruments


class MidiBuilder:
    """构建 MIDI 文件"""
    
    def __init__(self):
        self.ticks_per_beat = 480
    
    def build(self, music_data: MusicData) -> bytes:
        """
        将 MusicData 转换为 MIDI 文件字节
        
        Args:
            music_data: 音乐数据
        
        Returns:
            MIDI 文件的字节数据
        """
        # 过滤空轨道
        tracks_with_notes = [t for t in music_data.tracks if t.notes]
        num_tracks = len(tracks_with_notes)
        
        if num_tracks == 0:
            # 返回一个空的但有效的 MIDI 文件
            num_tracks = 1
        
        # 创建 MIDI 文件
        midi = MIDIFile(
            numTracks=num_tracks,
            removeDuplicates=True,
            deinterleave=True,
            ticks_per_quarternote=self.ticks_per_beat,
        )
        
        # 设置全局 tempo
        for track_idx in range(num_tracks):
            midi.addTempo(track_idx, 0, music_data.bpm)
            midi.addTimeSignature(
                track_idx, 0,
                music_data.time_signature[0],
                int(music_data.time_signature[1]).bit_length() - 1,
                24, 8
            )
        
        # 添加各轨道
        for track_idx, track in enumerate(tracks_with_notes):
            self._add_track(midi, track_idx, track)
        
        # 写入字节流
        buffer = BytesIO()
        midi.writeFile(buffer)
        buffer.seek(0)
        
        return buffer.read()
    
    def _add_track(
        self, 
        midi: MIDIFile, 
        track_idx: int, 
        track: TrackData,
    ):
        """添加单个轨道"""
        # 轨道名称
        midi.addTrackName(track_idx, 0, track.name)
        
        # 确定 MIDI 通道
        # Channel 9 (索引) 用于打击乐
        if track.name == "Drums" or track.instrument >= 128:
            channel = 9
        else:
            # 使用轨道索引作为通道，跳过 9
            channel = track_idx if track_idx < 9 else track_idx + 1
            channel = channel % 16
            if channel == 9:
                channel = 10 % 16
        
        # 设置乐器（打击乐不需要）
        if channel != 9 and track.instrument < 128:
            midi.addProgramChange(track_idx, channel, 0, track.instrument)
        
        # 设置音量
        volume = int(track.volume * 127)
        midi.addControllerEvent(track_idx, channel, 0, 7, volume)  # CC7 = Volume
        
        # 设置声像
        pan = int((track.pan + 1) * 63.5)  # -1~1 → 0~127
        midi.addControllerEvent(track_idx, channel, 0, 10, pan)  # CC10 = Pan
        
        # 添加音符
        for note in track.notes:
            # 确保音符参数在有效范围内
            pitch = max(0, min(127, note.pitch))
            velocity = max(1, min(127, note.velocity))
            start_time = max(0, note.start_time)
            duration = max(0.01, note.duration)
            
            midi.addNote(
                track=track_idx,
                channel=channel,
                pitch=pitch,
                time=start_time,
                duration=duration,
                volume=velocity,
            )
    
    def build_from_notes(
        self,
        notes: List[NoteEvent],
        bpm: int = 120,
        instrument: int = 0,
        track_name: str = "Track",
    ) -> bytes:
        """
        从音符列表直接构建 MIDI
        
        简化版接口，用于快速测试
        """
        track = TrackData(
            name=track_name,
            instrument=instrument,
            notes=notes,
        )
        
        music_data = MusicData(
            bpm=bpm,
            time_signature=(4, 4),
            total_beats=max((n.start_time + n.duration for n in notes), default=4),
            total_duration=0,  # 会被忽略
            scale="C_MAJOR",
            style="electronic",
            tracks=[track],
        )
        
        return self.build(music_data)