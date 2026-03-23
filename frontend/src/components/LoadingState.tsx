/**
 * 加载状态组件
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Music, GitCommit, Wand2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Generating your music...' }: LoadingStateProps) {
  const steps = [
    { icon: GitCommit, label: 'Fetching commits', delay: 0 },
    { icon: Wand2, label: 'Analyzing patterns', delay: 0.3 },
    { icon: Music, label: 'Composing music', delay: 0.6 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-md mx-auto text-center py-12"
    >
      {/* 动画图标 */}
      <div className="flex justify-center gap-4 mb-8">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: step.delay, duration: 0.3 }}
            className="w-12 h-12 rounded-full bg-purple-600/30 flex items-center justify-center"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
                delay: step.delay,
              }}
            >
              <step.icon className="w-6 h-6 text-purple-400" />
            </motion.div>
          </motion.div>
        ))}
      </div>

      {/* 进度条 */}
      <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden mb-4">
        <motion.div
          className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
          initial={{ width: '0%' }}
          animate={{ width: '100%' }}
          transition={{ duration: 3, repeat: Infinity }}
        />
      </div>

      {/* 消息 */}
      <p className="text-gray-400">{message}</p>

      {/* 步骤说明 */}
      <div className="mt-6 space-y-2">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: step.delay + 0.5 }}
            className="text-sm text-gray-500 flex items-center justify-center gap-2"
          >
            <step.icon className="w-4 h-4" />
            <span>{step.label}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}