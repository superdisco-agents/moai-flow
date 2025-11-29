"""Tests for GitHub Repository Health Agent.

Comprehensive test suite covering:
- Repository health monitoring
- Stale issue detection
- Stale PR detection
- Auto-close stale items
- Health score calculation
- Actionable recommendations
- Stale item cleanup workflows
- Health trends analysis
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from pathlib import Path

from moai_flow.github.repo_agent import (
    GitHubRepoAgent,
    StaleItem,
    HealthMetrics,
    HealthCategory,
    Recommendation,
    RecommendationPriority,
)


class MockGitHubIssue:
    """Mock GitHub issue for testing."""

    def __init__(
        self,
        number,
        title,
        state,
        created_at,
        updated_at,
        labels=None,
        assignees=None,
        is_pr=False,
    ):
        self.number = number
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at
        self.html_url = f"https://github.com/test/repo/issues/{number}"

        # Create label mocks with name attribute
        self.labels = []
        for label in (labels or []):
            label_mock = Mock()
            label_mock.name = label
            self.labels.append(label_mock)

        self.assignees = [Mock(login=assignee) for assignee in (assignees or [])]
        self.pull_request = Mock() if is_pr else None

        # Mock methods
        self.add_to_labels = Mock()
        self.create_comment = Mock()
        self.edit = Mock()

    def _add_label(self, label):
        """Helper to actually add label for testing."""
        label_mock = Mock()
        label_mock.name = label
        self.labels.append(label_mock)


class MockGitHubPR:
    """Mock GitHub pull request for testing."""

    def __init__(
        self,
        number,
        title,
        state,
        created_at,
        updated_at,
        merged_at=None,
        labels=None,
        assignees=None,
    ):
        self.number = number
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at
        self.merged_at = merged_at
        self.html_url = f"https://github.com/test/repo/pull/{number}"

        # Create label mocks with name attribute
        self.labels = []
        for label in (labels or []):
            label_mock = Mock()
            label_mock.name = label
            self.labels.append(label_mock)

        self.assignees = [Mock(login=assignee) for assignee in (assignees or [])]

        # Mock methods
        self.add_to_labels = Mock()
        self.create_issue_comment = Mock()
        self.edit = Mock()


@pytest.fixture
def mock_github():
    """Create mock GitHub client and repository."""
    with patch("moai_flow.github.repo_agent.Github") as mock_gh:
        with patch("moai_flow.github.repo_agent.Auth") as mock_auth:
            mock_client = MagicMock()
            mock_repo = MagicMock()

            mock_gh.return_value = mock_client
            mock_client.get_repo.return_value = mock_repo
            mock_auth.Token.return_value = MagicMock()

            yield mock_repo


@pytest.fixture
def repo_agent(mock_github):
    """Create GitHubRepoAgent instance with mocked GitHub."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        with patch("moai_flow.github.repo_agent.Auth") as mock_auth:
            mock_auth.Token.return_value = MagicMock()
            agent = GitHubRepoAgent("test_owner", "test_repo")
            agent.repo = mock_github
            return agent


class TestStaleIssueDetection:
    """Test suite for stale issue detection."""

    def test_get_stale_issues_30_days(self, repo_agent, mock_github):
        """Test finding issues stale for 30+ days."""
        now = datetime.now()
        old_date = now - timedelta(days=35)

        # Create mock issues
        mock_issues = [
            MockGitHubIssue(1, "Old issue", "open", old_date, old_date),
            MockGitHubIssue(2, "Recent issue", "open", now, now),
            MockGitHubIssue(3, "Stale issue", "open", old_date, old_date),
        ]

        mock_github.get_issues.return_value = mock_issues

        # Get stale issues
        stale = repo_agent.get_stale_issues(days=30)

        # Should find 2 stale issues
        assert len(stale) == 2
        assert all(item.days_stale >= 30 for item in stale)
        assert stale[0].number in [1, 3]

    def test_get_stale_issues_with_labels(self, repo_agent, mock_github):
        """Test filtering stale issues by labels."""
        now = datetime.now()
        old_date = now - timedelta(days=40)

        mock_issues = [
            MockGitHubIssue(1, "Bug issue", "open", old_date, old_date, labels=["bug"]),
            MockGitHubIssue(
                2, "Feature issue", "open", old_date, old_date, labels=["feature"]
            ),
        ]

        mock_github.get_issues.return_value = mock_issues

        # Filter by bug label
        stale = repo_agent.get_stale_issues(days=30, labels=["bug"])

        assert len(stale) == 1
        assert stale[0].number == 1

    def test_get_stale_issues_exclude_labels(self, repo_agent, mock_github):
        """Test excluding issues with specific labels."""
        now = datetime.now()
        old_date = now - timedelta(days=40)

        mock_issues = [
            MockGitHubIssue(
                1, "Keep open", "open", old_date, old_date, labels=["keep-open"]
            ),
            MockGitHubIssue(2, "Normal", "open", old_date, old_date, labels=["bug"]),
        ]

        mock_github.get_issues.return_value = mock_issues

        # Exclude keep-open label
        stale = repo_agent.get_stale_issues(days=30, exclude_labels=["keep-open"])

        assert len(stale) == 1
        assert stale[0].number == 2

    def test_get_stale_issues_sorted_by_staleness(self, repo_agent, mock_github):
        """Test that stale issues are sorted by days stale (descending)."""
        now = datetime.now()

        mock_issues = [
            MockGitHubIssue(1, "30 days", "open", now, now - timedelta(days=30)),
            MockGitHubIssue(2, "60 days", "open", now, now - timedelta(days=60)),
            MockGitHubIssue(3, "45 days", "open", now, now - timedelta(days=45)),
        ]

        mock_github.get_issues.return_value = mock_issues

        stale = repo_agent.get_stale_issues(days=20)

        # Should be sorted by staleness (most stale first)
        assert len(stale) == 3
        assert stale[0].days_stale >= stale[1].days_stale >= stale[2].days_stale


