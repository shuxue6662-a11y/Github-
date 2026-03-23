/**
 * 仓库输入组件
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Github, CheckCircle, XCircle, Loader2, Star, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';
import { useRepoValidation, POPULAR_REPOS } from '../hooks/useGitHub';

interface RepoInputProps {
  onSubmit: (url: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function RepoInput({ onSubmit, isLoading, disabled }: RepoInputProps) {
  const { repoUrl, setRepoUrl, isValidating, isValid, validationError, repoInfo } =
    useRepoValidation();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid && !disabled) {
      onSubmit(repoUrl);
    }
  };

  const handleQuickSelect = (url: string) => {
    setRepoUrl(url);
    // 自动提交
    setTimeout(() => onSubmit(url), 100);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit}>
        {/* 主输入框 */}
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <Github className="w-5 h-5" />
          </div>

          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="Enter GitHub repo (e.g., facebook/react)"
            disabled={disabled || isLoading}
            className={clsx(
              'w-full pl-12 pr-32 py-4 rounded-2xl',
              'bg-white/10 backdrop-blur-md',
              'border-2 transition-all duration-200',
              'text-white placeholder-gray-400',
              'focus:outline-none',
              {
                'border-white/20 focus:border-purple-400': !isValid && !validationError,
                'border-green-400/50 focus:border-green-400': isValid,
                'border-red-400/50 focus:border-red-400': validationError,
                'opacity-50 cursor-not-allowed': disabled || isLoading,
              }
            )}
          />

          {/* 验证状态指示器 */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
            <AnimatePresence mode="wait">
              {isValidating && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                >
                  <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                </motion.div>
              )}

              {!isValidating && isValid && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-2"
                >
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  {repoInfo?.stars && (
                    <span className="text-sm text-gray-400 flex items-center gap-1">
                      <Star className="w-3 h-3" />
                      {repoInfo.stars.toLocaleString()}
                    </span>
                  )}
                </motion.div>
              )}

              {!isValidating && validationError && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                >
                  <XCircle className="w-5 h-5 text-red-400" />
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={!isValid || disabled || isLoading}
              className={clsx(
                'px-4 py-2 rounded-xl font-medium transition-all',
                'flex items-center gap-2',
                {
                  'bg-purple-600 hover:bg-purple-500 text-white': isValid && !isLoading,
                  'bg-gray-600 text-gray-400 cursor-not-allowed': !isValid || isLoading,
                }
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* 错误提示 */}
        <AnimatePresence>
          {validationError && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-2 text-sm text-red-400 pl-4"
            >
              {validationError}
            </motion.p>
          )}
        </AnimatePresence>
      </form>

      {/* 快速选择 */}
      <div className="mt-6">
        <p className="text-sm text-gray-400 mb-3 text-center">
          Or try a popular repository:
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {POPULAR_REPOS.map((repo) => (
            <button
              key={repo.url}
              onClick={() => handleQuickSelect(repo.url)}
              disabled={disabled || isLoading}
              className={clsx(
                'px-3 py-1.5 rounded-full text-sm',
                'bg-white/5 hover:bg-white/10 border border-white/10',
                'transition-all duration-200',
                'flex items-center gap-1.5',
                {
                  'opacity-50 cursor-not-allowed': disabled || isLoading,
                }
              )}
            >
              <span>{repo.emoji}</span>
              <span>{repo.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}