"""GitHub Issue Agent for automated issue creation and management.

This module provides automated issue creation from task failures, automatic triage,
context enrichment, and similarity detection.

Example:
    >>> agent = GitHubIssueAgent("owner", "repo", token)
    >>> issue_number = agent.create_issue_from_failure(
    ...     task_id="task-001",
    ...     agent_id="agent-backend",
    ...     error=TimeoutError("API timeout"),
    ...     context={"env": "production"},
    ...     spec_id="SPEC-001"
    ... )
    >>> print(f"Created issue #{issue_number}")
"""

import os
import sys
import traceback
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import re

# GitHub API imports
try:
    from github import Github, GithubException, Auth
    from github.Issue import Issue
    from github.Repository import Repository
except ImportError:
    Github = None
    GithubException = Exception
    Auth = None
    Issue = None
    Repository = None

from .triage import IssueTriage, IssueMetadata, IssuePriority

logger = logging.getLogger(__name__)


class GitHubIssueAgent:
    """GitHub Issue automation agent.

    Handles automated issue creation from task failures, auto-triage,
    context enrichment, SPEC linking, and similar issue detection.

    Attributes:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        github_token: GitHub API authentication token
        github_client: PyGithub client instance
        repo: GitHub repository object
        triage: Issue triage system
    """

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: Optional[str] = None,
    ):
        """Initialize GitHub Issue Agent.

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

        # Initialize triage system
        self.triage = IssueTriage()

        logger.info(f"Initialized GitHub Issue Agent for {repo_owner}/{repo_name}")

    def create_issue_from_failure(
        self,
        task_id: str,
        agent_id: str,
        error: Exception,
        context: Dict[str, Any],
        spec_id: Optional[str] = None,
    ) -> int:
        """Create GitHub issue from task failure.

        Automatically creates a detailed issue with:
        - Error type and message
        - Stack trace with syntax highlighting
        - Environment information (sanitized)
        - Recent git commits
        - Related SPEC link (if provided)
        - Auto-generated labels and priority

        Args:
            task_id: Failed task ID
            agent_id: Agent that encountered the failure
            error: Exception that was raised
            context: Task context and metadata
            spec_id: Related SPEC ID (e.g., "SPEC-001")

        Returns:
            Issue number of created issue

        Raises:
            GithubException: If issue creation fails
        """
        try:
            # Auto-triage to get metadata
            metadata = self.auto_triage(error, context)

            # Enhance context
            enhanced_context = self._enhance_context(context, task_id, agent_id, spec_id)

            # Load issue template
            template = self._load_issue_template("error_report")

            # Format error information
            error_type = type(error).__name__
            error_message = str(error)
            stack_trace = self._format_stack_trace(error)
            environment = self._format_environment(enhanced_context)
            recent_changes = self._get_recent_commits(limit=5)

            # Generate issue body from template
            body = template
            body = body.replace("{{TASK_ID}}", task_id)
            body = body.replace("{{AGENT_ID}}", agent_id)
            body = body.replace("{{TIMESTAMP}}", datetime.now().isoformat())
            body = body.replace("{{ERROR_TYPE}}", error_type)
            body = body.replace("{{ERROR_MESSAGE}}", error_message)
            body = body.replace("{{STACK_TRACE}}", stack_trace)
            body = body.replace("{{ENVIRONMENT}}", environment)
            body = body.replace("{{RECENT_COMMITS}}", recent_changes)
            body = body.replace("{{SPEC_LINK}}", self._generate_spec_link(spec_id) if spec_id else "N/A")

            # Create issue
            issue = self.repo.create_issue(
                title=metadata.title,
                body=body,
                labels=metadata.labels,
                assignees=metadata.assignees,
            )

            logger.info(f"Created issue #{issue.number} for task failure: {task_id}")

            # Link to SPEC if provided
            if spec_id:
                self.link_to_spec(issue.number, spec_id)

            # Add context as comment
            if enhanced_context:
                context_comment = self._format_context_comment(enhanced_context)
                issue.create_comment(context_comment)

            return issue.number

        except GithubException as e:
            logger.error(f"Failed to create issue: {str(e)}")
            raise

    def auto_triage(
        self, error: Exception, context: Dict[str, Any]
    ) -> IssueMetadata:
        """Automatically triage issue based on error type and context.

        Uses IssueTriage system to analyze error and context, then assigns:
        - Appropriate labels (by error type, component, environment)
        - Priority level (CRITICAL, HIGH, MEDIUM, LOW)
        - Suggested assignees (by component ownership)

        Args:
            error: Exception that triggered issue
            context: Additional context for classification

        Returns:
            IssueMetadata with labels, priority, assignees
        """
        return self.triage.classify(error, context)

    def add_context(
        self,
        issue_number: int,
        stack_trace: Optional[str] = None,
        environment: Optional[Dict[str, Any]] = None,
        recent_changes: Optional[List[str]] = None,
    ) -> None:
        """Add detailed context to existing issue.

        Adds a formatted comment with additional debugging information:
        - Stack trace (syntax highlighted)
        - Environment variables (sanitized, no secrets)
        - Recent git commits
        - Related files and line numbers

        Args:
            issue_number: GitHub issue number
            stack_trace: Stack trace string
            environment: Environment variables and system info
            recent_changes: List of recent commit SHAs or messages

        Raises:
            GithubException: If comment creation fails
        """
        try:
            issue = self.repo.get_issue(issue_number)

            # Build context comment
            context_parts = ["## Additional Context\n"]

            if stack_trace:
                context_parts.append("### Stack Trace\n")
                context_parts.append("```python")
                context_parts.append(stack_trace)
                context_parts.append("```\n")

            if environment:
                context_parts.append("### Environment\n")
                for key, value in environment.items():
                    # Sanitize secrets
                    if any(secret in key.lower() for secret in ["token", "key", "secret", "password"]):
                        value = "***REDACTED***"
                    context_parts.append(f"- **{key}**: {value}")
                context_parts.append("\n")

            if recent_changes:
                context_parts.append("### Recent Changes\n")
                for change in recent_changes:
                    context_parts.append(f"- {change}")
                context_parts.append("\n")

            comment_body = "\n".join(context_parts)
            issue.create_comment(comment_body)

            logger.info(f"Added context to issue #{issue_number}")

        except GithubException as e:
            logger.error(f"Failed to add context to issue #{issue_number}: {str(e)}")
            raise

    def link_to_spec(self, issue_number: int, spec_id: str) -> None:
        """Link issue to SPEC document.

        Creates a bidirectional link between the issue and SPEC:
        - Adds SPEC reference to issue description
        - Adds issue link to SPEC (if SPEC file exists)

        Args:
            issue_number: GitHub issue number
            spec_id: SPEC ID (e.g., "SPEC-001")

        Raises:
            GithubException: If issue update fails
        """
        try:
            issue = self.repo.get_issue(issue_number)

            # Add SPEC link as comment
            spec_link = self._generate_spec_link(spec_id)
            spec_comment = f"""## Related SPEC

