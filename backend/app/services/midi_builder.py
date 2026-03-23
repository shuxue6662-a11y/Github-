"""
MIDI 文件构建
"""
from io import BytesIO
from midiutil import MIDIFile

from app.models.schemas import MusicData, TrackData


class MidiBuilder:
    """构建 MIDI 文件"""
    
    def build(self, music_data: MusicData) -> bytes:
        """
        将 MusicData 转换为 MIDI 文件字节
        """
        # 创建 MIDI 文件（多轨道）
        num_tracks = len(music_data.tracks)
        midi = MIDIFile(
            numTracks=num_tracks,
            removeDuplicates=True,
            deinterleave=True,
        )
        
        # 设置 tempo
        for track_idx in range(num_tracks):
            midi.addTempo(track_idx, 0, music_data.bpm)
        
        # 添加各轨道
        for track_idx, track in enumerate(music_data.tracks):
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
        track: TrackData
    ):
        """添加单个轨道"""
        # 轨道名称
        midi.addTrackName(track_idx, 0, track.name)
        
        # 设置乐器（除了鼓轨道）
        channel = track_idx % 16
        
        # 鼓轨道固定使用 channel 9
        if track.name == "Drums" or track.instrument >= 128:
            channel = 9
        else:
            midi.addProgramChange(track_idx, channel, 0, track.instrument)
        
        # 添加音符
        for note in track.notes:
            # MIDI channel 9 (鼓) 不需要调整
            note_channel = 9 if channel == 9 else channel
            
            midi.addNote(
                track=track_idx,
                channel=note_channel,
                pitch=note.pitch,
                time=note.start_time,
                duration=note.duration,
                volume=note.velocity,
            )