"""Unit tests for GitHub Health Metrics System (PRD-06).

Tests cover:
- Individual metric calculators
- HealthMetrics dataclass
- HealthTrend analysis
- Health score calculation
- Trend comparison
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from moai_flow.github.health_metrics import (
    HealthMetricsAnalyzer,
    HealthMetrics,
    HealthTrend,
    HealthComparison,
)


class TestHealthMetrics:
    """Test suite for HealthMetrics dataclass."""

    def test_health_metrics_creation(self):
        """Test creating HealthMetrics instance."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=10.5,
            pr_merge_time=2.3,
            stale_count=5,
            contributor_activity=8,
            test_coverage_trend=1.5,
            health_score=85,
            trend=HealthTrend.IMPROVING,
        )

        assert metrics.issue_velocity == 10.5
        assert metrics.pr_merge_time == 2.3
        assert metrics.stale_count == 5
        assert metrics.contributor_activity == 8
        assert metrics.test_coverage_trend == 1.5
        assert metrics.health_score == 85
        assert metrics.trend == HealthTrend.IMPROVING

    def test_health_metrics_to_dict(self):
        """Test converting HealthMetrics to dictionary."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=10.5,
            pr_merge_time=2.3,
            stale_count=5,
            contributor_activity=8,
            test_coverage_trend=1.5,
            health_score=85,
            trend=HealthTrend.IMPROVING,
        )

        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert metrics_dict["issue_velocity"] == 10.5
        assert metrics_dict["pr_merge_time"] == 2.3
        assert metrics_dict["stale_count"] == 5
        assert metrics_dict["contributor_activity"] == 8
        assert metrics_dict["test_coverage_trend"] == 1.5
        assert metrics_dict["health_score"] == 85
        assert metrics_dict["trend"] == "improving"


class TestHealthTrend:
    """Test suite for HealthTrend enum."""

    def test_health_trend_values(self):
        """Test HealthTrend enum values."""
        assert HealthTrend.IMPROVING.value == "improving"
        assert HealthTrend.STABLE.value == "stable"
        assert HealthTrend.DEGRADING.value == "degrading"


@pytest.fixture
def mock_github_repo():
    """Create a mock GitHub repository."""
    repo = Mock()
    repo.owner = Mock()
    repo.owner.login = "test-owner"
    repo.name = "test-repo"
    return repo


@pytest.fixture
def mock_github_client(mock_github_repo):
    """Create a mock GitHub client."""
    client = Mock()
    client.get_repo = Mock(return_value=mock_github_repo)
    return client


@pytest.fixture
def health_analyzer(mock_github_client, mock_github_repo):
    """Create HealthMetricsAnalyzer with mocked GitHub client."""
    with patch("moai_flow.github.health_metrics.Github") as mock_github:
        with patch("moai_flow.github.health_metrics.Auth"):
            mock_github.return_value = mock_github_client
            analyzer = HealthMetricsAnalyzer(
                repo_owner="test-owner",
                repo_name="test-repo",
                github_token="fake-token",
            )
            analyzer.repo = mock_github_repo
            return analyzer


class TestHealthMetricsAnalyzer:
    """Test suite for HealthMetricsAnalyzer."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        with patch("moai_flow.github.health_metrics.Github"):
            with patch("moai_flow.github.health_metrics.Auth"):
                analyzer = HealthMetricsAnalyzer(
                    repo_owner="test-owner",
                    repo_name="test-repo",
                    github_token="fake-token",
                    stale_days=60,
                )

                assert analyzer.repo_owner == "test-owner"
                assert analyzer.repo_name == "test-repo"
                assert analyzer.stale_days == 60

    def test_calculate_issue_velocity(self, health_analyzer):
        """Test issue velocity calculation."""
        # Mock closed issues
        mock_issues = []
        for i in range(20):
            issue = Mock()
            issue.pull_request = None  # Not a PR
            issue.closed_at = datetime.now() - timedelta(days=i)
            mock_issues.append(issue)

        health_analyzer.repo.get_issues = Mock(return_value=mock_issues)

        velocity = health_analyzer.calculate_issue_velocity(lookback_weeks=4)

        assert isinstance(velocity, float)
        assert velocity >= 0
        assert velocity == 5.0  # 20 issues / 4 weeks

    def test_calculate_pr_merge_time(self, health_analyzer):
        """Test PR merge time calculation."""
        # Mock merged PRs
        mock_prs = []
        for i in range(10):
            pr = Mock()
            pr.merged = True
            pr.created_at = datetime.now() - timedelta(days=i + 5)
            pr.merged_at = datetime.now() - timedelta(days=i)
            mock_prs.append(pr)

        health_analyzer.repo.get_pulls = Mock(return_value=mock_prs)

        merge_time = health_analyzer.calculate_pr_merge_time(lookback_weeks=4)

        assert isinstance(merge_time, float)
        assert merge_time >= 0

    def test_calculate_stale_count(self, health_analyzer):
        """Test stale count calculation."""
        # Mock stale issues
        old_date = datetime.now() - timedelta(days=90)
        recent_date = datetime.now() - timedelta(days=30)

        mock_issues = [
            Mock(pull_request=None, updated_at=old_date),  # Stale
            Mock(pull_request=None, updated_at=old_date),  # Stale
            Mock(pull_request=None, updated_at=recent_date),  # Not stale
        ]

        mock_prs = [
            Mock(updated_at=old_date),  # Stale
            Mock(updated_at=recent_date),  # Not stale
        ]

        health_analyzer.repo.get_issues = Mock(return_value=mock_issues)
        health_analyzer.repo.get_pulls = Mock(return_value=mock_prs)

        stale_count = health_analyzer.calculate_stale_count()

        assert stale_count == 3  # 2 stale issues + 1 stale PR

    def test_calculate_contributor_activity(self, health_analyzer):
        """Test contributor activity calculation."""
        # Mock commits with different authors
        mock_commits = []
        for i in range(20):
            commit = Mock()
            commit.author = Mock()
            commit.author.login = f"contributor-{i % 5}"  # 5 unique contributors
            mock_commits.append(commit)

        health_analyzer.repo.get_commits = Mock(return_value=mock_commits)

        activity = health_analyzer.calculate_contributor_activity(lookback_weeks=4)

        assert activity == 5  # 5 unique contributors

    def test_calculate_test_coverage_trend(self, health_analyzer):
        """Test test coverage trend calculation."""
        # Note: This returns 0.0 in current implementation (no coverage data)
        coverage_trend = health_analyzer.calculate_test_coverage_trend(lookback_weeks=4)

        assert isinstance(coverage_trend, float)
        assert coverage_trend == 0.0

    def test_calculate_health_score(self, health_analyzer):
        """Test health score calculation."""
        score = health_analyzer._calculate_health_score(
            issue_velocity=10.0,  # Good velocity
            pr_merge_time=2.0,  # Fast merge
            stale_count=5,  # Low stale count
            contributor_activity=5,  # Active contributors
            test_coverage_trend=0.0,  # Stable coverage
        )

        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert score >= 70  # Should be high score

    def test_calculate_health_score_poor(self, health_analyzer):
        """Test health score calculation with poor metrics."""
        score = health_analyzer._calculate_health_score(
            issue_velocity=1.0,  # Low velocity
            pr_merge_time=15.0,  # Slow merge
            stale_count=50,  # High stale count
            contributor_activity=1,  # Few contributors
            test_coverage_trend=-5.0,  # Degrading coverage
        )

        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert score < 50  # Should be low score

    def test_determine_trend_improving(self, health_analyzer):
        """Test trend determination for improving health."""
        trend = health_analyzer._determine_trend(80)
        assert trend == HealthTrend.IMPROVING

    def test_determine_trend_stable(self, health_analyzer):
        """Test trend determination for stable health."""
        trend = health_analyzer._determine_trend(60)
        assert trend == HealthTrend.STABLE

    def test_determine_trend_degrading(self, health_analyzer):
        """Test trend determination for degrading health."""
        trend = health_analyzer._determine_trend(40)
        assert trend == HealthTrend.DEGRADING