This issue is related to {spec_link}

**SPEC ID**: {spec_id}
"""
            issue.create_comment(spec_comment)

            # Add SPEC label
            issue.add_to_labels(f"spec:{spec_id.lower()}")

            logger.info(f"Linked issue #{issue_number} to {spec_id}")

            # TODO: Add issue link to SPEC file (if exists)
            self._add_issue_to_spec_file(spec_id, issue_number)

        except GithubException as e:
            logger.error(f"Failed to link issue #{issue_number} to {spec_id}: {str(e)}")
            raise

    def update_priority(
        self, issue_number: int, priority: IssuePriority, reason: str
    ) -> None:
        """Update issue priority with justification.

        Updates priority label and adds a comment explaining the change.

        Args:
            issue_number: GitHub issue number
            priority: New priority level
            reason: Justification for priority change

        Raises:
            GithubException: If issue update fails
        """
        try:
            issue = self.repo.get_issue(issue_number)

            # Remove old priority labels
            current_labels = [label.name for label in issue.labels]
            priority_labels = [
                "priority:critical",
                "priority:high",
                "priority:medium",
                "priority:low",
            ]

            for old_label in priority_labels:
                if old_label in current_labels:
                    issue.remove_from_labels(old_label)

            # Add new priority label
            new_label = f"priority:{priority.value}"
            issue.add_to_labels(new_label)

            # Add comment explaining change
            priority_comment = f"""## Priority Update

