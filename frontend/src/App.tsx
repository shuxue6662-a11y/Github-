/**
 * RepoRhythm 主应用
 */
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Music, Github, Heart } from 'lucide-react';

import {
  RepoInput,
  StyleSelector,
  MusicPlayer,
  Visualizer,
  CommitTimeline,
  Settings,
  ErrorMessage,
  LoadingState,
} from './components';
import { useMusic } from './hooks/useMusic';
import { useAppStore } from './store';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 60000,
    },
  },
});

function RepoRhythmApp() {
  const {
    selectedStyle,
    bpm,
    maxCommits,
    includeDrums,
    includeBass,
    includeChords,
  } = useAppStore();

  const {
    musicData,
    isGenerating,
    isLoaded,
    playbackState,
    error,
    generate,
    play,
    pause,
    stop,
    seekToProgress,
    downloadMidi,
    reset,
  } = useMusic();

  const handleGenerate = async (repoUrl: string) => {
    await generate({
      repo_url: repoUrl,
      style: selectedStyle,
      bpm,
      max_commits: maxCommits,
      include_drums: includeDrums,
      include_bass: includeBass,
      include_chords: includeChords,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/50 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8 md:py-16">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-4 flex items-center justify-center gap-4">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Music className="w-10 h-10 md:w-14 md:h-14 text-purple-400" />
            </motion.div>
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              RepoRhythm
            </span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto">
            Transform your GitHub commit history into beautiful music.
            <br />
            Every commit tells a story — now you can hear it.
          </p>
        </motion.header>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Input Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <RepoInput
              onSubmit={handleGenerate}
              isLoading={isGenerating}
              disabled={isGenerating}
            />
          </motion.section>

          {/* Style Selector */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StyleSelector disabled={isGenerating} />
          </motion.section>

          {/* Settings */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Settings disabled={isGenerating} />
          </motion.section>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <ErrorMessage message={error.message} onRetry={reset} />
            )}
          </AnimatePresence>

          {/* Loading State */}
          <AnimatePresence>
            {isGenerating && <LoadingState />}
          </AnimatePresence>

          {/* Music Player */}
          <AnimatePresence>
            {isLoaded && musicData && (
              <motion.section
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="space-y-6"
              >
                {/* Visualizer */}
                <Visualizer
                  musicData={musicData.music_data}
                  progress={playbackState.progress}
                  isPlaying={playbackState.isPlaying}
                />

                {/* Player */}
                <MusicPlayer
                  musicData={musicData}
                  playbackState={playbackState}
                  onPlay={play}
                  onPause={pause}
                  onStop={stop}
                  onSeek={seekToProgress}
                  onDownload={downloadMidi}
                />

                {/* Timeline */}
                <div className="pt-4">
                  <CommitTimeline
                    musicData={musicData.music_data}
                    progress={playbackState.progress}
                  />
                </div>
              </motion.section>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-16 text-center text-gray-500 text-sm"
        >
          <p className="flex items-center justify-center gap-2">
            Made with <Heart className="w-4 h-4 text-red-400" /> by developers, for developers
          </p>
          <p className="mt-2 flex items-center justify-center gap-2">
            <Github className="w-4 h-4" />
            <a
              href="https://github.com/yourusername/repo-rhythm"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-purple-400 transition-colors"
            >
              Star on GitHub
            </a>
          </p>
        </motion.footer>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RepoRhythmApp />
    </QueryClientProvider>
  );
}