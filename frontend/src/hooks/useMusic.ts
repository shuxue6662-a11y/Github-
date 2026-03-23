/**
 * 音乐播放相关 Hook
 */
import { useState, useCallback, useEffect, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { audioEngine, type PlaybackState } from '../services/audioEngine';
import { repoApi } from '../services/api';
import type { MusicResponse, GenerateRequest, MusicData } from '../types';

export interface UseMusicOptions {
  onGenerated?: (data: MusicResponse) => void;
  onError?: (error: Error) => void;
}

export interface UseMusicReturn {
  // 状态
  musicData: MusicResponse | null;
  isGenerating: boolean;
  isLoaded: boolean;
  playbackState: PlaybackState;
  error: Error | null;

  // 操作
  generate: (params: GenerateRequest) => Promise<void>;
  play: () => Promise<void>;
  pause: () => void;
  stop: () => void;
  seek: (time: number) => void;
  seekToProgress: (progress: number) => void;
  downloadMidi: () => void;
  reset: () => void;
}

const initialPlaybackState: PlaybackState = {
  isPlaying: false,
  isPaused: false,
  currentTime: 0,
  duration: 0,
  progress: 0,
};

export function useMusic(options: UseMusicOptions = {}): UseMusicReturn {
  const { onGenerated, onError } = options;

  const [musicData, setMusicData] = useState<MusicResponse | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [playbackState, setPlaybackState] = useState<PlaybackState>(initialPlaybackState);
  const [error, setError] = useState<Error | null>(null);

  const isInitialized = useRef(false);

  // 生成音乐
  const generateMutation = useMutation({
    mutationFn: async (params: GenerateRequest) => {
      return await repoApi.generateMusic(params);
    },
    onSuccess: async (data) => {
      setMusicData(data);
      setError(null);

      try {
        // 初始化音频引擎
        if (!isInitialized.current) {
          await audioEngine.init();
          isInitialized.current = true;
        }

        // 设置状态回调
        audioEngine.setStateChangeCallback(setPlaybackState);

        // 加载音乐
        audioEngine.loadMusic(data.music_data);
        audioEngine.scheduleMusic(data.music_data);
        setIsLoaded(true);

        // 更新初始状态
        setPlaybackState({
          ...initialPlaybackState,
          duration: data.music_data.total_duration,
        });

        onGenerated?.(data);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to load music');
        setError(error);
        onError?.(error);
      }
    },
    onError: (err) => {
      const error = err instanceof Error ? err : new Error('Failed to generate music');
      setError(error);
      onError?.(error);
    },
  });

  // 生成
  const generate = useCallback(
    async (params: GenerateRequest) => {
      // 停止当前播放
      if (isLoaded) {
        audioEngine.stop();
        setIsLoaded(false);
      }
      setMusicData(null);
      setError(null);
      setPlaybackState(initialPlaybackState);

      await generateMutation.mutateAsync(params);
    },
    [isLoaded]
  );

  // 播放
  const play = useCallback(async () => {
    if (!isLoaded) return;

    try {
      if (!isInitialized.current) {
        await audioEngine.init();
        isInitialized.current = true;
      }
      audioEngine.play();
    } catch (err) {
      console.error('Failed to play:', err);
    }
  }, [isLoaded]);

  // 暂停
  const pause = useCallback(() => {
    if (isLoaded) {
      audioEngine.pause();
    }
  }, [isLoaded]);

  // 停止
  const stop = useCallback(() => {
    if (isLoaded) {
      audioEngine.stop();
    }
  }, [isLoaded]);

  // 跳转
  const seek = useCallback(
    (time: number) => {
      if (isLoaded) {
        audioEngine.seek(time);
      }
    },
    [isLoaded]
  );

  // 按进度跳转
  const seekToProgress = useCallback(
    (progress: number) => {
      if (isLoaded) {
        audioEngine.seekToProgress(progress);
      }
    },
    [isLoaded]
  );

  // 下载 MIDI
  const downloadMidi = useCallback(() => {
    if (musicData?.midi_base64) {
      const filename = musicData.repo_name.replace('/', '_') + '_rhythm';
      repoApi.downloadMidi(musicData.midi_base64, filename);
    }
  }, [musicData]);

  // 重置
  const reset = useCallback(() => {
    audioEngine.dispose();
    setMusicData(null);
    setIsLoaded(false);
    setPlaybackState(initialPlaybackState);
    setError(null);
    isInitialized.current = false;
  }, []);

  // 清理
  useEffect(() => {
    return () => {
      audioEngine.dispose();
    };
  }, []);

  return {
    musicData,
    isGenerating: generateMutation.isPending,
    isLoaded,
    playbackState,
    error,
    generate,
    play,
    pause,
    stop,
    seek,
    seekToProgress,
    downloadMidi,
    reset,
  };
}