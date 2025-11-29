"""GitHub Repository Health Agent for automated repo health monitoring.

This module provides comprehensive repository health monitoring, stale item management,
actionable recommendations, and health trend analysis for GitHub repositories.

Example:
    >>> agent = GitHubRepoAgent("owner", "repo", token)
    >>> health_score = agent.calculate_health_score()
    >>> print(f"Repository Health: {health_score}/100")
    >>>
    >>> # Get stale issues and PRs
    >>> stale_issues = agent.get_stale_issues(days=30)
    >>> stale_prs = agent.get_stale_prs(days=30)
    >>>
    >>> # Auto-cleanup with warnings
    >>> cleanup_report = agent.cleanup_stale_items(
    ...     warning_days=30,
    ...     close_days=60,
    ...     auto_close_days=90,
    ...     dry_run=False
    >>> )
    >>>
    >>> # Get actionable recommendations
    >>> recommendations = agent.get_actionable_recommendations()
    >>> for rec in recommendations:
    ...     print(f"{rec['priority']}: {rec['action']}")
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# GitHub API imports
try:
    from github import Github, GithubException, Auth
    from github.Issue import Issue
    from github.PullRequest import PullRequest
    from github.Repository import Repository
except ImportError:
    Github = None
    GithubException = Exception
    Auth = None
    Issue = None
    PullRequest = None
    Repository = None

logger = logging.getLogger(__name__)


class HealthCategory(Enum):
    """Health score category levels."""

    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"            # 75-89
    FAIR = "fair"            # 60-74
    POOR = "poor"            # 40-59
    CRITICAL = "critical"    # 0-39


class RecommendationPriority(Enum):
    """Priority levels for actionable recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class StaleItem:
    """Represents a stale issue or PR.

    Attributes:
        number: Issue/PR number
        title: Issue/PR title
        url: Issue/PR URL
        state: Current state (open/closed)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        days_stale: Days since last update
        labels: List of labels
        assignees: List of assignees
        type: Item type (issue or pull_request)
    """

    number: int
    title: str
    url: str
    state: str
    created_at: datetime
    updated_at: datetime
    days_stale: int
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    type: str = "issue"  # "issue" or "pull_request"


@dataclass
class HealthMetrics:
    """Repository health metrics.

    Attributes:
        total_score: Overall health score (0-100)
        issue_velocity_score: Issue velocity score (0-20)
        pr_merge_time_score: PR merge time score (0-20)
        stale_item_score: Stale item count score (0-20)
        test_coverage_score: Test coverage score (0-20)
        contributor_activity_score: Contributor activity score (0-20)
        category: Health category
        metrics: Raw metrics used for calculation
    """

    total_score: float
    issue_velocity_score: float
    pr_merge_time_score: float
    stale_item_score: float
    test_coverage_score: float
    contributor_activity_score: float
    category: HealthCategory
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Recommendation:
    """Actionable recommendation for repository improvement.

    Attributes:
        priority: Recommendation priority
        category: Recommendation category
        action: Recommended action to take
        impact: Expected impact description
        metrics: Related metrics
        details: Additional details
    """

    priority: RecommendationPriority
    category: str
    action: str
    impact: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    details: Optional[str] = None


