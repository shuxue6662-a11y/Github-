/**
 * API 调用服务
 */
import axios from 'axios';
import type { MusicData } from './audioEngine';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s，大 repo 需要时间
});

export interface RepoInfo {
  name: string;
  full_name: string;
  description: string | null;
  stars: number;
  forks: number;
  language: string | null;
}

export interface MusicResponse {
  success: boolean;
  repo_name: string;
  style: string;
  bpm: number;
  duration: number;
  music_data: MusicData;
  midi_base64: string | null;
}

export interface GenerateRequest {
  repo_url: string;
  style?: string;
  bpm?: number;
  scale?: string;
  max_commits?: number;
}

export const repoApi = {
  /**
   * 生成音乐
   */
  async generateMusic(params: GenerateRequest): Promise<MusicResponse> {
    const response = await api.post<MusicResponse>('/api/v1/music/generate', params);
    return response.data;
  },
  
  /**
   * 获取仓库信息
   */
  async getRepoInfo(owner: string, repo: string): Promise<RepoInfo> {
    const response = await api.get<RepoInfo>(`/api/v1/github/repo/${owner}/${repo}`);
    return response.data;
  },
  
  /**
   * 获取可用风格
   */
  async getStyles(): Promise<{ styles: { id: string; name: string }[] }> {
    const response = await api.get('/api/v1/music/styles');
    return response.data;
  },
  
  /**
   * 下载 MIDI 文件
   */
  downloadMidi(midiBase64: string, filename: string): void {
    const byteCharacters = atob(midiBase64);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'audio/midi' });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(url);
  },
};