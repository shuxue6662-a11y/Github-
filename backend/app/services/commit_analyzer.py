"""
Commit 数据分析器
"""
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from app.models.schemas import CommitData, CommitAnalysis


class CommitAnalyzer:
    """分析 commit 数据，提取音乐生成所需特征"""
    
    def analyze(self, commits: list[CommitData]) -> CommitAnalysis:
        """
        分析 commit 列表
        """
        if not commits:
            raise ValueError("No commits to analyze")
        
        # 基础统计
        total = len(commits)
        
        # 时间范围
        timestamps = [c.timestamp for c in commits]
        date_range = (max(timestamps) - min(timestamps)).days or 1
        
        # 每日平均
        avg_per_day = total / date_range
        
        # Top 贡献者
        author_counts = Counter(c.author for c in commits)
        top_contributors = [
            {"name": name, "commits": count}
            for name, count in author_counts.most_common(5)
        ]
        
        # Commit 类型分布
        type_counts = Counter(c.commit_type.value for c in commits)
        
        # 活跃时间分布（24小时）
        hour_counts = [0] * 24
        for c in commits:
            hour_counts[c.timestamp.hour] += 1
        
        return CommitAnalysis(
            total_commits=total,
            date_range_days=date_range,
            avg_commits_per_day=round(avg_per_day, 2),
            top_contributors=top_contributors,
            commit_type_distribution=dict(type_counts),
            activity_hours=hour_counts,
            commits=commits,
        )