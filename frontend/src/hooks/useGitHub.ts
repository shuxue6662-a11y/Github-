/**
 * GitHub 相关 Hook
 */
import { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { repoApi } from '../services/api';
import type { RepoInfo, StyleInfo } from '../types';

/**
 * 解析 GitHub URL
 */
export function parseGitHubUrl(url: string): { owner: string; repo: string } | null {
  const trimmed = url.trim().replace(/\/$/, '');

  // 尝试不同的模式
  const patterns = [
    /github\.com\/([^\/]+)\/([^\/\?#]+)/,
    /^([^\/]+)\/([^\/\?#]+)$/,
  ];

  for (const pattern of patterns) {
    const match = trimmed.match(pattern);
    if (match) {
      return {
        owner: match[1],
        repo: match[2].replace(/\.git$/, ''),
      };
    }
  }

  return null;
}

/**
 * 仓库验证 Hook
 */
export function useRepoValidation() {
  const [repoUrl, setRepoUrl] = useState('');
  const [debouncedUrl, setDebouncedUrl] = useState('');

  // 防抖
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedUrl(repoUrl);
    }, 500);

    return () => clearTimeout(timer);
  }, [repoUrl]);

  const validationQuery = useQuery({
    queryKey: ['validateRepo', debouncedUrl],
    queryFn: () => repoApi.validateRepo(debouncedUrl),
    enabled: debouncedUrl.length > 0,
    retry: false,
    staleTime: 60000, // 1 分钟
  });

  const isValid = validationQuery.data?.valid ?? false;
  const validationError = validationQuery.data?.error;
  const repoInfo = validationQuery.data?.valid
    ? {
        full_name: validationQuery.data.full_name,
        stars: validationQuery.data.stars,
      }
    : null;

  return {
    repoUrl,
    setRepoUrl,
    isValidating: validationQuery.isFetching,
    isValid,
    validationError,
    repoInfo,
  };
}

/**
 * 音乐风格 Hook
 */
export function useMusicStyles() {
  const stylesQuery = useQuery({
    queryKey: ['musicStyles'],
    queryFn: () => repoApi.getStyles(),
    staleTime: Infinity, // 风格列表不会变
  });

  return {
    styles: stylesQuery.data ?? [],
    isLoading: stylesQuery.isLoading,
    error: stylesQuery.error,
  };
}

/**
 * 仓库信息 Hook
 */
export function useRepoInfo(owner: string, repo: string, enabled: boolean = true) {
  const repoQuery = useQuery({
    queryKey: ['repoInfo', owner, repo],
    queryFn: () => repoApi.getRepoInfo(owner, repo),
    enabled: enabled && !!owner && !!repo,
    staleTime: 300000, // 5 分钟
  });

  return {
    repoInfo: repoQuery.data,
    isLoading: repoQuery.isLoading,
    error: repoQuery.error,
  };
}

/**
 * 热门仓库示例
 */
export const POPULAR_REPOS = [
  { name: 'React', url: 'facebook/react', emoji: '⚛️' },
  { name: 'Vue', url: 'vuejs/vue', emoji: '💚' },
  { name: 'Next.js', url: 'vercel/next.js', emoji: '▲' },
  { name: 'TypeScript', url: 'microsoft/TypeScript', emoji: '🔷' },
  { name: 'Rust', url: 'rust-lang/rust', emoji: '🦀' },
  { name: 'Go', url: 'golang/go', emoji: '🐹' },
  { name: 'Python', url: 'python/cpython', emoji: '🐍' },
  { name: 'Linux', url: 'torvalds/linux', emoji: '🐧' },
];