class TestStalePRDetection:
    """Test suite for stale PR detection."""

    def test_get_stale_prs_14_days(self, repo_agent, mock_github):
        """Test finding PRs stale for 14+ days."""
        now = datetime.now()
        old_date = now - timedelta(days=20)

        mock_prs = [
            MockGitHubPR(1, "Old PR", "open", old_date, old_date),
            MockGitHubPR(2, "Recent PR", "open", now, now),
            MockGitHubPR(3, "Stale PR", "open", old_date, old_date),
        ]

        mock_github.get_pulls.return_value = mock_prs

        # Get stale PRs
        stale = repo_agent.get_stale_prs(days=14)

        # Should find 2 stale PRs
        assert len(stale) == 2
        assert all(item.days_stale >= 14 for item in stale)
        assert all(item.type == "pull_request" for item in stale)


class TestAutoCloseStale:
    """Test suite for auto-closing stale items."""

    def test_auto_close_stale_issue(self, repo_agent, mock_github):
        """Test auto-closing a stale issue."""
        now = datetime.now()
        old_date = now - timedelta(days=90)

        mock_issue = MockGitHubIssue(1, "Stale issue", "open", old_date, old_date)
        mock_github.get_issue.return_value = mock_issue

        stale_item = StaleItem(
            number=1,
            title="Stale issue",
            url=mock_issue.html_url,
            state="open",
            created_at=old_date,
            updated_at=old_date,
            days_stale=90,
            type="issue",
        )

        # Auto-close
        success = repo_agent.auto_close_stale(stale_item)

        assert success
        mock_github.get_issue.assert_called_once_with(1)
        mock_issue.create_comment.assert_called_once()
        mock_issue.edit.assert_called_once_with(state="closed")

    def test_auto_close_stale_pr(self, repo_agent, mock_github):
        """Test auto-closing a stale PR."""
        now = datetime.now()
        old_date = now - timedelta(days=60)

        mock_pr = MockGitHubPR(1, "Stale PR", "open", old_date, old_date)
        mock_github.get_pull.return_value = mock_pr

        stale_item = StaleItem(
            number=1,
            title="Stale PR",
            url=mock_pr.html_url,
            state="open",
            created_at=old_date,
            updated_at=old_date,
            days_stale=60,
            type="pull_request",
        )

        # Auto-close
        success = repo_agent.auto_close_stale(stale_item)

        assert success
        mock_github.get_pull.assert_called_once_with(1)
        mock_pr.create_issue_comment.assert_called_once()
        mock_pr.edit.assert_called_once_with(state="closed")

    def test_auto_close_adds_label(self, repo_agent, mock_github):
        """Test that auto-close adds stale label before closing."""
        now = datetime.now()
        old_date = now - timedelta(days=90)

        mock_issue = MockGitHubIssue(1, "Stale", "open", old_date, old_date)
        mock_github.get_issue.return_value = mock_issue

        stale_item = StaleItem(
            number=1,
            title="Stale",
            url=mock_issue.html_url,
            state="open",
            created_at=old_date,
            updated_at=old_date,
            days_stale=90,
            type="issue",
        )

        repo_agent.auto_close_stale(stale_item, label="auto-closed")

        mock_issue.add_to_labels.assert_called_once_with("auto-closed")


