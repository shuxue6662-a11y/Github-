/**
 * Zustand 状态管理
 */
import { create } from 'zustand';
import type { MusicStyle } from '../types';

interface AppState {
  // 设置
  selectedStyle: MusicStyle;
  bpm: number;
  maxCommits: number;
  includeDrums: boolean;
  includeBass: boolean;
  includeChords: boolean;

  // 操作
  setStyle: (style: MusicStyle) => void;
  setBpm: (bpm: number) => void;
  setMaxCommits: (max: number) => void;
  setIncludeDrums: (include: boolean) => void;
  setIncludeBass: (include: boolean) => void;
  setIncludeChords: (include: boolean) => void;
  resetSettings: () => void;
}

const defaultSettings = {
  selectedStyle: 'electronic' as MusicStyle,
  bpm: 120,
  maxCommits: 200,
  includeDrums: true,
  includeBass: true,
  includeChords: true,
};

export const useAppStore = create<AppState>((set) => ({
  ...defaultSettings,

  setStyle: (style) => set({ selectedStyle: style }),
  setBpm: (bpm) => set({ bpm: Math.max(60, Math.min(200, bpm)) }),
  setMaxCommits: (max) => set({ maxCommits: Math.max(10, Math.min(500, max)) }),
  setIncludeDrums: (include) => set({ includeDrums: include }),
  setIncludeBass: (include) => set({ includeBass: include }),
  setIncludeChords: (include) => set({ includeChords: include }),
  resetSettings: () => set(defaultSettings),
}));