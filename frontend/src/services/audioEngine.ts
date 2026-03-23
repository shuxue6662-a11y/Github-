/**
 * Tone.js 音频引擎
 */
import * as Tone from 'tone';
import type { MusicData, TrackData, NoteEvent } from '../types';

// MIDI 音高转音符名
function midiToNoteName(midi: number): string {
  const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const octave = Math.floor(midi / 12) - 1;
  const note = notes[midi % 12];
  return `${note}${octave}`;
}

// GM 乐器到 Tone.js 合成器类型映射
type SynthType = 'synth' | 'fm' | 'am' | 'membrane' | 'metal' | 'pluck' | 'mono';

function getInstrumentType(gmNumber: number): SynthType {
  // 简化映射
  if (gmNumber >= 0 && gmNumber <= 7) return 'synth'; // Piano
  if (gmNumber >= 8 && gmNumber <= 15) return 'metal'; // Chromatic Percussion
  if (gmNumber >= 24 && gmNumber <= 31) return 'pluck'; // Guitar
  if (gmNumber >= 32 && gmNumber <= 39) return 'fm'; // Bass
  if (gmNumber >= 40 && gmNumber <= 55) return 'synth'; // Strings
  if (gmNumber >= 80 && gmNumber <= 87) return 'mono'; // Synth Lead
  if (gmNumber >= 88 && gmNumber <= 95) return 'am'; // Synth Pad
  return 'synth';
}

// 创建合成器
function createSynth(type: SynthType): Tone.PolySynth {
  switch (type) {
    case 'fm':
      return new Tone.PolySynth(Tone.FMSynth, {
        envelope: { attack: 0.01, decay: 0.2, sustain: 0.3, release: 0.5 },
      });
    case 'am':
      return new Tone.PolySynth(Tone.AMSynth, {
        envelope: { attack: 0.3, decay: 0.2, sustain: 0.8, release: 1.0 },
      });
    case 'mono':
      return new Tone.PolySynth(Tone.MonoSynth, {
        oscillator: { type: 'sawtooth' },
        envelope: { attack: 0.01, decay: 0.1, sustain: 0.5, release: 0.3 },
      });
    case 'pluck':
      return new Tone.PolySynth(Tone.Synth, {
        oscillator: { type: 'triangle' },
        envelope: { attack: 0.001, decay: 0.4, sustain: 0, release: 0.4 },
      });
    case 'metal':
      return new Tone.PolySynth(Tone.Synth, {
        oscillator: { type: 'square' },
        envelope: { attack: 0.001, decay: 0.3, sustain: 0.1, release: 0.5 },
      });
    default:
      return new Tone.PolySynth(Tone.Synth, {
        oscillator: { type: 'triangle' },
        envelope: { attack: 0.02, decay: 0.1, sustain: 0.3, release: 0.8 },
      });
  }
}

export interface PlaybackState {
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;
  duration: number;
  progress: number;
}

export class AudioEngine {
  private synths: Map<string, Tone.PolySynth> = new Map();
  private drumSampler: Tone.Sampler | null = null;
  private scheduledEvents: number[] = [];
  private _isPlaying = false;
  private _isPaused = false;
  private _duration = 0;
  private startTime = 0;
  private pauseTime = 0;
  private onStateChange?: (state: PlaybackState) => void;
  private animationFrame?: number;

  async init(): Promise<void> {
    if (Tone.context.state !== 'running') {
      await Tone.start();
    }
    console.log('🎵 Audio engine initialized');
  }

  setStateChangeCallback(callback: (state: PlaybackState) => void): void {
    this.onStateChange = callback;
  }

  private updateState(): void {
    if (this.onStateChange) {
      this.onStateChange(this.getState());
    }
  }

  private startProgressTracking(): void {
    const update = () => {
      if (this._isPlaying && !this._isPaused) {
        this.updateState();
        this.animationFrame = requestAnimationFrame(update);
      }
    };
    update();
  }

