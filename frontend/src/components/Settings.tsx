/**
 * 高级设置组件
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings as SettingsIcon, ChevronDown, ChevronUp } from 'lucide-react';
import { clsx } from 'clsx';
import { useAppStore } from '../store';

interface SettingsProps {
  disabled?: boolean;
}

export function Settings({ disabled }: SettingsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const {
    bpm,
    maxCommits,
    includeDrums,
    includeBass,
    includeChords,
    setBpm,
    setMaxCommits,
    setIncludeDrums,
    setIncludeBass,
    setIncludeChords,
  } = useAppStore();

  return (
    <div className="w-full max-w-md mx-auto">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className={clsx(
          'w-full flex items-center justify-center gap-2 py-2',
          'text-sm text-gray-400 hover:text-gray-300 transition-colors',
          { 'opacity-50 cursor-not-allowed': disabled }
        )}
      >
        <SettingsIcon className="w-4 h-4" />
        <span>Advanced Settings</span>
        {isOpen ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="glass rounded-xl p-4 mt-2 space-y-4">
              {/* BPM */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <label className="text-gray-400">BPM</label>
                  <span className="text-white font-medium">{bpm}</span>
                </div>
                <input
                  type="range"
                  min="60"
                  max="200"
                  value={bpm}
                  onChange={(e) => setBpm(Number(e.target.value))}
                  disabled={disabled}
                  className="w-full accent-purple-500"
                />
              </div>

              {/* Max Commits */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <label className="text-gray-400">Max Commits</label>
                  <span className="text-white font-medium">{maxCommits}</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="500"
                  step="10"
                  value={maxCommits}
                  onChange={(e) => setMaxCommits(Number(e.target.value))}
                  disabled={disabled}
                  className="w-full accent-purple-500"
                />
              </div>

              {/* Toggles */}
              <div className="flex flex-wrap gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeDrums}
                    onChange={(e) => setIncludeDrums(e.target.checked)}
                    disabled={disabled}
                    className="accent-purple-500"
                  />
                  <span className="text-sm text-gray-300">Drums</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeBass}
                    onChange={(e) => setIncludeBass(e.target.checked)}
                    disabled={disabled}
                    className="accent-purple-500"
                  />
                  <span className="text-sm text-gray-300">Bass</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeChords}
                    onChange={(e) => setIncludeChords(e.target.checked)}
                    disabled={disabled}
                    className="accent-purple-500"
                  />
                  <span className="text-sm text-gray-300">Chords</span>
                </label>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}