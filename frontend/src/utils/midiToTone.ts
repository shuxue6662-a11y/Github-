/**
 * MIDI 数据处理工具
 */
import type { MusicData, TrackData, NoteEvent } from '../types';

/**
 * MIDI 音高转音符名
 */
export function midiToNoteName(midi: number): string {
  const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const octave = Math.floor(midi / 12) - 1;
  const note = notes[midi % 12];
  return `${note}${octave}`;
}

/**
 * 音符名转 MIDI 音高
 */
export function noteNameToMidi(noteName: string): number {
  const noteMap: Record<string, number> = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11,
  };

  const match = noteName.match(/^([A-G]#?)(-?\d+)$/);
  if (!match) return 60; // 默认 C4

  const [, note, octaveStr] = match;
  const octave = parseInt(octaveStr, 10);
  const noteValue = noteMap[note] ?? 0;

  return (octave + 1) * 12 + noteValue;
}

/**
 * MIDI 力度转音量 (0-1)
 */
export function velocityToVolume(velocity: number): number {
  return Math.max(0, Math.min(1, velocity / 127));
}

/**
 * 拍数转秒数
 */
export function beatsToSeconds(beats: number, bpm: number): number {
  return (beats / bpm) * 60;
}

/**
 * 秒数转拍数
 */
export function secondsToBeats(seconds: number, bpm: number): number {
  return (seconds * bpm) / 60;
}

/**
 * 格式化时间 (mm:ss)
 */
export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * 解析 Base64 MIDI 数据
 */
export function parseMidiBase64(base64: string): Uint8Array {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

/**
 * 获取音乐统计信息
 */
export function getMusicStats(musicData: MusicData): {
  totalNotes: number;
  totalTracks: number;
  duration: string;
  bpm: number;
  highestNote: string;
  lowestNote: string;
  avgVelocity: number;
} {
  let totalNotes = 0;
  let highestPitch = 0;
  let lowestPitch = 127;
  let totalVelocity = 0;

  musicData.tracks.forEach((track) => {
    track.notes.forEach((note) => {
      totalNotes++;
      totalVelocity += note.velocity;
      if (note.pitch > highestPitch) highestPitch = note.pitch;
      if (note.pitch < lowestPitch) lowestPitch = note.pitch;
    });
  });

  return {
    totalNotes,
    totalTracks: musicData.tracks.length,
    duration: formatTime(musicData.total_duration),
    bpm: musicData.bpm,
    highestNote: midiToNoteName(highestPitch),
    lowestNote: midiToNoteName(lowestPitch),
    avgVelocity: totalNotes > 0 ? Math.round(totalVelocity / totalNotes) : 0,
  };
}

/**
 * 获取轨道颜色
 */
export function getTrackColor(index: number): string {
  const colors = [
    '#a855f7', // purple
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#84cc16', // lime
  ];
  return colors[index % colors.length];
}

/**
 * 生成波形数据（简化版，用于可视化）
 */
export function generateWaveformData(
  musicData: MusicData,
  bars: number = 50
): number[] {
  const waveform = new Array(bars).fill(0);
  const barDuration = musicData.total_duration / bars;

  musicData.tracks.forEach((track) => {
    track.notes.forEach((note) => {
      const startTime = beatsToSeconds(note.start_time, musicData.bpm);
      const barIndex = Math.min(bars - 1, Math.floor(startTime / barDuration));
      waveform[barIndex] += note.velocity / 127;
    });
  });

  // 归一化
  const maxValue = Math.max(...waveform, 1);
  return waveform.map((v) => v / maxValue);
}