  private stopProgressTracking(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = undefined;
    }
  }

  getState(): PlaybackState {
    const currentTime = this._isPlaying
      ? Tone.Transport.seconds
      : this.pauseTime;

    return {
      isPlaying: this._isPlaying && !this._isPaused,
      isPaused: this._isPaused,
      currentTime,
      duration: this._duration,
      progress: this._duration > 0 ? currentTime / this._duration : 0,
    };
  }

  loadMusic(musicData: MusicData): void {
    // 清理之前的资源
    this.dispose();

    // 设置 BPM
    Tone.Transport.bpm.value = musicData.bpm;
    this._duration = musicData.total_duration;

    // 为每个轨道创建合成器
    musicData.tracks.forEach((track, index) => {
      if (track.name === 'Drums') {
        // 鼓轨道使用简单的合成鼓
        const drumSynth = new Tone.MembraneSynth().toDestination();
        this.synths.set(`drum_${index}`, drumSynth as unknown as Tone.PolySynth);
      } else {
        const synthType = getInstrumentType(track.instrument);
        const synth = createSynth(synthType);

        // 设置音量和声像
        const volume = track.volume ?? 1;
        const pan = track.pan ?? 0;

        const panner = new Tone.Panner(pan).toDestination();
        const gain = new Tone.Gain(volume).connect(panner);
        synth.connect(gain);

        this.synths.set(`track_${index}`, synth);
      }
    });

    console.log(`🎵 Loaded ${musicData.tracks.length} tracks`);
  }

  scheduleMusic(musicData: MusicData): void {
    // 清除之前的调度
    this.scheduledEvents.forEach((id) => Tone.Transport.clear(id));
    this.scheduledEvents = [];

    const beatsPerSecond = musicData.bpm / 60;

    musicData.tracks.forEach((track, trackIndex) => {
      const synth = this.synths.get(
        track.name === 'Drums' ? `drum_${trackIndex}` : `track_${trackIndex}`
      );

      if (!synth) return;

      track.notes.forEach((note) => {
        // 将拍数转换为秒
        const startSeconds = note.start_time / beatsPerSecond;
        const durationSeconds = Math.max(0.05, note.duration / beatsPerSecond);

        const eventId = Tone.Transport.schedule((time) => {
          try {
            if (track.name === 'Drums') {
              // 鼓使用固定音高
              (synth as unknown as Tone.MembraneSynth).triggerAttackRelease(
                'C2',
                durationSeconds,
                time,
                note.velocity / 127
              );
            } else {
              const noteName = midiToNoteName(note.pitch);
              synth.triggerAttackRelease(
                noteName,
                durationSeconds,
                time,
                note.velocity / 127
              );
            }
          } catch (e) {
            // 忽略播放错误
          }
        }, startSeconds);

        this.scheduledEvents.push(eventId);
      });
    });

    // 在结束时停止
    const endEventId = Tone.Transport.schedule(() => {
      this.stop();
    }, this._duration);
    this.scheduledEvents.push(endEventId);

    console.log(`🎵 Scheduled ${this.scheduledEvents.length} events`);
  }

  play(): void {
    if (this._isPaused) {
      // 从暂停恢复
      Tone.Transport.start();
      this._isPaused = false;
    } else {
      // 从头开始
      Tone.Transport.start();
      this.startTime = Tone.now();
    }
    this._isPlaying = true;
    this.startProgressTracking();
    this.updateState();
  }

  pause(): void {
    if (this._isPlaying) {
      Tone.Transport.pause();
      this._isPaused = true;
      this.pauseTime = Tone.Transport.seconds;
      this.stopProgressTracking();
      this.updateState();
    }
  }

  stop(): void {
    Tone.Transport.stop();
    Tone.Transport.position = 0;
    this._isPlaying = false;
    this._isPaused = false;
    this.pauseTime = 0;
    this.stopProgressTracking();
    this.updateState();
  }

  seek(time: number): void {
    const wasPlaying = this._isPlaying && !this._isPaused;

    if (wasPlaying) {
      Tone.Transport.pause();
    }

    Tone.Transport.seconds = Math.max(0, Math.min(time, this._duration));

    if (wasPlaying) {
      Tone.Transport.start();
    }

    this.updateState();
  }

  seekToProgress(progress: number): void {
    const time = progress * this._duration;
    this.seek(time);
  }

  get isPlaying(): boolean {
    return this._isPlaying && !this._isPaused;
  }

  get isPaused(): boolean {
    return this._isPaused;
  }

  get currentTime(): number {
    return Tone.Transport.seconds;
  }

  get duration(): number {
    return this._duration;
  }

  dispose(): void {
    this.stop();

    // 清除所有调度的事件
    this.scheduledEvents.forEach((id) => Tone.Transport.clear(id));
    this.scheduledEvents = [];

    // 释放所有合成器
    this.synths.forEach((synth) => {
      try {
        synth.dispose();
      } catch (e) {
        // 忽略释放错误
      }
    });
    this.synths.clear();

    if (this.drumSampler) {
      this.drumSampler.dispose();
      this.drumSampler = null;
    }

    console.log('🎵 Audio engine disposed');
  }
}

// 单例导出
export const audioEngine = new AudioEngine();