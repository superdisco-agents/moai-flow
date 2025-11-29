"""Comprehensive tests for GitHub PR Agent.

Tests cover:
- PR creation with various configurations
- Description generation from SPEC
- Metadata management (labels, reviewers, assignees)
- Status updates (draft/ready toggle)
- Comment posting
- Review requests
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile
import os

from moai_flow.github.pr_agent import (
    GitHubPRAgent,
    PRMetadata,
    FileChange,
    GithubException,
)


@pytest.fixture
def mock_github():
    """Mock GitHub client and repository."""
    with patch("moai_flow.github.pr_agent.Github") as mock_gh:
        mock_client = MagicMock()
        mock_repo = MagicMock()

        mock_gh.return_value = mock_client
        mock_client.get_repo.return_value = mock_repo

        yield {
            "client": mock_client,
            "repo": mock_repo,
            "github": mock_gh,
        }


@pytest.fixture
def mock_auth():
    """Mock GitHub authentication."""
    with patch("moai_flow.github.pr_agent.Auth") as mock_auth:
        mock_token = MagicMock()
        mock_auth.Token.return_value = mock_token
        yield mock_auth


@pytest.fixture
def pr_agent(mock_github, mock_auth):
    """Create PR agent instance with mocked GitHub."""
    agent = GitHubPRAgent(
        repo_owner="test-owner",
        repo_name="test-repo",
        github_token="test-token-123",
    )
    return agent


@pytest.fixture
def sample_file_changes():
    """Sample file changes for testing."""
    return [
        FileChange(
            path="src/api/users.py",
            additions=50,
            deletions=10,
            change_type="modified",
        ),
        FileChange(
            path="tests/test_users.py",
            additions=30,
            deletions=5,
            change_type="modified",
        ),
        FileChange(
            path="docs/api.md",
            additions=20,
            deletions=0,
            change_type="added",
        ),
    ]


@pytest.fixture
def temp_spec_dir():
    """Create temporary SPEC directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        spec_dir = Path(tmpdir) / ".moai" / "specs" / "SPEC-001"
        spec_dir.mkdir(parents=True)

        spec_content = """# User Authentication Feature

## Summary

Implement JWT-based authentication for user login and registration.

## Breaking Changes

- API endpoint `/login` now requires email instead of username

## Deployment

1. Run database migrations
2. Update environment variables
3. Restart API servers
"""
        (spec_dir / "spec.md").write_text(spec_content)

        # Change to temp directory for tests
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        yield tmpdir

        os.chdir(original_dir)


