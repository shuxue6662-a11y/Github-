/**
 * 音乐风格选择器
 */
import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { useMusicStyles } from '../hooks/useGitHub';
import { useAppStore } from '../store';
import type { MusicStyle } from '../types';

const STYLE_EMOJIS: Record<string, string> = {
  electronic: '🎹',
  classical: '🎻',
  rock: '🎸',
  jazz: '🎷',
  ambient: '🌊',
  chiptune: '👾',
  lofi: '☕',
  orchestral: '🎼',
};

interface StyleSelectorProps {
  disabled?: boolean;
}

export function StyleSelector({ disabled }: StyleSelectorProps) {
  const { styles, isLoading } = useMusicStyles();
  const { selectedStyle, setStyle } = useAppStore();

  if (isLoading) {
    return (
      <div className="flex justify-center gap-2">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="w-24 h-20 rounded-xl bg-white/5 animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <h3 className="text-sm text-gray-400 mb-3 text-center">Select Style</h3>
      <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
        {styles.map((style) => (
          <motion.button
            key={style.id}
            onClick={() => setStyle(style.id as MusicStyle)}
            disabled={disabled}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={clsx(
              'p-3 rounded-xl flex flex-col items-center gap-1',
              'transition-all duration-200',
              'border-2',
              {
                'bg-purple-600/30 border-purple-400': selectedStyle === style.id,
                'bg-white/5 border-transparent hover:bg-white/10 hover:border-white/20':
                  selectedStyle !== style.id,
                'opacity-50 cursor-not-allowed': disabled,
              }
            )}
          >
            <span className="text-2xl">{STYLE_EMOJIS[style.id] || '🎵'}</span>
            <span className="text-xs text-gray-300 font-medium">
              {style.name.split(' ')[0]}
            </span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}