**New Priority**: {priority.value.upper()}

**Reason**: {reason}

**Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            issue.create_comment(priority_comment)

            logger.info(f"Updated issue #{issue_number} priority to {priority.value}")

        except GithubException as e:
            logger.error(f"Failed to update priority for issue #{issue_number}: {str(e)}")
            raise

    def get_similar_issues(
        self, error: Exception, limit: int = 5
    ) -> List[int]:
        """Find similar existing issues based on error pattern.

        Searches for issues with similar:
        - Error type
        - Error message patterns
        - Affected components
        - Labels

        Args:
            error: Exception to search for
            limit: Maximum number of similar issues to return

        Returns:
            List of similar issue numbers (most similar first)
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)

            # Build search query
            # Search for issues with same error type in title or body
            query_parts = [
                f"repo:{self.repo_owner}/{self.repo_name}",
                f'"{error_type}"',
                "is:issue",
            ]

            # Add key terms from error message
            key_terms = self._extract_key_terms(error_message)
            if key_terms:
                query_parts.append(f'"{key_terms[0]}"')

            search_query = " ".join(query_parts)

            # Search GitHub
            issues = self.github_client.search_issues(
                query=search_query, sort="created", order="desc"
            )

            # Get top N similar issues
            similar_issues = []
            for issue in issues[:limit]:
                similar_issues.append(issue.number)

            logger.info(f"Found {len(similar_issues)} similar issues for {error_type}")
            return similar_issues

        except Exception as e:
            logger.warning(f"Failed to search for similar issues: {str(e)}")
            return []

    # Private helper methods

    def _enhance_context(
        self,
        context: Dict[str, Any],
        task_id: str,
        agent_id: str,
        spec_id: Optional[str],
    ) -> Dict[str, Any]:
        """Enhance context with additional metadata.

        Args:
            context: Original context
            task_id: Task ID
            agent_id: Agent ID
            spec_id: SPEC ID

        Returns:
            Enhanced context dictionary
        """
        enhanced = context.copy()
        enhanced["task_id"] = task_id
        enhanced["agent_id"] = agent_id
        if spec_id:
            enhanced["spec_id"] = spec_id
        enhanced["timestamp"] = datetime.now().isoformat()

        # Add system information if not present
        if "python_version" not in enhanced:
            enhanced["python_version"] = sys.version.split()[0]
        if "platform" not in enhanced:
            enhanced["platform"] = platform.platform()

        return enhanced

    def _format_stack_trace(self, error: Exception) -> str:
        """Format stack trace with syntax highlighting.

        Args:
            error: Exception object

        Returns:
            Formatted stack trace string
        """
        if hasattr(error, "__traceback__"):
            tb_lines = traceback.format_exception(
                type(error), error, error.__traceback__
            )
            return "".join(tb_lines)
        else:
            return str(error)

    def _format_environment(self, context: Dict[str, Any]) -> str:
        """Format environment variables and system info.

        Args:
            context: Context with environment data

        Returns:
            Formatted environment string
        """
        env_parts = []

        # Python version
        python_version = context.get("python_version", sys.version.split()[0])
        env_parts.append(f"- **Python**: {python_version}")

        # OS info
        platform_info = context.get("platform", platform.platform())
        env_parts.append(f"- **OS**: {platform_info}")

        # MoAI-Flow version (if available)
        if "moai_version" in context:
            env_parts.append(f"- **MoAI-Flow**: {context['moai_version']}")

        # Environment type
        if "environment" in context:
            env_parts.append(f"- **Environment**: {context['environment']}")

        # Component
        if "component" in context:
            env_parts.append(f"- **Component**: {context['component']}")

        return "\n".join(env_parts)

    def _get_recent_commits(self, limit: int = 5) -> str:
        """Get recent commits from repository.

        Args:
            limit: Number of commits to retrieve

        Returns:
            Formatted commit list
        """
        try:
            commits = self.repo.get_commits()[:limit]
            commit_lines = []

            for commit in commits:
                sha_short = commit.sha[:7]
                message = commit.commit.message.split("\n")[0]  # First line only
                commit_lines.append(f"- `{sha_short}` {message}")

            return "\n".join(commit_lines) if commit_lines else "No recent commits"

        except Exception as e:
            logger.warning(f"Failed to get recent commits: {str(e)}")
            return "Unable to retrieve commit history"

    def _generate_spec_link(self, spec_id: str) -> str:
        """Generate markdown link to SPEC.

        Args:
            spec_id: SPEC ID

        Returns:
            Markdown link to SPEC
        """
        # Assuming SPEC is in .moai/specs/SPEC-ID/spec.md
        spec_path = f".moai/specs/{spec_id}/spec.md"
        return f"[{spec_id}]({spec_path})"

    def _add_issue_to_spec_file(self, spec_id: str, issue_number: int) -> None:
        """Add issue link to SPEC file (if it exists).

        Args:
            spec_id: SPEC ID
            issue_number: Issue number
        """
        try:
            spec_path = Path(f".moai/specs/{spec_id}/spec.md")
            if not spec_path.exists():
                logger.warning(f"SPEC file not found: {spec_path}")
                return

            content = spec_path.read_text()

            # Check if Issues section exists
            if "## Related Issues" not in content:
                # Add Issues section at the end
                issue_link = f"- #{issue_number}"
                content += f"\n\n## Related Issues\n\n{issue_link}\n"
            else:
                # Add to existing section
                issue_link = f"- #{issue_number}"
                content = content.replace(
                    "## Related Issues",
                    f"## Related Issues\n\n{issue_link}",
                )

            spec_path.write_text(content)
            logger.info(f"Added issue #{issue_number} to {spec_id}")

        except Exception as e:
            logger.warning(f"Failed to add issue to SPEC file: {str(e)}")

    def _load_issue_template(self, template_name: str) -> str:
        """Load issue template from file.

        Args:
            template_name: Template name (e.g., "error_report")

        Returns:
            Template content
        """
        # Try MoAI Flow custom template
        template_path = Path(__file__).parent / "templates" / f"issue_{template_name}.md"
        if template_path.exists():
            return template_path.read_text()

        # Fallback to default template
        return self._get_default_error_template()

    def _get_default_error_template(self) -> str:
        """Get default error report template.

        Returns:
            Default template string
        """
        return """## Error Report