class TestGitHubPRAgentInit:
    """Test PR agent initialization."""

    def test_init_with_token(self, mock_github, mock_auth):
        """Test initialization with explicit token."""
        agent = GitHubPRAgent("owner", "repo", "test-token")

        assert agent.repo_owner == "owner"
        assert agent.repo_name == "repo"
        assert agent.github_token == "test-token"

    def test_init_with_env_token(self, mock_github, mock_auth, monkeypatch):
        """Test initialization with environment variable token."""
        monkeypatch.setenv("GITHUB_TOKEN", "env-token")

        agent = GitHubPRAgent("owner", "repo")

        assert agent.github_token == "env-token"

    def test_init_without_token(self, mock_github, mock_auth, monkeypatch):
        """Test initialization fails without token."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        with pytest.raises(ValueError, match="GitHub token is required"):
            GitHubPRAgent("owner", "repo")

    def test_init_calls_github_api(self, mock_github, mock_auth):
        """Test that initialization sets up GitHub client."""
        agent = GitHubPRAgent("owner", "repo", "token")

        mock_auth.Token.assert_called_once_with("token")
        mock_github["client"].get_repo.assert_called_once_with("owner/repo")


class TestCreatePR:
    """Test PR creation functionality."""

    def test_create_pr_basic(self, pr_agent, mock_github):
        """Test basic PR creation."""
        # Setup mocks
        mock_branch = MagicMock()
        mock_github["repo"].get_branch.return_value = mock_branch

        mock_comparison = MagicMock()
        mock_comparison.total_commits = 5
        mock_comparison.files = [
            MagicMock(
                filename="src/api.py",
                additions=50,
                deletions=10,
                status="modified",
            )
        ]
        mock_github["repo"].compare.return_value = mock_comparison

        mock_pr = MagicMock()
        mock_pr.number = 123
        mock_github["repo"].create_pull.return_value = mock_pr

        # Create PR
        pr_number = pr_agent.create_pr(
            branch_name="feature/test",
            base_branch="main",
        )

        assert pr_number == 123
        mock_github["repo"].create_pull.assert_called_once()

    def test_create_pr_with_spec(self, pr_agent, mock_github, temp_spec_dir):
        """Test PR creation with SPEC integration."""
        # Setup mocks
        mock_branch = MagicMock()
        mock_github["repo"].get_branch.return_value = mock_branch

        mock_comparison = MagicMock()
        mock_comparison.total_commits = 3
        mock_comparison.files = []
        mock_github["repo"].compare.return_value = mock_comparison

        mock_pr = MagicMock()
        mock_pr.number = 456
        mock_github["repo"].create_pull.return_value = mock_pr

        # Create PR with SPEC
        pr_number = pr_agent.create_pr(
            branch_name="feature/SPEC-001",
            base_branch="main",
            spec_id="SPEC-001",
        )

        assert pr_number == 456

        # Verify PR was created with SPEC content
        call_args = mock_github["repo"].create_pull.call_args
        assert "SPEC-001" in call_args.kwargs["title"]

    def test_create_pr_with_auto_labels(self, pr_agent, mock_github):
        """Test PR creation with automatic label assignment."""
        # Setup mocks
        mock_branch = MagicMock()
        mock_github["repo"].get_branch.return_value = mock_branch

        mock_comparison = MagicMock()
        mock_comparison.total_commits = 2
        mock_comparison.files = [
            MagicMock(
                filename="tests/test_api.py",
                additions=30,
                deletions=5,
                status="added",
            )
        ]
        mock_github["repo"].compare.return_value = mock_comparison

        mock_pr = MagicMock()
        mock_pr.number = 789
        mock_github["repo"].create_pull.return_value = mock_pr

        # Create PR with auto labels
        pr_number = pr_agent.create_pr(
            branch_name="feature/tests",
            base_branch="main",
            auto_labels=True,
        )

        # Verify labels were added
        mock_pr.add_to_labels.assert_called_once()
        labels = mock_pr.add_to_labels.call_args[0]
        assert "testing" in labels

    def test_create_pr_draft(self, pr_agent, mock_github):
        """Test draft PR creation."""
        # Setup mocks
        mock_branch = MagicMock()
        mock_github["repo"].get_branch.return_value = mock_branch

        mock_comparison = MagicMock()
        mock_comparison.total_commits = 1
        mock_comparison.files = []
        mock_github["repo"].compare.return_value = mock_comparison

        mock_pr = MagicMock()
        mock_pr.number = 999
        mock_github["repo"].create_pull.return_value = mock_pr

        # Create draft PR
        pr_number = pr_agent.create_pr(
            branch_name="feature/wip",
            base_branch="main",
            is_draft=True,
        )

        # Verify draft flag was set
        call_args = mock_github["repo"].create_pull.call_args
        assert call_args.kwargs["draft"] is True

    def test_create_pr_branch_not_found(self, pr_agent, mock_github):
        """Test PR creation fails when branch doesn't exist."""
        mock_github["repo"].get_branch.side_effect = GithubException(
            404, {"message": "Branch not found"}
        )

        with pytest.raises(ValueError, match="Branch not found"):
            pr_agent.create_pr(
                branch_name="nonexistent",
                base_branch="main",
            )

    def test_create_pr_no_changes(self, pr_agent, mock_github):
        """Test PR creation fails when no changes exist."""
        mock_branch = MagicMock()
        mock_github["repo"].get_branch.return_value = mock_branch

        mock_comparison = MagicMock()
        mock_comparison.total_commits = 0
        mock_github["repo"].compare.return_value = mock_comparison

        with pytest.raises(ValueError, match="No changes"):
            pr_agent.create_pr(
                branch_name="feature/empty",
                base_branch="main",
            )


class TestGenerateDescription:
    """Test PR description generation."""

    def test_generate_description_basic(self, pr_agent, sample_file_changes):
        """Test basic description generation."""
        description = pr_agent.generate_description(None, sample_file_changes)

        assert "Changes" in description
        assert "Test Plan" in description
        assert "src/api/users.py" in description

    def test_generate_description_with_spec(
        self, pr_agent, sample_file_changes, temp_spec_dir
    ):
        """Test description generation with SPEC integration."""
        description = pr_agent.generate_description("SPEC-001", sample_file_changes)

        assert "SPEC-001" in description
        assert "JWT-based authentication" in description
        assert "Breaking Changes" in description
        assert "requires email instead of username" in description

    def test_generate_description_includes_test_plan(
        self, pr_agent, sample_file_changes
    ):
        """Test that description includes test plan checklist."""
        description = pr_agent.generate_description(None, sample_file_changes)

        assert "- [ ] Unit tests passing" in description
        assert "- [ ] Coverage >= 90%" in description

    def test_generate_description_formats_file_changes(
        self, pr_agent, sample_file_changes
    ):
        """Test file changes are formatted as table."""
        description = pr_agent.generate_description(None, sample_file_changes)

        # Check markdown table format
        assert "| File | Changes | Type |" in description
        assert "+50/-10" in description
        assert "modified" in description