class GitHubRepoAgent:
    """GitHub Repository Health automation agent.

    Monitors repository health, manages stale items, provides actionable
    recommendations, and tracks health trends over time.

    Attributes:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        github_token: GitHub API authentication token
        github_client: PyGithub client instance
        repo: GitHub repository object
    """

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: Optional[str] = None,
    ):
        """Initialize GitHub Repo Health Agent.

        Args:
            repo_owner: Repository owner username/organization
            repo_name: Repository name
            github_token: GitHub API token (defaults to GITHUB_TOKEN env var)

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

        if not self.github_token:
            raise ValueError(
                "GitHub token is required. Provide via parameter or GITHUB_TOKEN env var"
            )

        # Initialize GitHub client
        auth = Auth.Token(self.github_token)
        self.github_client = Github(auth=auth)
        self.repo = self.github_client.get_repo(f"{repo_owner}/{repo_name}")

        logger.info(f"Initialized GitHub Repo Agent for {repo_owner}/{repo_name}")

    def monitor_health(self) -> HealthMetrics:
        """Monitor overall repository health.

        Calculates comprehensive health score based on:
        - Issue velocity (20 points)
        - PR merge time (20 points)
        - Stale item count (20 points)
        - Test coverage (20 points)
        - Contributor activity (20 points)

        Returns:
            HealthMetrics object with scores and category

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> health = agent.monitor_health()
            >>> print(f"Health: {health.total_score}/100 ({health.category.value})")
        """
        logger.info("Calculating repository health metrics...")

        # Calculate individual scores
        issue_velocity = self._calculate_issue_velocity_score()
        pr_merge_time = self._calculate_pr_merge_time_score()
        stale_items = self._calculate_stale_item_score()
        test_coverage = self._calculate_test_coverage_score()
        contributor_activity = self._calculate_contributor_activity_score()

        # Calculate total score
        total_score = (
            issue_velocity +
            pr_merge_time +
            stale_items +
            test_coverage +
            contributor_activity
        )

        # Determine category
        category = self._determine_health_category(total_score)

        metrics = HealthMetrics(
            total_score=round(total_score, 2),
            issue_velocity_score=round(issue_velocity, 2),
            pr_merge_time_score=round(pr_merge_time, 2),
            stale_item_score=round(stale_items, 2),
            test_coverage_score=round(test_coverage, 2),
            contributor_activity_score=round(contributor_activity, 2),
            category=category,
            metrics={
                "timestamp": datetime.now().isoformat(),
                "repo": f"{self.repo_owner}/{self.repo_name}"
            }
        )

        logger.info(f"Health score calculated: {total_score}/100 ({category.value})")
        return metrics

    def get_stale_issues(
        self,
        days: int = 30,
        labels: Optional[List[str]] = None,
        exclude_labels: Optional[List[str]] = None
    ) -> List[StaleItem]:
        """Find stale issues based on inactivity threshold.

        Args:
            days: Number of days of inactivity to consider stale
            labels: Optional list of labels to filter by
            exclude_labels: Optional list of labels to exclude

        Returns:
            List of StaleItem objects for stale issues

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> stale = agent.get_stale_issues(days=60)
            >>> for item in stale:
            ...     print(f"#{item.number}: {item.title} ({item.days_stale} days)")
        """
        logger.info(f"Finding issues stale for {days}+ days...")

        stale_items = []
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get open issues
        issues = self.repo.get_issues(state="open")

        for issue in issues:
            # Skip pull requests (they are also returned by get_issues)
            if issue.pull_request:
                continue

            # Check if issue is stale
            if issue.updated_at < cutoff_date:
                # Apply label filters
                issue_labels = [label.name for label in issue.labels]

                if labels and not any(label in issue_labels for label in labels):
                    continue

                if exclude_labels and any(label in issue_labels for label in exclude_labels):
                    continue

                # Calculate days stale
                days_stale = (datetime.now() - issue.updated_at).days

                stale_item = StaleItem(
                    number=issue.number,
                    title=issue.title,
                    url=issue.html_url,
                    state=issue.state,
                    created_at=issue.created_at,
                    updated_at=issue.updated_at,
                    days_stale=days_stale,
                    labels=issue_labels,
                    assignees=[assignee.login for assignee in issue.assignees],
                    type="issue"
                )
                stale_items.append(stale_item)

        logger.info(f"Found {len(stale_items)} stale issues")
        return sorted(stale_items, key=lambda x: x.days_stale, reverse=True)

    def get_stale_prs(
        self,
        days: int = 30,
        labels: Optional[List[str]] = None,
        exclude_labels: Optional[List[str]] = None
    ) -> List[StaleItem]:
        """Find stale pull requests based on inactivity threshold.

        Args:
            days: Number of days of inactivity to consider stale
            labels: Optional list of labels to filter by
            exclude_labels: Optional list of labels to exclude

        Returns:
            List of StaleItem objects for stale PRs

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> stale = agent.get_stale_prs(days=14)
            >>> for item in stale:
            ...     print(f"PR #{item.number}: {item.title} ({item.days_stale} days)")
        """
        logger.info(f"Finding PRs stale for {days}+ days...")

        stale_items = []
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get open pull requests
        pulls = self.repo.get_pulls(state="open")

        for pr in pulls:
            # Check if PR is stale
            if pr.updated_at < cutoff_date:
                # Apply label filters
                pr_labels = [label.name for label in pr.labels]

                if labels and not any(label in pr_labels for label in labels):
                    continue

                if exclude_labels and any(label in pr_labels for label in exclude_labels):
                    continue

                # Calculate days stale
                days_stale = (datetime.now() - pr.updated_at).days

                stale_item = StaleItem(
                    number=pr.number,
                    title=pr.title,
                    url=pr.html_url,
                    state=pr.state,
                    created_at=pr.created_at,
                    updated_at=pr.updated_at,
                    days_stale=days_stale,
                    labels=pr_labels,
                    assignees=[assignee.login for assignee in pr.assignees],
                    type="pull_request"
                )
                stale_items.append(stale_item)

        logger.info(f"Found {len(stale_items)} stale PRs")
        return sorted(stale_items, key=lambda x: x.days_stale, reverse=True)

    def auto_close_stale(
        self,
        item: StaleItem,
        reason: str = "Automatically closed due to inactivity",
        label: str = "stale"
    ) -> bool:
        """Close a stale issue or PR with a comment.

        Args:
            item: StaleItem to close
            reason: Reason for closing
            label: Label to add before closing

        Returns:
            True if successfully closed, False otherwise

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> stale_issues = agent.get_stale_issues(days=90)
            >>> for item in stale_issues:
            ...     agent.auto_close_stale(item, reason="90 days of inactivity")
        """
        try:
            if item.type == "issue":
                issue = self.repo.get_issue(item.number)

                # Add stale label
                if label and label not in item.labels:
                    issue.add_to_labels(label)

                # Add closing comment
                close_message = f"""