class TestHealthScoreCalculation:
    """Test suite for health score calculation."""

    def test_calculate_health_score_returns_float(self, repo_agent):
        """Test that health score returns a float between 0 and 100."""
        with patch.object(repo_agent, "monitor_health") as mock_monitor:
            mock_monitor.return_value = Mock(total_score=75.5)

            score = repo_agent.calculate_health_score()

            assert isinstance(score, float)
            assert 0 <= score <= 100
            assert score == 75.5

    def test_monitor_health_returns_metrics(self, repo_agent):
        """Test that monitor_health returns HealthMetrics."""
        # Mock all score calculation methods
        with patch.object(
            repo_agent, "_calculate_issue_velocity_score", return_value=15.0
        ):
            with patch.object(
                repo_agent, "_calculate_pr_merge_time_score", return_value=18.0
            ):
                with patch.object(
                    repo_agent, "_calculate_stale_item_score", return_value=12.0
                ):
                    with patch.object(
                        repo_agent, "_calculate_test_coverage_score", return_value=10.0
                    ):
                        with patch.object(
                            repo_agent,
                            "_calculate_contributor_activity_score",
                            return_value=14.0,
                        ):
                            health = repo_agent.monitor_health()

                            assert isinstance(health, HealthMetrics)
                            assert health.total_score == 69.0
                            assert health.issue_velocity_score == 15.0
                            assert health.pr_merge_time_score == 18.0
                            assert health.category == HealthCategory.FAIR

    def test_health_category_excellent(self, repo_agent):
        """Test EXCELLENT health category (90-100)."""
        category = repo_agent._determine_health_category(95)
        assert category == HealthCategory.EXCELLENT

    def test_health_category_good(self, repo_agent):
        """Test GOOD health category (75-89)."""
        category = repo_agent._determine_health_category(80)
        assert category == HealthCategory.GOOD

    def test_health_category_fair(self, repo_agent):
        """Test FAIR health category (60-74)."""
        category = repo_agent._determine_health_category(65)
        assert category == HealthCategory.FAIR

    def test_health_category_poor(self, repo_agent):
        """Test POOR health category (40-59)."""
        category = repo_agent._determine_health_category(50)
        assert category == HealthCategory.POOR

    def test_health_category_critical(self, repo_agent):
        """Test CRITICAL health category (0-39)."""
        category = repo_agent._determine_health_category(30)
        assert category == HealthCategory.CRITICAL


class TestActionableRecommendations:
    """Test suite for actionable recommendations."""

    def test_recommendations_for_stale_issues(self, repo_agent, mock_github):
        """Test recommendations when there are many stale issues."""
        # Mock stale issues
        stale_issues = [Mock() for _ in range(25)]

        with patch.object(repo_agent, "get_stale_issues", return_value=stale_issues):
            with patch.object(repo_agent, "get_stale_prs", return_value=[]):
                with patch.object(repo_agent, "monitor_health") as mock_health:
                    mock_health.return_value = Mock(
                        issue_velocity_score=15.0,
                        pr_merge_time_score=18.0,
                        stale_item_score=5.0,
                        test_coverage_score=12.0,
                        contributor_activity_score=14.0,
                    )

                    recommendations = repo_agent.get_actionable_recommendations()

                    # Should recommend addressing stale issues
                    stale_recs = [
                        r
                        for r in recommendations
                        if r.category == "stale_management" and "issue" in r.action
                    ]
                    assert len(stale_recs) > 0
                    assert stale_recs[0].priority == RecommendationPriority.HIGH

    def test_recommendations_for_stale_prs(self, repo_agent, mock_github):
        """Test CRITICAL priority for many stale PRs."""
        # Mock stale PRs
        stale_prs = [Mock() for _ in range(15)]

        with patch.object(repo_agent, "get_stale_issues", return_value=[]):
            with patch.object(repo_agent, "get_stale_prs", return_value=stale_prs):
                with patch.object(repo_agent, "monitor_health") as mock_health:
                    mock_health.return_value = Mock(
                        issue_velocity_score=15.0,
                        pr_merge_time_score=18.0,
                        stale_item_score=5.0,
                        test_coverage_score=12.0,
                        contributor_activity_score=14.0,
                    )

                    recommendations = repo_agent.get_actionable_recommendations()

                    # Should recommend addressing stale PRs with CRITICAL priority
                    pr_recs = [
                        r
                        for r in recommendations
                        if r.category == "stale_management"
                        and "pull request" in r.action
                    ]
                    assert len(pr_recs) > 0
                    assert pr_recs[0].priority == RecommendationPriority.CRITICAL

    def test_recommendations_sorted_by_priority(self, repo_agent, mock_github):
        """Test that recommendations are sorted by priority."""
        with patch.object(repo_agent, "get_stale_issues", return_value=[]):
            with patch.object(repo_agent, "get_stale_prs", return_value=[]):
                with patch.object(repo_agent, "monitor_health") as mock_health:
                    mock_health.return_value = Mock(
                        issue_velocity_score=5.0,
                        pr_merge_time_score=5.0,
                        stale_item_score=15.0,
                        test_coverage_score=5.0,
                        contributor_activity_score=5.0,
                    )

                    recommendations = repo_agent.get_actionable_recommendations()

                    # Verify sorted by priority
                    priority_values = {
                        RecommendationPriority.CRITICAL: 0,
                        RecommendationPriority.HIGH: 1,
                        RecommendationPriority.MEDIUM: 2,
                        RecommendationPriority.LOW: 3,
                    }

                    for i in range(len(recommendations) - 1):
                        current_priority = priority_values[recommendations[i].priority]
                        next_priority = priority_values[recommendations[i + 1].priority]
                        assert current_priority <= next_priority


