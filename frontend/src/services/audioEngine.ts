/**
 * Tone.js 音频引擎封装
 */
import * as Tone from 'tone';

export interface NoteEvent {
  pitch: number;
  velocity: number;
  start_time: number;
  duration: number;
  channel: number;
}

export interface TrackData {
  name: string;
  instrument: number;
  notes: NoteEvent[];
}

export interface MusicData {
  bpm: number;
  time_signature: [number, number];
  total_duration: number;
  tracks: TrackData[];
}

// GM 乐器映射到 Tone.js 合成器
const instrumentMap: Record<number, () => Tone.PolySynth | Tone.Sampler> = {
  0: () => new Tone.PolySynth(Tone.Synth).toDestination(),    // Piano
  38: () => new Tone.PolySynth(Tone.FMSynth).toDestination(), // Synth Bass
  80: () => new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: 'square' }
  }).toDestination(),  // Square Lead
  81: () => new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: 'sawtooth' }
  }).toDestination(),  // Saw Lead
  89: () => new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: 'sine' },
    envelope: { attack: 0.5, decay: 0.2, sustain: 0.8, release: 1 }
  }).toDestination(),  // Pad
};

// MIDI 音高转频率
function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

// MIDI 音高转音符名
function midiToNote(midi: number): string {
  const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const octave = Math.floor(midi / 12) - 1;
  const note = notes[midi % 12];
  return `${note}${octave}`;
}

export class AudioEngine {
  private synths: Map<number, Tone.PolySynth> = new Map();
  private isPlaying: boolean = false;
  private scheduledEvents: number[] = [];
  
  async init(): Promise<void> {
    await Tone.start();
    console.log('Audio context started');
  }
  
  loadMusic(musicData: MusicData): void {
    // 清理旧的合成器
    this.dispose();
    
    // 设置 BPM
    Tone.Transport.bpm.value = musicData.bpm;
    
    // 为每个轨道创建合成器
    musicData.tracks.forEach((track, index) => {
      const createSynth = instrumentMap[track.instrument] || instrumentMap[0];
      const synth = createSynth();
      this.synths.set(index, synth as Tone.PolySynth);
    });
  }
  
  scheduleMusic(musicData: MusicData): void {
    const now = Tone.now();
    
    musicData.tracks.forEach((track, trackIndex) => {
      const synth = this.synths.get(trackIndex);
      if (!synth) return;
      
      // 跳过鼓轨道（需要特殊处理）
      if (track.name === 'Drums') {
        // TODO: 使用 Tone.Players 处理鼓采样
        return;
      }
      
      track.notes.forEach(note => {
        const noteName = midiToNote(note.pitch);
        const startTime = Tone.Time(note.start_time, 'n').toSeconds();
        const duration = Tone.Time(note.duration, 'n').toSeconds();
        const velocity = note.velocity / 127;
        
        // 使用 Transport 调度
        const eventId = Tone.Transport.schedule((time) => {
          synth.triggerAttackRelease(
            noteName,
            duration,
            time,
            velocity
          );
        }, startTime);
        
        this.scheduledEvents.push(eventId);
      });
    });
  }
  
  play(): void {
    if (!this.isPlaying) {
      Tone.Transport.start();
      this.isPlaying = true;
    }
  }
  
  pause(): void {
    if (this.isPlaying) {
      Tone.Transport.pause();
      this.isPlaying = false;
    }
  }
  
  stop(): void {
    Tone.Transport.stop();
    Tone.Transport.position = 0;
    this.isPlaying = false;
  }
  
  seek(time: number): void {
    Tone.Transport.position = time;
  }
  
  get currentTime(): number {
    return Tone.Transport.seconds;
  }
  
  get playing(): boolean {
    return this.isPlaying;
  }
  
  dispose(): void {
    this.stop();
    this.scheduledEvents.forEach(id => Tone.Transport.clear(id));
    this.scheduledEvents = [];
    this.synths.forEach(synth => synth.dispose());
    this.synths.clear();
  }
}

// 单例导出
export const audioEngine = new AudioEngine();