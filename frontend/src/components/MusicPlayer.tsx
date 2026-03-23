/**
 * 音乐播放器组件
 */
import React from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  Pause,
  Square,
  Download,
  SkipBack,
  Volume2,
  Music2,
} from 'lucide-react';
import { clsx } from 'clsx';
import type { PlaybackState, MusicResponse } from '../types';
import { formatTime } from '../utils/midiToTone';

interface MusicPlayerProps {
  musicData: MusicResponse;
  playbackState: PlaybackState;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onSeek: (progress: number) => void;
  onDownload: () => void;
}

export function MusicPlayer({
  musicData,
  playbackState,
  onPlay,
  onPause,
  onStop,
  onSeek,
  onDownload,
}: MusicPlayerProps) {
  const { isPlaying, currentTime, duration, progress } = playbackState;

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const newProgress = x / rect.width;
    onSeek(Math.max(0, Math.min(1, newProgress)));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto glass rounded-3xl p-6"
    >
      {/* 头部信息 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-purple-600/30 flex items-center justify-center">
            <Music2 className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">{musicData.repo_name}</h3>
            <p className="text-sm text-gray-400">
              {musicData.style} • {musicData.bpm} BPM
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span>{musicData.total_notes} notes</span>
          <span>•</span>
          <span>{musicData.total_tracks} tracks</span>
        </div>
      </div>

      {/* 进度条 */}
      <div className="mb-4">
        <div
          className="h-2 bg-white/10 rounded-full cursor-pointer overflow-hidden"
          onClick={handleProgressClick}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
            style={{ width: `${progress * 100}%` }}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-400">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* 控制按钮 */}
      <div className="flex items-center justify-center gap-4">
        {/* 重置 */}
        <button
          onClick={onStop}
          className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          title="Stop"
        >
          <SkipBack className="w-5 h-5" />
        </button>

        {/* 播放/暂停 */}
        <button
          onClick={isPlaying ? onPause : onPlay}
          className={clsx(
            'w-16 h-16 rounded-full flex items-center justify-center transition-all',
            'bg-gradient-to-r from-purple-600 to-pink-600',
            'hover:from-purple-500 hover:to-pink-500',
            'shadow-lg shadow-purple-500/30'
          )}
        >
          {isPlaying ? (
            <Pause className="w-8 h-8 text-white" />
          ) : (
            <Play className="w-8 h-8 text-white ml-1" />
          )}
        </button>

        {/* 停止 */}
        <button
          onClick={onStop}
          className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          title="Reset"
        >
          <Square className="w-4 h-4" />
        </button>

        {/* 下载 */}
        <button
          onClick={onDownload}
          className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          title="Download MIDI"
        >
          <Download className="w-5 h-5" />
        </button>
      </div>

      {/* 统计信息 */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="flex justify-center gap-6 text-sm">
          <div className="text-center">
            <p className="text-gray-400">Commits</p>
            <p className="font-semibold text-white">{musicData.commits_processed}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400">Duration</p>
            <p className="font-semibold text-white">{formatTime(musicData.duration)}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-400">Generated in</p>
            <p className="font-semibold text-white">{musicData.generation_time_ms}ms</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}