**Task ID**: {{TASK_ID}}
**Agent ID**: {{AGENT_ID}}
**Timestamp**: {{TIMESTAMP}}

## Error

```
{{ERROR_TYPE}}: {{ERROR_MESSAGE}}
```

## Stack Trace

```python
{{STACK_TRACE}}
```

## Environment

{{ENVIRONMENT}}

## Recent Changes

{{RECENT_COMMITS}}

## Related SPEC

{{SPEC_LINK}}

## Steps to Reproduce

1. <!-- Add steps to reproduce -->

## Expected Behavior

<!-- Describe expected behavior -->

## Actual Behavior

<!-- Describe actual behavior -->
"""

    def _format_context_comment(self, context: Dict[str, Any]) -> str:
        """Format context as a comment.

        Args:
            context: Context dictionary

        Returns:
            Formatted comment string
        """
        lines = ["## Task Context\n"]

        for key, value in context.items():
            if key not in ["stack_trace", "environment_vars"]:
                lines.append(f"- **{key}**: {value}")

        return "\n".join(lines)

    def _extract_key_terms(self, text: str, max_terms: int = 3) -> List[str]:
        """Extract key terms from error message for search.

        Args:
            text: Error message
            max_terms: Maximum terms to extract

        Returns:
            List of key terms
        """
        # Remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "is",
            "was",
            "are",
            "were",
        }

        # Split and filter
        words = re.findall(r"\b\w+\b", text.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 3]

        return key_terms[:max_terms]
