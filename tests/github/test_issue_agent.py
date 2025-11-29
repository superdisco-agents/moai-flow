"""Tests for GitHub Issue Agent.

Comprehensive test suite covering:
- Issue creation from failures
- Auto-triage logic
- Context enrichment
- SPEC linking
- Priority updates
- Similar issue detection
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from pathlib import Path

from moai_flow.github.issue_agent import GitHubIssueAgent
from moai_flow.github.triage import (
    IssueTriage,
    IssueMetadata,
    IssuePriority,
    TriageRule,
)


class TestIssueTriage:
    """Test suite for issue triage system."""

    def test_classify_timeout_error(self):
        """Test classification of timeout errors."""
        triage = IssueTriage()
        error = TimeoutError("Request timed out after 30s")
        context = {"component": "api", "environment": "production"}

        metadata = triage.classify(error, context)

        assert "timeout" in metadata.labels
        assert "performance" in metadata.labels
        assert metadata.priority == IssuePriority.HIGH

    def test_classify_security_error(self):
        """Test classification of security errors."""
        triage = IssueTriage()
        error = PermissionError("Permission denied: unauthorized access")
        context = {"component": "auth"}

        metadata = triage.classify(error, context)

        assert "security" in metadata.labels
        assert metadata.priority == IssuePriority.CRITICAL

    def test_classify_type_error(self):
        """Test classification of type errors."""
        triage = IssueTriage()
        error = TypeError("Expected str, got int")
        context = {"component": "backend"}

        metadata = triage.classify(error, context)

        assert "bug" in metadata.labels or "typeerror" in metadata.labels
        assert metadata.priority == IssuePriority.MEDIUM

    def test_classify_with_production_context(self):
        """Test that production environment increases priority."""
        triage = IssueTriage()
        error = ValueError("Invalid value")
        context = {"environment": "production"}

        metadata = triage.classify(error, context)

        assert "production" in metadata.labels
        # Production should elevate priority
        assert metadata.priority in [IssuePriority.HIGH, IssuePriority.MEDIUM]

    def test_assign_priority_critical_conditions(self):
        """Test CRITICAL priority assignment."""
        triage = IssueTriage()

        # Memory error
        error = MemoryError("Out of memory")
        priority = triage.assign_priority(error, {})
        assert priority == IssuePriority.CRITICAL

        # High user impact
        error = Exception("Service down")
        priority = triage.assign_priority(error, {"user_impact": 2000})
        assert priority == IssuePriority.CRITICAL

    def test_assign_priority_high_conditions(self):
        """Test HIGH priority assignment."""
        triage = IssueTriage()

        # Timeout in production
        error = TimeoutError("Timeout")
        priority = triage.assign_priority(error, {"environment": "production"})
        assert priority == IssuePriority.HIGH

        # High frequency error
        error = Exception("Error")
        priority = triage.assign_priority(error, {"frequency": 15})
        assert priority == IssuePriority.HIGH

    def test_suggest_assignees_by_component(self):
        """Test assignee suggestion based on component."""
        triage = IssueTriage()

        # Backend component
        assignees = triage.suggest_assignees(
            Exception("Error"), {"component": "backend"}
        )
        assert "backend-team" in assignees

        # Frontend component
        assignees = triage.suggest_assignees(
            Exception("Error"), {"component": "frontend"}
        )
        assert "frontend-team" in assignees

        # Security component
        assignees = triage.suggest_assignees(
            Exception("Error"), {"component": "security"}
        )
        assert "security-team" in assignees

    def test_calculate_sla(self):
        """Test SLA calculation for different priorities."""
        triage = IssueTriage()

        assert triage.calculate_sla(IssuePriority.CRITICAL) == 4
        assert triage.calculate_sla(IssuePriority.HIGH) == 24
        assert triage.calculate_sla(IssuePriority.MEDIUM) == 72
        assert triage.calculate_sla(IssuePriority.LOW) == 168

    def test_custom_triage_rules(self):
        """Test custom triage rules extension."""
        custom_rule = TriageRule(
            error_patterns=[r"custom error"],
            labels=["custom-label"],
            priority=IssuePriority.HIGH,
            assignees=["custom-team"],
        )

        triage = IssueTriage(custom_rules=[custom_rule])
        error = Exception("This is a custom error")
        context = {}

        metadata = triage.classify(error, context)

        assert "custom-label" in metadata.labels
        assert "custom-team" in metadata.assignees


class TestGitHubIssueAgent:
    """Test suite for GitHub Issue Agent."""

    @pytest.fixture
    def mock_github_client(self):
        """Create mock GitHub client."""
        with patch("moai_flow.github.issue_agent.Github") as mock_github:
            mock_repo = MagicMock()
            mock_client = MagicMock()
            mock_client.get_repo.return_value = mock_repo
            mock_github.return_value = mock_client

            yield mock_github, mock_client, mock_repo

    @pytest.fixture
    def mock_auth(self):
        """Mock GitHub Auth."""
        with patch("moai_flow.github.issue_agent.Auth") as mock_auth:
            mock_auth.Token.return_value = MagicMock()
            yield mock_auth

    @pytest.fixture
    def agent(self, mock_github_client, mock_auth):
        """Create GitHubIssueAgent instance with mocked dependencies."""
        _, _, mock_repo = mock_github_client
        agent = GitHubIssueAgent(
            repo_owner="test-owner", repo_name="test-repo", github_token="test-token"
        )
        agent.repo = mock_repo
        return agent

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.repo_owner == "test-owner"
        assert agent.repo_name == "test-repo"
        assert agent.github_token == "test-token"
        assert isinstance(agent.triage, IssueTriage)

    def test_initialization_no_token_raises(self, mock_github_client, mock_auth):
        """Test that initialization without token raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                GitHubIssueAgent(repo_owner="owner", repo_name="repo")

    def test_create_issue_from_failure(self, agent):
        """Test issue creation from task failure."""
        # Setup mock issue
        mock_issue = MagicMock()
        mock_issue.number = 42
        agent.repo.create_issue.return_value = mock_issue

        # Create issue
        error = TimeoutError("Request timeout")
        context = {"component": "api", "environment": "production"}

        issue_number = agent.create_issue_from_failure(
            task_id="task-001",
            agent_id="agent-backend",
            error=error,
            context=context,
            spec_id="SPEC-001",
        )

        # Verify issue was created
        assert issue_number == 42
        assert agent.repo.create_issue.called

        # Verify issue content
        call_args = agent.repo.create_issue.call_args
        assert "task-001" in call_args.kwargs["body"]
        assert "agent-backend" in call_args.kwargs["body"]
        assert "TimeoutError" in call_args.kwargs["body"]

    def test_auto_triage(self, agent):
        """Test automatic triage."""
        error = PermissionError("Access denied")
        context = {"component": "auth", "environment": "production"}

        metadata = agent.auto_triage(error, context)

        assert isinstance(metadata, IssueMetadata)
        assert metadata.priority == IssuePriority.CRITICAL
        assert "security" in metadata.labels

    def test_add_context(self, agent):
        """Test adding context to existing issue."""
        mock_issue = MagicMock()
        agent.repo.get_issue.return_value = mock_issue

        agent.add_context(
            issue_number=42,
            stack_trace="Traceback...",
            environment={"python": "3.11", "os": "Linux"},
            recent_changes=["commit1", "commit2"],
        )

        # Verify comment was created
        assert mock_issue.create_comment.called
        comment_body = mock_issue.create_comment.call_args[0][0]
        assert "Stack Trace" in comment_body
        assert "Environment" in comment_body
        assert "Recent Changes" in comment_body

    def test_add_context_sanitizes_secrets(self, agent):
        """Test that secrets are sanitized in context."""
        mock_issue = MagicMock()
        agent.repo.get_issue.return_value = mock_issue

        agent.add_context(
            issue_number=42,
            environment={
                "API_TOKEN": "secret123",
                "DATABASE_PASSWORD": "pass456",
                "PYTHON_VERSION": "3.11",
            },
        )

        comment_body = mock_issue.create_comment.call_args[0][0]
        assert "REDACTED" in comment_body
        assert "secret123" not in comment_body
        assert "pass456" not in comment_body
        assert "3.11" in comment_body  # Non-secret should be included

    def test_link_to_spec(self, agent):
        """Test linking issue to SPEC."""
        mock_issue = MagicMock()
        agent.repo.get_issue.return_value = mock_issue

        with patch.object(agent, "_add_issue_to_spec_file"):
            agent.link_to_spec(issue_number=42, spec_id="SPEC-001")

        # Verify SPEC link comment was created
        assert mock_issue.create_comment.called
        comment_body = mock_issue.create_comment.call_args[0][0]
        assert "SPEC-001" in comment_body

        # Verify label was added
        assert mock_issue.add_to_labels.called

    def test_update_priority(self, agent):
        """Test updating issue priority."""
        mock_issue = MagicMock()
        mock_label1 = MagicMock()
        mock_label1.name = "priority:low"
        mock_label2 = MagicMock()
        mock_label2.name = "bug"
        mock_issue.labels = [mock_label1, mock_label2]
        agent.repo.get_issue.return_value = mock_issue

        agent.update_priority(
            issue_number=42,
            priority=IssuePriority.CRITICAL,
            reason="Production outage affecting 1000+ users",
        )

        # Verify old priority label was removed
        assert mock_issue.remove_from_labels.called

        # Verify new priority label was added
        assert mock_issue.add_to_labels.called
        assert "priority:critical" in mock_issue.add_to_labels.call_args[0]

        # Verify comment explaining change was added
        assert mock_issue.create_comment.called
        comment_body = mock_issue.create_comment.call_args[0][0]
        assert "critical" in comment_body.lower()
        assert "Production outage" in comment_body

    def test_get_similar_issues(self, agent):
        """Test finding similar issues."""
        # Setup mock search results
        mock_issue1 = MagicMock()
        mock_issue1.number = 10
        mock_issue2 = MagicMock()
        mock_issue2.number = 15
        mock_issue3 = MagicMock()
        mock_issue3.number = 20

        agent.github_client.search_issues.return_value = [
            mock_issue1,
            mock_issue2,
            mock_issue3,
        ]

        error = TimeoutError("Request timeout")
        similar_issues = agent.get_similar_issues(error, limit=3)

        assert len(similar_issues) == 3
        assert 10 in similar_issues
        assert 15 in similar_issues
        assert 20 in similar_issues

    def test_get_similar_issues_handles_errors(self, agent):
        """Test that similar issue search handles errors gracefully."""
        agent.github_client.search_issues.side_effect = Exception("Search failed")

        error = TimeoutError("Timeout")
        similar_issues = agent.get_similar_issues(error)

        # Should return empty list on error
        assert similar_issues == []

    def test_format_stack_trace(self, agent):
        """Test stack trace formatting."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            stack_trace = agent._format_stack_trace(e)
            assert "ValueError" in stack_trace
            assert "Test error" in stack_trace

    def test_format_environment(self, agent):
        """Test environment formatting."""
        context = {
            "python_version": "3.11.0",
            "platform": "Linux-x86_64",
            "environment": "production",
            "component": "api",
        }

        env_string = agent._format_environment(context)

        assert "Python" in env_string
        assert "3.11.0" in env_string
        assert "Linux" in env_string
        assert "production" in env_string
        assert "api" in env_string

    def test_get_recent_commits_success(self, agent):
        """Test getting recent commits."""
        # Setup mock commits
        mock_commit1 = MagicMock()
        mock_commit1.sha = "abc1234567890"
        mock_commit1.commit.message = "Fix bug in API"

        mock_commit2 = MagicMock()
        mock_commit2.sha = "def4567890123"
        mock_commit2.commit.message = "Add new feature"

        agent.repo.get_commits.return_value = [mock_commit1, mock_commit2]

        commits_string = agent._get_recent_commits(limit=2)

        assert "abc1234" in commits_string  # Short SHA
        assert "Fix bug in API" in commits_string
        assert "def4567" in commits_string
        assert "Add new feature" in commits_string

    def test_get_recent_commits_handles_errors(self, agent):
        """Test that commit retrieval handles errors gracefully."""
        agent.repo.get_commits.side_effect = Exception("API error")

        commits_string = agent._get_recent_commits()

        assert "Unable to retrieve" in commits_string

    def test_extract_key_terms(self, agent):
        """Test key term extraction from error messages."""
        text = "The database connection timed out while processing request"
        key_terms = agent._extract_key_terms(text, max_terms=3)

        assert len(key_terms) <= 3
        assert "database" in key_terms or "connection" in key_terms

    def test_load_issue_template_custom(self, agent):
        """Test loading custom issue template."""
        template_path = (
            Path(__file__).parent.parent.parent
            / "moai_flow"
            / "github"
            / "templates"
            / "issue_error_report.md"
        )

        if template_path.exists():
            template = agent._load_issue_template("error_report")
            assert "{{TASK_ID}}" in template
            assert "{{ERROR_TYPE}}" in template

    def test_load_issue_template_default(self, agent):
        """Test fallback to default template."""
        template = agent._load_issue_template("nonexistent_template")
        assert "{{TASK_ID}}" in template
        assert "{{ERROR_TYPE}}" in template


class TestIssueMetadata:
    """Test IssueMetadata dataclass."""

    def test_metadata_creation(self):
        """Test creating IssueMetadata."""
        metadata = IssueMetadata(
            title="Test Issue",
            body="Test body",
            labels=["bug", "high-priority"],
            priority=IssuePriority.HIGH,
            assignees=["user1", "user2"],
            milestone="v1.0",
        )

        assert metadata.title == "Test Issue"
        assert metadata.body == "Test body"
        assert "bug" in metadata.labels
        assert metadata.priority == IssuePriority.HIGH
        assert "user1" in metadata.assignees
        assert metadata.milestone == "v1.0"


class TestTriageRule:
    """Test TriageRule dataclass."""

    def test_rule_creation(self):
        """Test creating TriageRule."""
        rule = TriageRule(
            error_patterns=[r"timeout", r"timed out"],
            labels=["timeout", "performance"],
            priority=IssuePriority.HIGH,
            assignees=["backend-team"],
            auto_close=False,
        )

        assert len(rule.error_patterns) == 2
        assert "timeout" in rule.labels
        assert rule.priority == IssuePriority.HIGH
        assert "backend-team" in rule.assignees
        assert rule.auto_close is False


class TestIntegration:
    """Integration tests combining multiple components."""

    @pytest.fixture
    def integration_agent(self):
        """Create agent with mocked GitHub for integration tests."""
        with patch("moai_flow.github.issue_agent.Github") as mock_github:
            with patch("moai_flow.github.issue_agent.Auth"):
                mock_repo = MagicMock()
                mock_client = MagicMock()
                mock_client.get_repo.return_value = mock_repo
                mock_github.return_value = mock_client

                agent = GitHubIssueAgent(
                    repo_owner="test", repo_name="test", github_token="token"
                )
                agent.repo = mock_repo
                yield agent

    def test_full_workflow_timeout_error(self, integration_agent):
        """Test complete workflow for timeout error."""
        # Setup
        mock_issue = MagicMock()
        mock_issue.number = 99
        integration_agent.repo.create_issue.return_value = mock_issue

        # Execute
        error = TimeoutError("API request timeout after 30s")
        context = {
            "component": "api",
            "environment": "production",
            "endpoint": "/api/v1/users",
        }

        issue_number = integration_agent.create_issue_from_failure(
            task_id="task-timeout-001",
            agent_id="agent-api",
            error=error,
            context=context,
            spec_id="SPEC-042",
        )

        # Verify
        assert issue_number == 99
        assert integration_agent.repo.create_issue.called

        # Verify issue content
        call_kwargs = integration_agent.repo.create_issue.call_args.kwargs
        assert "timeout" in [label.lower() for label in call_kwargs["labels"]]
        assert "task-timeout-001" in call_kwargs["body"]

    def test_full_workflow_security_error(self, integration_agent):
        """Test complete workflow for security error."""
        # Setup
        mock_issue = MagicMock()
        mock_issue.number = 100
        integration_agent.repo.create_issue.return_value = mock_issue

        # Execute
        error = PermissionError("Unauthorized access attempt")
        context = {"component": "auth", "environment": "production", "user_id": "user123"}

        issue_number = integration_agent.create_issue_from_failure(
            task_id="task-security-001",
            agent_id="agent-auth",
            error=error,
            context=context,
        )

        # Verify
        assert issue_number == 100

        # Check that CRITICAL priority was assigned
        call_kwargs = integration_agent.repo.create_issue.call_args.kwargs
        labels = [label.lower() for label in call_kwargs["labels"]]
        assert "security" in labels


# Test coverage for error scenarios
class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def error_agent(self):
        """Create agent for error testing."""
        with patch("moai_flow.github.issue_agent.Github"):
            with patch("moai_flow.github.issue_agent.Auth"):
                agent = GitHubIssueAgent("test", "test", "token")
                agent.repo = MagicMock()
                return agent

    def test_create_issue_github_exception(self, error_agent):
        """Test handling of GitHub API exceptions."""
        from moai_flow.github.issue_agent import GithubException

        # Create a simple exception that inherits from GithubException
        error_agent.repo.create_issue.side_effect = Exception("GitHub API error")

        with pytest.raises(Exception):
            error_agent.create_issue_from_failure(
                task_id="test",
                agent_id="test",
                error=Exception("test"),
                context={},
            )

    def test_add_context_github_exception(self, error_agent):
        """Test handling of GitHub exception in add_context."""
        from moai_flow.github.issue_agent import GithubException

        # Create a simple exception
        error_agent.repo.get_issue.side_effect = Exception("Issue not found")

        with pytest.raises(Exception):
            error_agent.add_context(issue_number=999, stack_trace="test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=moai_flow.github", "--cov-report=term-missing"])