class TestSetMetadata:
    """Test PR metadata management."""

    def test_set_labels(self, pr_agent, mock_github):
        """Test setting PR labels."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.set_metadata(
            pr_number=123,
            labels=["enhancement", "api"],
        )

        mock_pr.add_to_labels.assert_called_once_with("enhancement", "api")

    def test_set_reviewers(self, pr_agent, mock_github):
        """Test requesting PR reviewers."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.set_metadata(
            pr_number=123,
            reviewers=["reviewer1", "reviewer2"],
        )

        mock_pr.create_review_request.assert_called_once_with(
            reviewers=["reviewer1", "reviewer2"]
        )

    def test_set_assignees(self, pr_agent, mock_github):
        """Test setting PR assignees."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.set_metadata(
            pr_number=123,
            assignees=["user1", "user2"],
        )

        mock_pr.add_to_assignees.assert_called_once_with("user1", "user2")

    def test_set_all_metadata(self, pr_agent, mock_github):
        """Test setting all metadata at once."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.set_metadata(
            pr_number=123,
            labels=["bug"],
            reviewers=["reviewer"],
            assignees=["assignee"],
        )

        mock_pr.add_to_labels.assert_called_once()
        mock_pr.create_review_request.assert_called_once()
        mock_pr.add_to_assignees.assert_called_once()

    def test_set_metadata_api_error(self, pr_agent, mock_github):
        """Test metadata setting handles API errors."""
        mock_github["repo"].get_pull.side_effect = GithubException(
            500, {"message": "Internal error"}
        )

        with pytest.raises(GithubException):
            pr_agent.set_metadata(pr_number=123, labels=["test"])


class TestUpdateStatus:
    """Test PR status updates (draft/ready)."""

    @patch("moai_flow.github.pr_agent.GitHubPRAgent._execute_graphql")
    def test_update_to_draft(self, mock_graphql, pr_agent, mock_github):
        """Test converting PR to draft."""
        mock_pr = MagicMock()
        mock_pr.raw_data = {"node_id": "PR_node_123"}
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.update_status(pr_number=123, is_draft=True)

        mock_graphql.assert_called_once()
        call_args = mock_graphql.call_args
        assert "convertPullRequestToDraft" in call_args[0][0]

    @patch("moai_flow.github.pr_agent.GitHubPRAgent._execute_graphql")
    def test_update_to_ready(self, mock_graphql, pr_agent, mock_github):
        """Test marking PR as ready for review."""
        mock_pr = MagicMock()
        mock_pr.raw_data = {"node_id": "PR_node_456"}
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.update_status(pr_number=456, is_draft=False)

        mock_graphql.assert_called_once()
        call_args = mock_graphql.call_args
        assert "markPullRequestReadyForReview" in call_args[0][0]


class TestAddComment:
    """Test PR comment functionality."""

    def test_add_comment(self, pr_agent, mock_github):
        """Test adding comment to PR."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.add_comment(pr_number=123, comment="Test comment")

        mock_pr.create_issue_comment.assert_called_once_with("Test comment")

    def test_add_comment_markdown(self, pr_agent, mock_github):
        """Test adding markdown comment."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        markdown_comment = "## Review Notes\n\n- Point 1\n- Point 2"
        pr_agent.add_comment(pr_number=123, comment=markdown_comment)

        mock_pr.create_issue_comment.assert_called_once_with(markdown_comment)

    def test_add_comment_api_error(self, pr_agent, mock_github):
        """Test comment addition handles API errors."""
        mock_pr = MagicMock()
        mock_pr.create_issue_comment.side_effect = GithubException(
            403, {"message": "Forbidden"}
        )
        mock_github["repo"].get_pull.return_value = mock_pr

        with pytest.raises(GithubException):
            pr_agent.add_comment(pr_number=123, comment="Test")


