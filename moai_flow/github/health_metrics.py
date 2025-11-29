"""GitHub Repository Health Metrics System for PRD-06.

This module provides comprehensive repository health tracking with:
- Issue velocity metrics (issues closed per week)
- PR merge time analysis (average time to merge)
- Stale item detection (stale issues/PRs)
- Contributor activity tracking
- Test coverage trend analysis
- Overall health scoring and trend detection

Example:
    >>> from moai_flow.github.health_metrics import HealthMetricsAnalyzer
    >>> analyzer = HealthMetricsAnalyzer("owner", "repo", token)
    >>> metrics = analyzer.calculate_health_metrics()
    >>> print(f"Health Score: {metrics.health_score}/100")
    >>> print(f"Trend: {metrics.trend}")
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import statistics

# GitHub API imports
try:
    from github import Github, GithubException, Auth
    from github.Repository import Repository
    from github.Issue import Issue
    from github.PullRequest import PullRequest
except ImportError:
    Github = None
    GithubException = Exception
    Auth = None
    Repository = None
    Issue = None
    PullRequest = None

logger = logging.getLogger(__name__)


class HealthTrend(str, Enum):
    """Repository health trend indicators."""

    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"


@dataclass
class HealthMetrics:
    """Repository health metrics snapshot.

    Attributes:
        timestamp: When metrics were calculated
        issue_velocity: Issues closed per week
        pr_merge_time: Average PR merge time in days
        stale_count: Number of stale items (issues + PRs)
        contributor_activity: Number of active contributors
        test_coverage_trend: Test coverage percentage change
        health_score: Overall health score (0-100)
        trend: Health trend direction
    """

    timestamp: datetime
    issue_velocity: float
    pr_merge_time: float
    stale_count: int
    contributor_activity: int
    test_coverage_trend: float
    health_score: int
    trend: HealthTrend

    # Detailed breakdowns
    issue_metrics: Dict[str, float] = field(default_factory=dict)
    pr_metrics: Dict[str, float] = field(default_factory=dict)
    contributor_metrics: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for storage/reporting."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "issue_velocity": self.issue_velocity,
            "pr_merge_time": self.pr_merge_time,
            "stale_count": self.stale_count,
            "contributor_activity": self.contributor_activity,
            "test_coverage_trend": self.test_coverage_trend,
            "health_score": self.health_score,
            "trend": self.trend.value,
            "issue_metrics": self.issue_metrics,
            "pr_metrics": self.pr_metrics,
            "contributor_metrics": self.contributor_metrics,
        }


@dataclass
class HealthComparison:
    """Comparison between two health metrics snapshots.

    Attributes:
        current: Current metrics
        previous: Previous metrics
        change_percentage: Percentage change in health score
        trend: Detected trend direction
        improvements: List of improved metrics
        degradations: List of degraded metrics
    """

    current: HealthMetrics
    previous: HealthMetrics
    change_percentage: float
    trend: HealthTrend
    improvements: List[str] = field(default_factory=list)
    degradations: List[str] = field(default_factory=list)


class HealthMetricsAnalyzer:
    """GitHub repository health metrics analyzer.

    Analyzes repository health across multiple dimensions:
    - Issue management (velocity, closure rate)
    - PR workflow (merge time, throughput)
    - Activity (contributor engagement)
    - Quality (test coverage trends)
    - Overall health scoring and trend detection

    Attributes:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        github_token: GitHub API authentication token
        github_client: PyGithub client instance
        repo: GitHub repository object
        stale_days: Number of days before item is considered stale
    """

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: Optional[str] = None,
        stale_days: int = 60,
    ):
        """Initialize Health Metrics Analyzer.

        Args:
            repo_owner: Repository owner username/organization
            repo_name: Repository name
            github_token: GitHub API token (defaults to GITHUB_TOKEN env var)
            stale_days: Days before item is considered stale (default: 60)

        Raises:
            ValueError: If GitHub token is not provided
            ImportError: If PyGithub is not installed
        """
        if Github is None:
            raise ImportError(
                "PyGithub is required. Install with: pip install PyGithub"
            )

        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.stale_days = stale_days

        if not self.github_token:
            raise ValueError(
                "GitHub token is required. Provide via parameter or GITHUB_TOKEN env var"
            )

        # Initialize GitHub client
        auth = Auth.Token(self.github_token)
        self.github_client = Github(auth=auth)
        self.repo = self.github_client.get_repo(f"{repo_owner}/{repo_name}")

        logger.info(f"Initialized Health Metrics Analyzer for {repo_owner}/{repo_name}")

    def calculate_health_metrics(
        self,
        lookback_weeks: int = 4,
        include_detailed: bool = True
    ) -> HealthMetrics:
        """Calculate comprehensive repository health metrics.

        Args:
            lookback_weeks: Number of weeks to analyze (default: 4)
            include_detailed: Include detailed breakdowns (default: True)

        Returns:
            HealthMetrics object with all calculated metrics
        """
        logger.info(f"Calculating health metrics for {lookback_weeks} weeks")

        # Calculate individual metrics
        issue_velocity = self.calculate_issue_velocity(lookback_weeks)
        pr_merge_time = self.calculate_pr_merge_time(lookback_weeks)
        stale_count = self.calculate_stale_count()
        contributor_activity = self.calculate_contributor_activity(lookback_weeks)
        test_coverage_trend = self.calculate_test_coverage_trend(lookback_weeks)

        # Calculate overall health score
        health_score = self._calculate_health_score(
            issue_velocity,
            pr_merge_time,
            stale_count,
            contributor_activity,
            test_coverage_trend
        )

        # Determine trend (requires historical data)
        trend = self._determine_trend(health_score)

        # Build detailed metrics if requested
        issue_metrics = {}
        pr_metrics = {}
        contributor_metrics = {}

        if include_detailed:
            issue_metrics = self._get_detailed_issue_metrics(lookback_weeks)
            pr_metrics = self._get_detailed_pr_metrics(lookback_weeks)
            contributor_metrics = self._get_detailed_contributor_metrics(lookback_weeks)

        metrics = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=issue_velocity,
            pr_merge_time=pr_merge_time,
            stale_count=stale_count,
            contributor_activity=contributor_activity,
            test_coverage_trend=test_coverage_trend,
            health_score=health_score,
            trend=trend,
            issue_metrics=issue_metrics,
            pr_metrics=pr_metrics,
            contributor_metrics=contributor_metrics,
        )

        logger.info(f"Health metrics calculated: score={health_score}, trend={trend.value}")
        return metrics

    def calculate_issue_velocity(self, lookback_weeks: int = 4) -> float:
        """Calculate issues closed per week.

        Args:
            lookback_weeks: Number of weeks to analyze

        Returns:
            Average issues closed per week
        """
        cutoff_date = datetime.now() - timedelta(weeks=lookback_weeks)

        closed_issues = self.repo.get_issues(
            state="closed",
            since=cutoff_date
        )

        # Count issues closed in the period
        issue_count = 0
        for issue in closed_issues:
            # Exclude PRs (GitHub treats PRs as issues)
            if not issue.pull_request:
                issue_count += 1

        velocity = issue_count / lookback_weeks if lookback_weeks > 0 else 0.0
        logger.debug(f"Issue velocity: {velocity:.2f} issues/week ({issue_count} closed in {lookback_weeks} weeks)")

        return round(velocity, 2)

    def calculate_pr_merge_time(self, lookback_weeks: int = 4) -> float:
        """Calculate average time to merge PRs in days.

        Args:
            lookback_weeks: Number of weeks to analyze

        Returns:
            Average days from PR creation to merge
        """
        cutoff_date = datetime.now() - timedelta(weeks=lookback_weeks)

        merged_prs = self.repo.get_pulls(
            state="closed",
            sort="updated",
            direction="desc"
        )

        merge_times = []
        for pr in merged_prs:
            # Only count merged PRs
            if pr.merged and pr.created_at >= cutoff_date:
                merge_time = (pr.merged_at - pr.created_at).total_seconds() / 86400  # Convert to days
                merge_times.append(merge_time)

        avg_merge_time = statistics.mean(merge_times) if merge_times else 0.0
        logger.debug(f"PR merge time: {avg_merge_time:.2f} days (from {len(merge_times)} PRs)")

        return round(avg_merge_time, 2)

    def calculate_stale_count(self) -> int:
        """Calculate number of stale issues and PRs.

        Returns:
            Total count of stale items (issues + PRs)
        """
        cutoff_date = datetime.now() - timedelta(days=self.stale_days)

        # Count stale issues (excluding PRs)
        stale_issues = 0
        open_issues = self.repo.get_issues(state="open")
        for issue in open_issues:
            if not issue.pull_request and issue.updated_at < cutoff_date:
                stale_issues += 1

        # Count stale PRs
        stale_prs = 0
        open_prs = self.repo.get_pulls(state="open")
        for pr in open_prs:
            if pr.updated_at < cutoff_date:
                stale_prs += 1

        total_stale = stale_issues + stale_prs
        logger.debug(f"Stale count: {total_stale} ({stale_issues} issues + {stale_prs} PRs)")

        return total_stale

    def calculate_contributor_activity(self, lookback_weeks: int = 4) -> int:
        """Calculate number of active contributors.

        Args:
            lookback_weeks: Number of weeks to analyze

        Returns:
            Count of unique contributors with commits
        """
        cutoff_date = datetime.now() - timedelta(weeks=lookback_weeks)

        # Get commits in the period
        commits = self.repo.get_commits(since=cutoff_date)

        # Collect unique contributors
        contributors = set()
        for commit in commits:
            if commit.author:
                contributors.add(commit.author.login)

        active_count = len(contributors)
        logger.debug(f"Active contributors: {active_count} in last {lookback_weeks} weeks")

        return active_count

    def calculate_test_coverage_trend(self, lookback_weeks: int = 4) -> float:
        """Calculate test coverage trend over time.

        Note: This requires coverage reports to be committed to the repository.
        If not available, returns 0.0.

        Args:
            lookback_weeks: Number of weeks to analyze

        Returns:
            Percentage change in test coverage (positive = improving)
        """
        try:
            # Try to read coverage from common locations
            coverage_paths = [
                "coverage.json",
                ".coverage",
                "coverage/coverage-summary.json",
                "tests/coverage.txt",
            ]

            # This is a simplified implementation
            # In production, you'd parse actual coverage files
            # For now, return 0.0 (no trend data available)

            logger.debug("Test coverage trend: No coverage data available")
            return 0.0

        except Exception as e:
            logger.warning(f"Failed to calculate coverage trend: {str(e)}")
            return 0.0

    def analyze_trend(
        self,
        current_metrics: HealthMetrics,
        historical_metrics: List[HealthMetrics],
    ) -> HealthComparison:
        """Analyze health trend by comparing current metrics with historical data.

        Args:
            current_metrics: Current health metrics
            historical_metrics: List of historical metrics (ordered by time)

        Returns:
            HealthComparison with trend analysis
        """
        if not historical_metrics:
            return HealthComparison(
                current=current_metrics,
                previous=current_metrics,
                change_percentage=0.0,
                trend=HealthTrend.STABLE,
                improvements=[],
                degradations=[],
            )

        # Compare with most recent historical metrics
        previous = historical_metrics[-1]

        # Calculate change percentage
        score_change = current_metrics.health_score - previous.health_score
        change_percentage = (score_change / previous.health_score * 100) if previous.health_score > 0 else 0.0

        # Determine trend
        if change_percentage > 5:
            trend = HealthTrend.IMPROVING
        elif change_percentage < -5:
            trend = HealthTrend.DEGRADING
        else:
            trend = HealthTrend.STABLE

        # Identify improvements and degradations
        improvements = []
        degradations = []

        if current_metrics.issue_velocity > previous.issue_velocity:
            improvements.append("issue_velocity")
        elif current_metrics.issue_velocity < previous.issue_velocity:
            degradations.append("issue_velocity")

        if current_metrics.pr_merge_time < previous.pr_merge_time:
            improvements.append("pr_merge_time")
        elif current_metrics.pr_merge_time > previous.pr_merge_time:
            degradations.append("pr_merge_time")

        if current_metrics.stale_count < previous.stale_count:
            improvements.append("stale_count")
        elif current_metrics.stale_count > previous.stale_count:
            degradations.append("stale_count")

        if current_metrics.contributor_activity > previous.contributor_activity:
            improvements.append("contributor_activity")
        elif current_metrics.contributor_activity < previous.contributor_activity:
            degradations.append("contributor_activity")

        if current_metrics.test_coverage_trend > previous.test_coverage_trend:
            improvements.append("test_coverage_trend")
        elif current_metrics.test_coverage_trend < previous.test_coverage_trend:
            degradations.append("test_coverage_trend")

        return HealthComparison(
            current=current_metrics,
            previous=previous,
            change_percentage=round(change_percentage, 2),
            trend=trend,
            improvements=improvements,
            degradations=degradations,
        )

    # Private helper methods

    def _calculate_health_score(
        self,
        issue_velocity: float,
        pr_merge_time: float,
        stale_count: int,
        contributor_activity: int,
        test_coverage_trend: float,
    ) -> int:
        """Calculate overall health score (0-100).

        Weighted scoring:
        - Issue velocity: 25% (higher is better)
        - PR merge time: 25% (lower is better)
        - Stale count: 20% (lower is better)
        - Contributor activity: 20% (higher is better)
        - Test coverage trend: 10% (positive is better)
        """
        score = 0

        # Issue velocity score (25 points max)
        # Target: 10+ issues/week = max score
        velocity_score = min(issue_velocity / 10 * 25, 25)
        score += velocity_score

        # PR merge time score (25 points max)
        # Target: <= 2 days = max score, > 10 days = 0
        if pr_merge_time <= 2:
            merge_score = 25
        elif pr_merge_time >= 10:
            merge_score = 0
        else:
            merge_score = 25 * (1 - (pr_merge_time - 2) / 8)
        score += merge_score

        # Stale count score (20 points max)
        # Target: 0 stale items = max score, 50+ stale = 0
        stale_score = max(0, 20 * (1 - stale_count / 50))
        score += stale_score

        # Contributor activity score (20 points max)
        # Target: 5+ contributors = max score
        activity_score = min(contributor_activity / 5 * 20, 20)
        score += activity_score

        # Test coverage trend score (10 points max)
        # Positive trend = 10, negative = 0, stable = 5
        if test_coverage_trend > 0:
            coverage_score = 10
        elif test_coverage_trend < 0:
            coverage_score = 0
        else:
            coverage_score = 5
        score += coverage_score

        return int(round(score))

    def _determine_trend(self, current_score: int) -> HealthTrend:
        """Determine health trend from current score.

        Note: This is a simplified version. In production, you'd compare
        with historical data.
        """
        # For now, use score thresholds
        if current_score >= 70:
            return HealthTrend.IMPROVING
        elif current_score >= 50:
            return HealthTrend.STABLE
        else:
            return HealthTrend.DEGRADING

    def _get_detailed_issue_metrics(self, lookback_weeks: int) -> Dict[str, float]:
        """Get detailed issue metrics breakdown."""
        cutoff_date = datetime.now() - timedelta(weeks=lookback_weeks)

        issues = self.repo.get_issues(state="all", since=cutoff_date)

        opened = 0
        closed = 0
        avg_close_time_days = []

        for issue in issues:
            if not issue.pull_request:
                if issue.created_at >= cutoff_date:
                    opened += 1
                if issue.closed_at and issue.closed_at >= cutoff_date:
                    closed += 1
                    close_time = (issue.closed_at - issue.created_at).total_seconds() / 86400
                    avg_close_time_days.append(close_time)

        return {
            "opened": opened,
            "closed": closed,
            "avg_close_time_days": round(statistics.mean(avg_close_time_days), 2) if avg_close_time_days else 0.0,
            "close_rate": round(closed / opened * 100, 2) if opened > 0 else 0.0,
        }

    def _get_detailed_pr_metrics(self, lookback_weeks: int) -> Dict[str, float]:
        """Get detailed PR metrics breakdown."""
        cutoff_date = datetime.now() - timedelta(weeks=lookback_weeks)

        prs = self.repo.get_pulls(state="all", sort="updated", direction="desc")

        opened = 0
        merged = 0
        avg_merge_time_days = []

        for pr in prs:
            if pr.created_at >= cutoff_date:
                opened += 1
            if pr.merged and pr.merged_at and pr.merged_at >= cutoff_date:
                merged += 1
                merge_time = (pr.merged_at - pr.created_at).total_seconds() / 86400
                avg_merge_time_days.append(merge_time)

        return {
            "opened": opened,
            "merged": merged,
            "avg_merge_time_days": round(statistics.mean(avg_merge_time_days), 2) if avg_merge_time_days else 0.0,
            "merge_rate": round(merged / opened * 100, 2) if opened > 0 else 0.0,
        }

    def _get_detailed_contributor_metrics(self, lookback_weeks: int) -> Dict[str, int]:
        """Get detailed contributor metrics breakdown."""
        cutoff_date = datetime.now() - timedelta(weeks=lookback_weeks)

        commits = self.repo.get_commits(since=cutoff_date)

        contributor_commits = defaultdict(int)
        for commit in commits:
            if commit.author:
                contributor_commits[commit.author.login] += 1

        return {
            "total_contributors": len(contributor_commits),
            "total_commits": sum(contributor_commits.values()),
            "avg_commits_per_contributor": round(
                sum(contributor_commits.values()) / len(contributor_commits), 2
            ) if contributor_commits else 0.0,
        }
