/**
 * API 服务
 */
import axios, { AxiosError } from 'axios';
import type { MusicResponse, GenerateRequest, StyleInfo, RepoInfo } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const data = error.response.data as { detail?: string; error?: string };
      const message = data.detail || data.error || 'An error occurred';
      throw new Error(message);
    } else if (error.request) {
      throw new Error('Network error. Please check your connection.');
    }
    throw error;
  }
);

export const repoApi = {
  /**
   * 生成音乐
   */
  async generateMusic(params: GenerateRequest): Promise<MusicResponse> {
    const response = await api.post<MusicResponse>('/api/v1/music/generate', {
      repo_url: params.repo_url,
      style: params.style || 'electronic',
      bpm: params.bpm || 120,
      scale: params.scale || 'C_MAJOR',
      max_commits: params.max_commits || 200,
      include_drums: params.include_drums ?? true,
      include_bass: params.include_bass ?? true,
      include_chords: params.include_chords ?? true,
    });
    return response.data;
  },

  /**
   * 获取可用风格
   */
  async getStyles(): Promise<StyleInfo[]> {
    const response = await api.get<{ styles: StyleInfo[] }>('/api/v1/music/styles');
    return response.data.styles;
  },

  /**
   * 验证仓库
   */
  async validateRepo(url: string): Promise<{
    valid: boolean;
    error?: string;
    full_name?: string;
    stars?: number;
  }> {
    const response = await api.get('/api/v1/github/validate', {
      params: { url },
    });
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
   * 下载 MIDI 文件
   */
  downloadMidi(midiBase64: string, filename: string): void {
    try {
      // Base64 解码
      const byteCharacters = atob(midiBase64);
      const byteNumbers = new Array(byteCharacters.length);

      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }

      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'audio/midi' });

      // 创建下载链接
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename.endsWith('.mid') ? filename : `${filename}.mid`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // 清理
      setTimeout(() => URL.revokeObjectURL(url), 100);
    } catch (error) {
      console.error('Failed to download MIDI:', error);
      throw new Error('Failed to download MIDI file');
    }
  },

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

export default repoApi;