class TestRequestReview:
    """Test review request functionality."""

    def test_request_review_single(self, pr_agent, mock_github):
        """Test requesting review from single user."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        pr_agent.request_review(pr_number=123, reviewers=["reviewer1"])

        mock_pr.create_review_request.assert_called_once_with(reviewers=["reviewer1"])

    def test_request_review_multiple(self, pr_agent, mock_github):
        """Test requesting review from multiple users."""
        mock_pr = MagicMock()
        mock_github["repo"].get_pull.return_value = mock_pr

        reviewers = ["reviewer1", "reviewer2", "reviewer3"]
        pr_agent.request_review(pr_number=123, reviewers=reviewers)

        mock_pr.create_review_request.assert_called_once_with(reviewers=reviewers)

    def test_request_review_api_error(self, pr_agent, mock_github):
        """Test review request handles API errors."""
        mock_pr = MagicMock()
        mock_pr.create_review_request.side_effect = GithubException(
            422, {"message": "User not found"}
        )
        mock_github["repo"].get_pull.return_value = mock_pr

        with pytest.raises(GithubException):
            pr_agent.request_review(pr_number=123, reviewers=["nonexistent"])


class TestLabelDetermination:
    """Test automatic label determination."""

    def test_determine_labels_api(self, pr_agent):
        """Test API-related files get api label."""
        file_changes = [
            FileChange("src/api/users.py", 10, 5, "modified"),
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "api" in labels

    def test_determine_labels_frontend(self, pr_agent):
        """Test frontend files get frontend label."""
        file_changes = [
            FileChange("src/ui/components/Button.tsx", 20, 0, "added"),
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "frontend" in labels

    def test_determine_labels_testing(self, pr_agent):
        """Test test files get testing label."""
        file_changes = [
            FileChange("tests/test_api.py", 50, 10, "modified"),
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "testing" in labels

    def test_determine_labels_docs(self, pr_agent):
        """Test documentation files get documentation label."""
        file_changes = [
            FileChange("docs/README.md", 30, 5, "modified"),
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "documentation" in labels

    def test_determine_labels_size_small(self, pr_agent):
        """Test small changes get size:small label."""
        file_changes = [
            FileChange("src/utils.py", 10, 5, "modified"),  # 15 total changes
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "size:small" in labels

    def test_determine_labels_size_large(self, pr_agent):
        """Test large changes get size:large label."""
        file_changes = [
            FileChange("src/api.py", 150, 80, "modified"),  # 230 total changes
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "size:large" in labels

    def test_determine_labels_multiple(self, pr_agent):
        """Test multiple labels from different file types."""
        file_changes = [
            FileChange("src/api/users.py", 30, 10, "modified"),
            FileChange("tests/test_users.py", 20, 5, "added"),
            FileChange("docs/api.md", 15, 0, "added"),
        ]

        labels = pr_agent._determine_labels(file_changes)

        assert "api" in labels
        assert "testing" in labels
        assert "documentation" in labels


class TestPRMetadata:
    """Test PRMetadata dataclass."""

    def test_pr_metadata_creation(self):
        """Test creating PRMetadata object."""
        metadata = PRMetadata(
            title="Test PR",
            description="Test description",
            labels=["bug", "urgent"],
            reviewers=["reviewer1"],
            assignees=["user1"],
            is_draft=True,
        )

        assert metadata.title == "Test PR"
        assert metadata.is_draft is True
        assert len(metadata.labels) == 2

    def test_pr_metadata_defaults(self):
        """Test PRMetadata default values."""
        metadata = PRMetadata(
            title="Test",
            description="Desc",
            labels=[],
            reviewers=[],
            assignees=[],
        )

        assert metadata.is_draft is False


class TestFileChange:
    """Test FileChange dataclass."""

    def test_file_change_creation(self):
        """Test creating FileChange object."""
        change = FileChange(
            path="src/api.py",
            additions=50,
            deletions=10,
            change_type="modified",
        )

        assert change.path == "src/api.py"
        assert change.additions == 50
        assert change.deletions == 10
        assert change.change_type == "modified"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_pygithub(self):
        """Test graceful handling when PyGithub is not installed."""
        with patch("moai_flow.github.pr_agent.Github", None):
            with pytest.raises(ImportError, match="PyGithub is required"):
                GitHubPRAgent("owner", "repo", "token")

    def test_api_rate_limit(self, pr_agent, mock_github):
        """Test handling of GitHub API rate limit errors."""
        mock_github["repo"].get_pull.side_effect = GithubException(
            403, {"message": "API rate limit exceeded"}
        )

        with pytest.raises(GithubException, match="rate limit"):
            pr_agent.set_metadata(pr_number=123, labels=["test"])

    def test_network_timeout(self, pr_agent, mock_github):
        """Test handling of network timeout errors."""
        import requests

        mock_github["repo"].create_pull.side_effect = requests.Timeout(
            "Connection timeout"
        )

        with pytest.raises(requests.Timeout):
            pr_agent.create_pr(
                branch_name="feature/test",
                base_branch="main",
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=moai_flow.github.pr_agent", "--cov-report=term-missing"])
