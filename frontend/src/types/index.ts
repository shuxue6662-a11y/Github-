/**
 * 完整类型定义
 */

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
  volume?: number;
  pan?: number;
}

export interface MusicData {
  bpm: number;
  time_signature: [number, number];
  total_beats: number;
  total_duration: number;
  scale: string;
  style: string;
  tracks: TrackData[];
}

export interface RepoInfo {
  name: string;
  full_name: string;
  description: string | null;
  stars: number;
  forks: number;
  watchers?: number;
  language: string | null;
  topics?: string[];
}

export interface MusicResponse {
  success: boolean;
  repo_name: string;
  style: string;
  bpm: number;
  scale: string;
  duration: number;
  total_tracks: number;
  total_notes: number;
  music_data: MusicData;
  midi_base64: string | null;
  commits_processed: number;
  generation_time_ms: number;
}

export interface GenerateRequest {
  repo_url: string;
  style?: string;
  bpm?: number;
  scale?: string;
  max_commits?: number;
  include_drums?: boolean;
  include_bass?: boolean;
  include_chords?: boolean;
}

export interface StyleInfo {
  id: string;
  name: string;
  description: string;
  emoji: string;
  bpm_range: [number, number];
}

export type MusicStyle =
  | 'electronic'
  | 'classical'
  | 'rock'
  | 'jazz'
  | 'ambient'
  | 'chiptune'
  | 'lofi'
  | 'orchestral';

export interface PlaybackState {
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;
  duration: number;
  progress: number;
}

export interface CommitData {
  sha: string;
  message: string;
  author: string;
  timestamp: string;
  additions: number;
  deletions: number;
  commit_type: string;
}

export interface AnalysisResponse {
  repo_info: RepoInfo;
  analysis: {
    total_commits: number;
    date_range_days: number;
    avg_commits_per_day: number;
    top_contributors: Array<{
      name: string;
      commits: number;
      percentage: number;
    }>;
    commit_type_distribution: Record<string, number>;
  };
}