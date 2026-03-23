/**
 * 音频可视化组件
 */
import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import type { MusicData } from '../types';
import { generateWaveformData, getTrackColor } from '../utils/midiToTone';

interface VisualizerProps {
  musicData: MusicData;
  progress: number;
  isPlaying: boolean;
}

export function Visualizer({ musicData, progress, isPlaying }: VisualizerProps) {
  const bars = 60;
  const waveformData = useMemo(
    () => generateWaveformData(musicData, bars),
    [musicData]
  );

  const currentBar = Math.floor(progress * bars);

  return (
    <div className="w-full max-w-2xl mx-auto h-32 flex items-end justify-center gap-[2px] px-4">
      {waveformData.map((value, index) => {
        const height = Math.max(8, value * 100);
        const isPast = index < currentBar;
        const isCurrent = index === currentBar;

        return (
          <motion.div
            key={index}
            className={clsx('w-1.5 rounded-full transition-colors duration-150', {
              'bg-purple-400': isPast,
              'bg-pink-400': isCurrent,
              'bg-white/20': !isPast && !isCurrent,
            })}
            animate={{
              height: isPlaying && isCurrent ? [height, height * 1.5, height] : height,
            }}
            transition={{
              duration: 0.3,
              repeat: isPlaying && isCurrent ? Infinity : 0,
            }}
            style={{ height }}
          />
        );
      })}
    </div>
  );
}

/**
 * 简单的动态波形（无实际音频数据时使用）
 */
export function SimpleWaveform({ isPlaying }: { isPlaying: boolean }) {
  const bars = 40;

  return (
    <div className="w-full h-24 flex items-center justify-center gap-[3px]">
      {Array.from({ length: bars }).map((_, index) => (
        <motion.div
          key={index}
          className="w-1 bg-purple-400 rounded-full"
          animate={
            isPlaying
              ? {
                  height: [16, 32 + Math.random() * 40, 16],
                }
              : { height: 16 }
          }
          transition={{
            duration: 0.5 + Math.random() * 0.3,
            repeat: Infinity,
            delay: index * 0.02,
          }}
          style={{ height: 16 }}
        />
      ))}
    </div>
  );
}