class TestCleanupStaleItems:
    """Test suite for batch cleanup workflow."""

    def test_cleanup_dry_run(self, repo_agent, mock_github):
        """Test cleanup in dry run mode."""
        now = datetime.now()
        old_date = now - timedelta(days=95)

        stale_item = StaleItem(
            number=1,
            title="Old",
            url="https://github.com/test/repo/issues/1",
            state="open",
            created_at=old_date,
            updated_at=old_date,
            days_stale=95,
            type="issue",
        )

        with patch.object(repo_agent, "get_stale_issues", return_value=[stale_item]):
            with patch.object(repo_agent, "get_stale_prs", return_value=[]):
                result = repo_agent.cleanup_stale_items(dry_run=True)

                # Should report what would be closed
                assert result["summary"]["dry_run"] is True
                assert len(result["would_close"]) > 0
                assert len(result["closed"]) == 0

    def test_cleanup_execution(self, repo_agent, mock_github):
        """Test actual cleanup execution."""
        now = datetime.now()
        old_date = now - timedelta(days=95)

        mock_issue = MockGitHubIssue(1, "Old", "open", old_date, old_date)
        mock_github.get_issue.return_value = mock_issue

        stale_item = StaleItem(
            number=1,
            title="Old",
            url=mock_issue.html_url,
            state="open",
            created_at=old_date,
            updated_at=old_date,
            days_stale=95,
            type="issue",
        )

        with patch.object(
            repo_agent, "get_stale_issues", return_value=[stale_item]
        ) as mock_get_issues:
            with patch.object(repo_agent, "get_stale_prs", return_value=[]):
                result = repo_agent.cleanup_stale_items(
                    auto_close_days=90, dry_run=False
                )

                # Should actually close items
                assert result["summary"]["dry_run"] is False
                assert len(result["closed"]) > 0


class TestHealthTrends:
    """Test suite for health trends analysis."""

    def test_get_health_trends_returns_metrics(self, repo_agent):
        """Test that health trends returns structured data."""
        with patch.object(repo_agent, "monitor_health") as mock_health:
            mock_health.return_value = Mock(
                total_score=75.0,
                issue_velocity_score=15.0,
                pr_merge_time_score=18.0,
                stale_item_score=12.0,
                test_coverage_score=10.0,
                contributor_activity_score=14.0,
            )

            trends = repo_agent.get_health_trends(days=30)

            # Should have all metric categories
            assert "overall_score" in trends
            assert "issue_velocity" in trends
            assert "pr_merge_time" in trends
            assert "stale_items" in trends
            assert "test_coverage" in trends
            assert "contributor_activity" in trends

            # Each should have timestamp and value
            for metric, data in trends.items():
                assert len(data) > 0
                assert "timestamp" in data[0]
                assert "value" in data[0]


class TestInitialization:
    """Test suite for GitHubRepoAgent initialization."""

    def test_init_with_token(self, mock_github):
        """Test initialization with explicit token."""
        with patch("moai_flow.github.repo_agent.Auth") as mock_auth:
            mock_auth.Token.return_value = MagicMock()
            agent = GitHubRepoAgent("owner", "repo", "explicit_token")

            assert agent.repo_owner == "owner"
            assert agent.repo_name == "repo"
            assert agent.github_token == "explicit_token"

    def test_init_with_env_token(self, mock_github):
        """Test initialization with environment variable token."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env_token"}):
            with patch("moai_flow.github.repo_agent.Auth") as mock_auth:
                mock_auth.Token.return_value = MagicMock()
                agent = GitHubRepoAgent("owner", "repo")

                assert agent.github_token == "env_token"

    def test_init_without_token_raises_error(self, mock_github):
        """Test that missing token raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                GitHubRepoAgent("owner", "repo")

    def test_init_without_pygithub_raises_error(self):
        """Test that missing PyGithub raises ImportError."""
        with patch("moai_flow.github.repo_agent.Github", None):
            with pytest.raises(ImportError, match="PyGithub is required"):
                GitHubRepoAgent("owner", "repo", "token")
