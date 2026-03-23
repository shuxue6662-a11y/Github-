"""
Commit 数据分析器
"""
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict

from app.models.schemas import CommitData, CommitAnalysis, ContributorStats


class CommitAnalyzer:
    """分析 commit 数据，提取音乐生成所需特征"""
    
    def analyze(self, commits: List[CommitData]) -> CommitAnalysis:
        """
        分析 commit 列表，生成综合分析结果
        """
        if not commits:
            raise ValueError("No commits to analyze")
        
        # 基础统计
        total = len(commits)
        
        # 时间范围
        timestamps = [c.timestamp for c in commits]
        min_time = min(timestamps)
        max_time = max(timestamps)
        date_range = max(1, (max_time - min_time).days)
        
        # 每日平均
        avg_per_day = total / date_range
        
        # 修改统计
        total_additions = sum(c.additions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        
        # 贡献者统计
        top_contributors = self._analyze_contributors(commits)
        
        # Commit 类型分布
        type_counts = Counter(c.commit_type.value for c in commits)
        
        # 文件类型分布
        file_type_counts: Dict[str, int] = defaultdict(int)
        for c in commits:
            for ft in c.file_types:
                file_type_counts[ft] += 1
        
        # 活跃时间分布（24小时）
        hour_counts = [0] * 24
        for c in commits:
            hour_counts[c.timestamp.hour] += 1
        
        # 活跃星期分布（0=周一，6=周日）
        weekday_counts = [0] * 7
        for c in commits:
            weekday_counts[c.timestamp.weekday()] += 1
        
        # 活跃度级别
        activity_level = self._determine_activity_level(avg_per_day)
        
        # 主导类型
        dominant_type = type_counts.most_common(1)[0][0] if type_counts else "other"
        
        return CommitAnalysis(
            total_commits=total,
            date_range_days=date_range,
            avg_commits_per_day=round(avg_per_day, 2),
            total_additions=total_additions,
            total_deletions=total_deletions,
            top_contributors=top_contributors,
            commit_type_distribution=dict(type_counts),
            file_type_distribution=dict(file_type_counts),
            activity_hours=hour_counts,
            activity_weekdays=weekday_counts,
            commits=commits,
            activity_level=activity_level,
            dominant_type=dominant_type,
        )
    
    def _analyze_contributors(
        self, 
        commits: List[CommitData],
        top_n: int = 10,
    ) -> List[ContributorStats]:
        """分析贡献者统计"""
        contributors: Dict[str, Dict] = defaultdict(lambda: {
            "email": "",
            "commits": 0,
            "additions": 0,
            "deletions": 0,
        })
        
        for c in commits:
            key = c.author
            contributors[key]["email"] = c.author_email
            contributors[key]["commits"] += 1
            contributors[key]["additions"] += c.additions
            contributors[key]["deletions"] += c.deletions
        
        total_commits = len(commits)
        
        result = []
        for name, stats in sorted(
            contributors.items(),
            key=lambda x: x[1]["commits"],
            reverse=True,
        )[:top_n]:
            result.append(ContributorStats(
                name=name,
                email=stats["email"],
                commits=stats["commits"],
                additions=stats["additions"],
                deletions=stats["deletions"],
                percentage=round(stats["commits"] / total_commits * 100, 1),
            ))
        
        return result
    
    def _determine_activity_level(self, avg_per_day: float) -> str:
        """确定活跃度级别"""
        if avg_per_day < 0.5:
            return "low"
        elif avg_per_day < 2:
            return "moderate"
        elif avg_per_day < 5:
            return "high"
        else:
            return "intense"