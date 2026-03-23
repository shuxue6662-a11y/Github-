/**
 * RepoRhythm 主应用
 */
import { useState } from 'react';
import { QueryClient, QueryClientProvider, useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Music, Github, Play, Pause, Download, Loader2 } from 'lucide-react';

import { repoApi, type GenerateRequest, type MusicResponse } from './services/api';
import { audioEngine } from './services/audioEngine';

const queryClient = new QueryClient();

function RepoRhythmApp() {
  const [repoUrl, setRepoUrl] = useState('');
  const [style, setStyle] = useState('electronic');
  const [isPlaying, setIsPlaying] = useState(false);
  const [musicData, setMusicData] = useState<MusicResponse | null>(null);
  
  const generateMutation = useMutation({
    mutationFn: (params: GenerateRequest) => repoApi.generateMusic(params),
    onSuccess: async (data) => {
      setMusicData(data);
      
      // 初始化音频引擎
      await audioEngine.init();
      audioEngine.loadMusic(data.music_data);
      audioEngine.scheduleMusic(data.music_data);
    },
  });
  
  const handleGenerate = () => {
    if (!repoUrl.trim()) return;
    
    generateMutation.mutate({
      repo_url: repoUrl,
      style,
      max_commits: 200,
    });
  };
  
  const handlePlayPause = () => {
    if (isPlaying) {
      audioEngine.pause();
    } else {
      audioEngine.play();
    }
    setIsPlaying(!isPlaying);
  };
  
  const handleDownload = () => {
    if (musicData?.midi_base64) {
      repoApi.downloadMidi(
        musicData.midi_base64,
        `${musicData.repo_name.replace('/', '_')}_rhythm.mid`
      );
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold mb-4 flex items-center justify-center gap-3">
            <Music className="w-12 h-12 text-purple-400" />
            RepoRhythm
          </h1>
          <p className="text-xl text-gray-300">
            Transform your GitHub commit history into music
          </p>
        </motion.div>
        
        {/* Input Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto mb-12"
        >
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-xl">
            <div className="flex gap-4 mb-4">
              <div className="flex-1 relative">
                <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Enter GitHub repo URL (e.g., facebook/react)"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-white/10 rounded-xl border border-white/20 focus:border-purple-400 focus:outline-none transition-colors"
                />
              </div>
            </div>
            
            <div className="flex gap-4">
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="px-4 py-3 bg-white/10 rounded-xl border border-white/20 focus:border-purple-400 focus:outline-none"
              >
                <option value="electronic">🎹 Electronic</option>
                <option value="classical">🎻 Classical</option>
                <option value="rock">🎸 Rock</option>
                <option value="jazz">🎷 Jazz</option>
                <option value="ambient">🌊 Ambient</option>
                <option value="chiptune">👾 Chiptune</option>
              </select>
              
              <button
                onClick={handleGenerate}
                disabled={generateMutation.isPending || !repoUrl.trim()}
                className="flex-1 px-6 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Composing...
                  </>
                ) : (
                  <>
                    <Music className="w-5 h-5" />
                    Generate Music
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.div>
        
        {/* Player Section */}
        <AnimatePresence>
          {musicData && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="max-w-2xl mx-auto"
            >
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-xl">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold mb-2">{musicData.repo_name}</h2>
                  <p className="text-gray-400">
                    {musicData.style} • {musicData.bpm} BPM • {Math.round(musicData.duration)}s
                  </p>
                </div>
                
                {/* Waveform Placeholder */}
                <div className="h-24 bg-white/5 rounded-xl mb-6 flex items-center justify-center">
                  <div className="flex gap-1">
                    {Array.from({ length: 40 }).map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-1 bg-purple-400 rounded-full"
                        animate={{
                          height: isPlaying 
                            ? [20, 40 + Math.random() * 40, 20]
                            : 20,
                        }}
                        transition={{
                          duration: 0.5,
                          repeat: Infinity,
                          delay: i * 0.05,
                        }}
                      />
                    ))}
                  </div>
                </div>
                
                {/* Controls */}
                <div className="flex justify-center gap-4">
                  <button
                    onClick={handlePlayPause}
                    className="w-16 h-16 bg-purple-600 hover:bg-purple-500 rounded-full flex items-center justify-center transition-colors"
                  >
                    {isPlaying ? (
                      <Pause className="w-8 h-8" />
                    ) : (
                      <Play className="w-8 h-8 ml-1" />
                    )}
                  </button>
                  
                  <button
                    onClick={handleDownload}
                    className="w-16 h-16 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors"
                    title="Download MIDI"
                  >
                    <Download className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Error Display */}
        {generateMutation.isError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-2xl mx-auto mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-center"
          >
            Failed to generate music. Please check the repository URL.
          </motion.div>
        )}
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