class TestHealthComparison:
    """Test suite for health trend analysis."""

    def test_analyze_trend_improving(self, health_analyzer):
        """Test trend analysis with improving health."""
        current = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=12.0,
            pr_merge_time=2.0,
            stale_count=5,
            contributor_activity=8,
            test_coverage_trend=1.0,
            health_score=85,
            trend=HealthTrend.IMPROVING,
        )

        previous = HealthMetrics(
            timestamp=datetime.now() - timedelta(weeks=4),
            issue_velocity=8.0,
            pr_merge_time=3.0,
            stale_count=10,
            contributor_activity=5,
            test_coverage_trend=0.0,
            health_score=70,
            trend=HealthTrend.STABLE,
        )

        comparison = health_analyzer.analyze_trend(current, [previous])

        assert comparison.trend == HealthTrend.IMPROVING
        assert comparison.change_percentage > 0
        assert "issue_velocity" in comparison.improvements
        assert "pr_merge_time" in comparison.improvements
        assert "stale_count" in comparison.improvements

    def test_analyze_trend_degrading(self, health_analyzer):
        """Test trend analysis with degrading health."""
        current = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=5.0,
            pr_merge_time=5.0,
            stale_count=20,
            contributor_activity=3,
            test_coverage_trend=-2.0,
            health_score=45,
            trend=HealthTrend.DEGRADING,
        )

        previous = HealthMetrics(
            timestamp=datetime.now() - timedelta(weeks=4),
            issue_velocity=10.0,
            pr_merge_time=2.0,
            stale_count=8,
            contributor_activity=7,
            test_coverage_trend=0.0,
            health_score=75,
            trend=HealthTrend.STABLE,
        )

        comparison = health_analyzer.analyze_trend(current, [previous])

        assert comparison.trend == HealthTrend.DEGRADING
        assert comparison.change_percentage < 0
        assert "issue_velocity" in comparison.degradations
        assert "pr_merge_time" in comparison.degradations
        assert "stale_count" in comparison.degradations

    def test_analyze_trend_stable(self, health_analyzer):
        """Test trend analysis with stable health."""
        current = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=10.0,
            pr_merge_time=2.5,
            stale_count=8,
            contributor_activity=6,
            test_coverage_trend=0.0,
            health_score=72,
            trend=HealthTrend.STABLE,
        )

        previous = HealthMetrics(
            timestamp=datetime.now() - timedelta(weeks=4),
            issue_velocity=10.0,
            pr_merge_time=2.5,
            stale_count=8,
            contributor_activity=6,
            test_coverage_trend=0.0,
            health_score=72,
            trend=HealthTrend.STABLE,
        )

        comparison = health_analyzer.analyze_trend(current, [previous])

        assert comparison.trend == HealthTrend.STABLE
        assert abs(comparison.change_percentage) <= 5
        assert len(comparison.improvements) == 0
        assert len(comparison.degradations) == 0

    def test_analyze_trend_no_history(self, health_analyzer):
        """Test trend analysis with no historical data."""
        current = HealthMetrics(
            timestamp=datetime.now(),
            issue_velocity=10.0,
            pr_merge_time=2.5,
            stale_count=8,
            contributor_activity=6,
            test_coverage_trend=0.0,
            health_score=72,
            trend=HealthTrend.STABLE,
        )

        comparison = health_analyzer.analyze_trend(current, [])

        assert comparison.trend == HealthTrend.STABLE
        assert comparison.change_percentage == 0.0
        assert len(comparison.improvements) == 0
        assert len(comparison.degradations) == 0