This issue has been automatically closed due to inactivity.

**Reason:** {reason}
**Last activity:** {item.updated_at.strftime('%Y-%m-%d')} ({item.days_stale} days ago)

If this issue is still relevant, please reopen it with updated information.
                """.strip()

                issue.create_comment(close_message)
                issue.edit(state="closed")

                logger.info(f"Closed stale issue #{item.number}")
                return True

            elif item.type == "pull_request":
                pr = self.repo.get_pull(item.number)

                # Add stale label
                if label and label not in item.labels:
                    pr.add_to_labels(label)

                # Add closing comment
                close_message = f"""
This pull request has been automatically closed due to inactivity.

**Reason:** {reason}
**Last activity:** {item.updated_at.strftime('%Y-%m-%d')} ({item.days_stale} days ago)

If this PR is still relevant, please reopen it and update it to resolve any conflicts.
                """.strip()

                pr.create_issue_comment(close_message)
                pr.edit(state="closed")

                logger.info(f"Closed stale PR #{item.number}")
                return True

            return False

        except GithubException as e:
            logger.error(f"Failed to close {item.type} #{item.number}: {e}")
            return False

    def calculate_health_score(self) -> float:
        """Calculate overall repository health score (0-100).

        Convenience method that returns just the numeric score.

        Returns:
            Health score from 0 to 100

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> score = agent.calculate_health_score()
            >>> print(f"Repository health: {score}/100")
        """
        metrics = self.monitor_health()
        return metrics.total_score

    def get_actionable_recommendations(self) -> List[Recommendation]:
        """Get prioritized list of actionable recommendations.

        Analyzes current repository state and provides specific actions
        to improve health score.

        Returns:
            List of Recommendation objects sorted by priority

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> recommendations = agent.get_actionable_recommendations()
            >>> for rec in recommendations:
            ...     print(f"[{rec.priority.value}] {rec.action}")
            ...     print(f"  Impact: {rec.impact}")
        """
        logger.info("Generating actionable recommendations...")

        recommendations = []

        # Get current health metrics
        health = self.monitor_health()

        # Stale items recommendations
        stale_issues = self.get_stale_issues(days=30)
        stale_prs = self.get_stale_prs(days=30)

        if len(stale_issues) > 20:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                category="stale_management",
                action=f"Address {len(stale_issues)} stale issues (30+ days inactive)",
                impact="Improve issue velocity score and reduce clutter",
                metrics={"stale_issue_count": len(stale_issues)},
                details="Consider triaging, closing, or updating these issues"
            ))
        elif len(stale_issues) > 10:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.MEDIUM,
                category="stale_management",
                action=f"Review {len(stale_issues)} stale issues",
                impact="Maintain healthy issue queue",
                metrics={"stale_issue_count": len(stale_issues)}
            ))

        if len(stale_prs) > 10:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.CRITICAL,
                category="stale_management",
                action=f"Address {len(stale_prs)} stale pull requests (30+ days inactive)",
                impact="Improve PR merge time and contributor satisfaction",
                metrics={"stale_pr_count": len(stale_prs)},
                details="Stale PRs block contributors and hurt project momentum"
            ))
        elif len(stale_prs) > 5:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                category="stale_management",
                action=f"Review {len(stale_prs)} stale pull requests",
                impact="Maintain healthy PR workflow",
                metrics={"stale_pr_count": len(stale_prs)}
            ))

        # Issue velocity recommendations
        if health.issue_velocity_score < 10:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                category="issue_velocity",
                action="Improve issue resolution rate",
                impact="Increase health score by up to 10 points",
                metrics={"current_score": health.issue_velocity_score},
                details="Target: Close 80%+ of new issues within 30 days"
            ))

        # PR merge time recommendations
        if health.pr_merge_time_score < 10:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                category="pr_merge_time",
                action="Reduce pull request merge time",
                impact="Increase health score by up to 10 points",
                metrics={"current_score": health.pr_merge_time_score},
                details="Target: Merge PRs within 7 days on average"
            ))

        # Test coverage recommendations
        if health.test_coverage_score < 15:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.MEDIUM,
                category="test_coverage",
                action="Improve test coverage",
                impact="Increase health score and code quality",
                metrics={"current_score": health.test_coverage_score},
                details="Target: 80%+ test coverage across the project"
            ))

        # Contributor activity recommendations
        if health.contributor_activity_score < 10:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.MEDIUM,
                category="contributor_activity",
                action="Increase contributor engagement",
                impact="Improve project sustainability",
                metrics={"current_score": health.contributor_activity_score},
                details="Consider good-first-issue labels, documentation improvements"
            ))

        # Sort by priority
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3
        }

        recommendations.sort(key=lambda x: priority_order[x.priority])

        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def cleanup_stale_items(
        self,
        warning_days: int = 30,
        close_days: int = 60,
        auto_close_days: int = 90,
        dry_run: bool = True,
        exclude_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Batch cleanup of stale items with progressive warnings.

        Three-tier stale detection system:
        - warning_days: Add warning label
        - close_days: Add close warning comment
        - auto_close_days: Auto-close with comment

        Args:
            warning_days: Days before adding warning label (default: 30)
            close_days: Days before close warning comment (default: 60)
            auto_close_days: Days before auto-closing (default: 90)
            dry_run: If True, only report what would be done
            exclude_labels: Labels to exclude from cleanup

        Returns:
            Dictionary with cleanup statistics

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> # Dry run first
            >>> report = agent.cleanup_stale_items(dry_run=True)
            >>> print(f"Would close {report['would_close']} items")
            >>>
            >>> # Execute cleanup
            >>> report = agent.cleanup_stale_items(dry_run=False)
            >>> print(f"Closed {report['closed']} items")
        """
        logger.info(f"Starting stale item cleanup (dry_run={dry_run})...")

        exclude_labels = exclude_labels or []

        stats = {
            "warning_added": [],
            "close_warning_added": [],
            "closed": [],
            "would_close": [],
            "errors": []
        }

        # Process stale issues
        for days, action in [
            (auto_close_days, "close"),
            (close_days, "warn_close"),
            (warning_days, "warn")
        ]:
            stale_issues = self.get_stale_issues(
                days=days,
                exclude_labels=exclude_labels
            )
            stale_prs = self.get_stale_prs(
                days=days,
                exclude_labels=exclude_labels
            )

            for item in stale_issues + stale_prs:
                try:
                    if action == "close":
                        if dry_run:
                            stats["would_close"].append(item.number)
                        else:
                            success = self.auto_close_stale(
                                item,
                                reason=f"{auto_close_days} days of inactivity"
                            )
                            if success:
                                stats["closed"].append(item.number)

                    elif action == "warn_close":
                        if "stale" not in item.labels and not dry_run:
                            # Add close warning comment
                            self._add_close_warning(item, close_days)
                            stats["close_warning_added"].append(item.number)

                    elif action == "warn":
                        if "stale" not in item.labels and not dry_run:
                            # Add warning label
                            self._add_warning_label(item)
                            stats["warning_added"].append(item.number)

                except Exception as e:
                    logger.error(f"Error processing {item.type} #{item.number}: {e}")
                    stats["errors"].append({
                        "number": item.number,
                        "type": item.type,
                        "error": str(e)
                    })

        # Generate summary
        stats["summary"] = {
            "warning_labels": len(stats["warning_added"]),
            "close_warnings": len(stats["close_warning_added"]),
            "closed_items": len(stats["closed"]),
            "would_close_items": len(stats["would_close"]),
            "errors": len(stats["errors"]),
            "dry_run": dry_run
        }

        logger.info(f"Cleanup complete: {stats['summary']}")
        return stats

    def get_health_trends(
        self,
        days: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical health trends.

        Note: This is a simplified version. For production use, you should
        store health metrics over time in a database or file.

        Args:
            days: Number of days of history to analyze

        Returns:
            Dictionary with trend data for each metric

        Example:
            >>> agent = GitHubRepoAgent("owner", "repo", token)
            >>> trends = agent.get_health_trends(days=30)
            >>> for metric, data in trends.items():
            ...     print(f"{metric}: {len(data)} data points")
        """
        logger.info(f"Analyzing health trends for last {days} days...")

        # In a real implementation, this would query stored historical data
        # For now, we provide current snapshot
        current_health = self.monitor_health()

        trends = {
            "overall_score": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": current_health.total_score
                }
            ],
            "issue_velocity": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": current_health.issue_velocity_score
                }
            ],
            "pr_merge_time": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": current_health.pr_merge_time_score
                }
            ],
            "stale_items": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": current_health.stale_item_score
                }
            ],
            "test_coverage": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": current_health.test_coverage_score
                }
            ],
            "contributor_activity": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": current_health.contributor_activity_score
                }
            ]
        }

        logger.info("Health trends retrieved")
        return trends

    # Private helper methods

    def _calculate_issue_velocity_score(self) -> float:
        """Calculate issue velocity score (0-20 points).

        Measures how quickly issues are resolved.
        Target: 80%+ closed within 30 days = 20 points
        """
        try:
            # Get issues from last 30 days
            since = datetime.now() - timedelta(days=30)
            all_issues = list(self.repo.get_issues(state="all", since=since))

            # Filter out PRs
            issues = [issue for issue in all_issues if not issue.pull_request]

            if not issues:
                return 10.0  # Neutral score if no data

            # Count closed issues
            closed_issues = [issue for issue in issues if issue.state == "closed"]

            # Calculate percentage
            close_rate = len(closed_issues) / len(issues) if issues else 0

            # Score: 0% = 0 points, 80%+ = 20 points
            score = min(close_rate / 0.80 * 20, 20.0)

            return score

        except Exception as e:
            logger.error(f"Error calculating issue velocity: {e}")
            return 10.0  # Return neutral score on error

    def _calculate_pr_merge_time_score(self) -> float:
        """Calculate PR merge time score (0-20 points).

        Measures average time to merge PRs.
        Target: <7 days average = 20 points
        """
        try:
            # Get merged PRs from last 30 days
            since = datetime.now() - timedelta(days=30)
            pulls = list(self.repo.get_pulls(state="closed"))

            # Filter to merged PRs in timeframe
            merged_prs = [
                pr for pr in pulls
                if pr.merged_at and pr.merged_at >= since
            ]

            if not merged_prs:
                return 10.0  # Neutral score if no data

            # Calculate average merge time
            merge_times = []
            for pr in merged_prs:
                if pr.merged_at and pr.created_at:
                    merge_time = (pr.merged_at - pr.created_at).days
                    merge_times.append(merge_time)

            if not merge_times:
                return 10.0

            avg_merge_time = sum(merge_times) / len(merge_times)

            # Score: 0 days = 20 points, 7 days = 15 points, 14+ days = 0 points
            if avg_merge_time <= 7:
                score = 20.0 - (avg_merge_time * 0.7)
            else:
                score = max(15.0 - ((avg_merge_time - 7) * 2), 0)

            return score

        except Exception as e:
            logger.error(f"Error calculating PR merge time: {e}")
            return 10.0

    def _calculate_stale_item_score(self) -> float:
        """Calculate stale item score (0-20 points).

        Penalizes repositories with many stale items.
        Target: <10 stale items = 20 points
        """
        try:
            stale_issues = self.get_stale_issues(days=30)
            stale_prs = self.get_stale_prs(days=30)

            total_stale = len(stale_issues) + len(stale_prs)

            # Score: 0 stale = 20 points, 10 stale = 10 points, 20+ stale = 0 points
            if total_stale == 0:
                score = 20.0
            elif total_stale <= 10:
                score = 20.0 - (total_stale * 1.0)
            else:
                score = max(10.0 - ((total_stale - 10) * 1.0), 0)

            return score

        except Exception as e:
            logger.error(f"Error calculating stale item score: {e}")
            return 10.0

    def _calculate_test_coverage_score(self) -> float:
        """Calculate test coverage score (0-20 points).

        Note: This is a simplified version. In production, you would integrate
        with coverage reporting tools (Codecov, Coveralls, etc.)

        Target: 80%+ coverage = 20 points
        """
        try:
            # Check for common coverage badges/files
            # This is a placeholder - integrate with your coverage tool

            # For now, check if tests directory exists
            try:
                self.repo.get_contents("tests")
                has_tests = True
            except:
                has_tests = False

            # Basic scoring: 15 points if tests exist, else 5
            score = 15.0 if has_tests else 5.0

            return score

        except Exception as e:
            logger.error(f"Error calculating test coverage: {e}")
            return 10.0

    def _calculate_contributor_activity_score(self) -> float:
        """Calculate contributor activity score (0-20 points).

        Measures recent contributor engagement.
        Target: 5+ active contributors in last 30 days = 20 points
        """
        try:
            # Get commits from last 30 days
            since = datetime.now() - timedelta(days=30)
            commits = list(self.repo.get_commits(since=since))

            # Get unique contributors
            contributors = set()
            for commit in commits:
                if commit.author:
                    contributors.add(commit.author.login)

            contributor_count = len(contributors)

            # Score: 0 contributors = 0, 5+ = 20 points
            score = min((contributor_count / 5.0) * 20, 20.0)

            return score

        except Exception as e:
            logger.error(f"Error calculating contributor activity: {e}")
            return 10.0

    def _determine_health_category(self, score: float) -> HealthCategory:
        """Determine health category from score.

        Args:
            score: Health score (0-100)

        Returns:
            HealthCategory enum value
        """
        if score >= 90:
            return HealthCategory.EXCELLENT
        elif score >= 75:
            return HealthCategory.GOOD
        elif score >= 60:
            return HealthCategory.FAIR
        elif score >= 40:
            return HealthCategory.POOR
        else:
            return HealthCategory.CRITICAL

    def _add_warning_label(self, item: StaleItem) -> None:
        """Add stale warning label to an item."""
        try:
            if item.type == "issue":
                issue = self.repo.get_issue(item.number)
                issue.add_to_labels("stale")
            elif item.type == "pull_request":
                pr = self.repo.get_pull(item.number)
                pr.add_to_labels("stale")

            logger.info(f"Added stale label to {item.type} #{item.number}")
        except Exception as e:
            logger.error(f"Failed to add label to {item.type} #{item.number}: {e}")

    def _add_close_warning(self, item: StaleItem, days: int) -> None:
        """Add close warning comment to an item."""
        try:
            warning_message = f"""
⚠️ **Stale Item Warning**

This {item.type} has been inactive for {item.days_stale} days and will be automatically closed if there is no activity within the next {90 - days} days.

If this is still relevant, please:
- Add a comment to keep it active
- Update the description or add new information
- Add the `keep-open` label to prevent auto-closure

Last activity: {item.updated_at.strftime('%Y-%m-%d')}
            """.strip()

            if item.type == "issue":
                issue = self.repo.get_issue(item.number)
                issue.create_comment(warning_message)
            elif item.type == "pull_request":
                pr = self.repo.get_pull(item.number)
                pr.create_issue_comment(warning_message)

            logger.info(f"Added close warning to {item.type} #{item.number}")
        except Exception as e:
            logger.error(f"Failed to add warning to {item.type} #{item.number}: {e}")
