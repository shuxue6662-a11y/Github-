/**
 * Commit 时间线可视化
 */
import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import type { MusicData } from '../types';
import { getTrackColor } from '../utils/midiToTone';

interface CommitTimelineProps {
  musicData: MusicData;
  progress: number;
}

export function CommitTimeline({ musicData, progress }: CommitTimelineProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <h4 className="text-sm text-gray-400 mb-3">Tracks</h4>
      <div className="space-y-2">
        {musicData.tracks.map((track, index) => (
          <div key={track.name} className="flex items-center gap-3">
            {/* 轨道名称 */}
            <div className="w-20 text-xs text-gray-400 truncate">{track.name}</div>

            {/* 轨道可视化 */}
            <div className="flex-1 h-6 bg-white/5 rounded overflow-hidden relative">
              {/* 进度指示器 */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-white/50 z-10"
                style={{ left: `${progress * 100}%` }}
              />

              {/* 音符块 */}
              <div className="relative w-full h-full">
                {track.notes.slice(0, 200).map((note, noteIndex) => {
                  const left = (note.start_time / musicData.total_beats) * 100;
                  const width = Math.max(
                    0.5,
                    (note.duration / musicData.total_beats) * 100
                  );

                  return (
                    <motion.div
                      key={noteIndex}
                      className="absolute top-1 bottom-1 rounded-sm"
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                        backgroundColor: getTrackColor(index),
                        opacity: 0.6 + (note.velocity / 127) * 0.4,
                      }}
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: noteIndex * 0.002 }}
                    />
                  );
                })}
              </div>
            </div>

            {/* 音符数量 */}
            <div className="w-12 text-xs text-gray-500 text-right">
              {track.notes.length}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}