class TestIntegration:
    """Integration tests for the complete health metrics system."""

    def test_calculate_health_metrics_complete(self, health_analyzer):
        """Test complete health metrics calculation."""
        # Mock all necessary GitHub API calls
        health_analyzer.repo.get_issues = Mock(return_value=[
            Mock(pull_request=None, closed_at=datetime.now(), created_at=datetime.now() - timedelta(days=3))
            for _ in range(20)
        ])

        health_analyzer.repo.get_pulls = Mock(return_value=[
            Mock(
                merged=True,
                created_at=datetime.now() - timedelta(days=5),
                merged_at=datetime.now() - timedelta(days=2),
            )
            for _ in range(10)
        ])

        health_analyzer.repo.get_commits = Mock(return_value=[
            Mock(author=Mock(login=f"user-{i % 5}"))
            for i in range(30)
        ])

        metrics = health_analyzer.calculate_health_metrics(
            lookback_weeks=4,
            include_detailed=True
        )

        assert isinstance(metrics, HealthMetrics)
        assert isinstance(metrics.health_score, int)
        assert 0 <= metrics.health_score <= 100
        assert isinstance(metrics.trend, HealthTrend)
        assert metrics.issue_velocity >= 0
        assert metrics.pr_merge_time >= 0
        assert metrics.stale_count >= 0
        assert metrics.contributor_activity >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
