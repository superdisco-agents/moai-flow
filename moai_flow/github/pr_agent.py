"""GitHub Pull Request Agent for automated PR creation and management.

This module provides automated PR creation from branches with:
- Auto-generated descriptions from SPEC
- Metadata management (labels, reviewers, assignees)
- Draft/ready status toggling
- Comment management
- Review requests

Example:
    >>> agent = GitHubPRAgent("owner", "repo", token)
    >>> pr_number = agent.create_pr(
    ...     branch_name="feature/SPEC-001",
    ...     base_branch="main",
    ...     spec_id="SPEC-001"
    ... )
    >>> agent.set_metadata(pr_number, labels=["enhancement"], reviewers=["reviewer1"])
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

# GitHub API imports - using PyGithub
try:
    from github import Github, GithubException, Auth
    from github.PullRequest import PullRequest
    from github.Repository import Repository
except ImportError:
    # Fallback for when PyGithub is not installed
    Github = None
    GithubException = Exception
    Auth = None
    PullRequest = None
    Repository = None

logger = logging.getLogger(__name__)


@dataclass
class PRMetadata:
    """Metadata for a pull request."""

    title: str
    description: str
    labels: List[str]
    reviewers: List[str]
    assignees: List[str]
    is_draft: bool = False


@dataclass
class FileChange:
    """Represents a file change in a PR."""

    path: str
    additions: int
    deletions: int
    change_type: str  # 'added', 'modified', 'removed'


class GitHubPRAgent:
    """GitHub Pull Request automation agent.

    Handles automated PR creation, description generation, metadata management,
    and review workflows.

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
        """Initialize GitHub PR Agent.

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

        logger.info(f"Initialized GitHub PR Agent for {repo_owner}/{repo_name}")

    def create_pr(
        self,
        branch_name: str,
        base_branch: str = "main",
        spec_id: Optional[str] = None,
        title: Optional[str] = None,
        auto_labels: bool = True,
        is_draft: bool = False,
    ) -> int:
        """Create a pull request from a branch.

        Args:
            branch_name: Source branch name
            base_branch: Target branch name (default: main)
            spec_id: SPEC ID for description generation (e.g., "SPEC-001")
            title: Custom PR title (auto-generated if not provided)
            auto_labels: Automatically assign labels based on changes
            is_draft: Create as draft PR

        Returns:
            PR number of created pull request

        Raises:
            GithubException: If PR creation fails
            ValueError: If branch doesn't exist or has no changes
        """
        try:
            # Verify branches exist
            try:
                self.repo.get_branch(branch_name)
                self.repo.get_branch(base_branch)
            except GithubException as e:
                raise ValueError(f"Branch not found: {str(e)}")

            # Get file changes
            comparison = self.repo.compare(base_branch, branch_name)
            if comparison.total_commits == 0:
                raise ValueError(f"No changes between {base_branch} and {branch_name}")

            file_changes = self._extract_file_changes(comparison)

            # Generate description
            description = self.generate_description(spec_id, file_changes)

            # Generate title if not provided
            if not title:
                title = self._generate_title(spec_id, file_changes)

            # Create PR
            pr = self.repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=base_branch,
                draft=is_draft,
            )

            logger.info(f"Created PR #{pr.number}: {title}")

            # Auto-assign labels if enabled
            if auto_labels:
                labels = self._determine_labels(file_changes)
                if labels:
                    pr.add_to_labels(*labels)
                    logger.info(f"Added labels to PR #{pr.number}: {labels}")

            return pr.number

        except GithubException as e:
            logger.error(f"Failed to create PR: {str(e)}")
            raise

    def generate_description(
        self,
        spec_id: Optional[str],
        file_changes: List[FileChange],
    ) -> str:
        """Generate PR description from SPEC and file changes.

        Args:
            spec_id: SPEC ID (e.g., "SPEC-001")
            file_changes: List of file changes

        Returns:
            Formatted PR description in markdown
        """
        # Load PR template
        template = self._load_pr_template()

        # Extract SPEC summary if available
        spec_summary = ""
        breaking_changes = ""
        deployment_notes = ""

        if spec_id:
            spec_data = self._read_spec_file(spec_id)
            if spec_data:
                spec_summary = spec_data.get("summary", "")
                breaking_changes = spec_data.get("breaking_changes", "")
                deployment_notes = spec_data.get("deployment_notes", "")

        # Generate file changes summary
        changes_summary = self._format_file_changes(file_changes)

        # Generate test plan
        test_plan = self._generate_test_plan(file_changes)

        # Replace template variables
        description = template
        description = description.replace("{{SPEC_ID}}", spec_id or "N/A")
        description = description.replace("{{SUMMARY}}", spec_summary)
        description = description.replace("{{CHANGES}}", changes_summary)
        description = description.replace("{{TEST_PLAN}}", test_plan)
        description = description.replace("{{BREAKING_CHANGES}}", breaking_changes or "None")
        description = description.replace("{{DEPLOYMENT_NOTES}}", deployment_notes or "None")

        return description

    def set_metadata(
        self,
        pr_number: int,
        labels: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> None:
        """Set PR metadata (labels, reviewers, assignees).

        Args:
            pr_number: Pull request number
            labels: List of label names to add
            reviewers: List of reviewer usernames
            assignees: List of assignee usernames

        Raises:
            GithubException: If metadata update fails
        """
        try:
            pr = self.repo.get_pull(pr_number)

            # Add labels
            if labels:
                pr.add_to_labels(*labels)
                logger.info(f"Added labels to PR #{pr_number}: {labels}")

            # Request reviewers
            if reviewers:
                pr.create_review_request(reviewers=reviewers)
                logger.info(f"Requested reviews from: {reviewers}")

            # Add assignees
            if assignees:
                pr.add_to_assignees(*assignees)
                logger.info(f"Assigned PR #{pr_number} to: {assignees}")

        except GithubException as e:
            logger.error(f"Failed to set metadata for PR #{pr_number}: {str(e)}")
            raise

    def update_status(self, pr_number: int, is_draft: bool) -> None:
        """Toggle PR between draft and ready status.

        Args:
            pr_number: Pull request number
            is_draft: True for draft, False for ready

        Raises:
            GithubException: If status update fails
        """
        try:
            pr = self.repo.get_pull(pr_number)

            # Note: PyGithub doesn't have direct draft toggle
            # We'll use GraphQL mutation for this
            mutation = """
            mutation($pullRequestId: ID!, $isDraft: Boolean!) {
                convertPullRequestToDraft(input: {pullRequestId: $pullRequestId}) {
                    pullRequest { isDraft }
                }
            }
            """ if is_draft else """
            mutation($pullRequestId: ID!) {
                markPullRequestReadyForReview(input: {pullRequestId: $pullRequestId}) {
                    pullRequest { isDraft }
                }
            }
            """

            # Get PR node ID for GraphQL
            pr_node_id = pr.raw_data.get("node_id")

            # Execute GraphQL mutation
            self._execute_graphql(mutation, {"pullRequestId": pr_node_id, "isDraft": is_draft})

            status = "draft" if is_draft else "ready"
            logger.info(f"Updated PR #{pr_number} to {status} status")

        except Exception as e:
            logger.error(f"Failed to update status for PR #{pr_number}: {str(e)}")
            raise

    def add_comment(self, pr_number: int, comment: str) -> None:
        """Add a comment to a pull request.

        Args:
            pr_number: Pull request number
            comment: Comment text (markdown supported)

        Raises:
            GithubException: If comment creation fails
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            logger.info(f"Added comment to PR #{pr_number}")

        except GithubException as e:
            logger.error(f"Failed to add comment to PR #{pr_number}: {str(e)}")
            raise

    def request_review(self, pr_number: int, reviewers: List[str]) -> None:
        """Request reviews from specific users.

        Args:
            pr_number: Pull request number
            reviewers: List of GitHub usernames to request reviews from

        Raises:
            GithubException: If review request fails
        """
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_review_request(reviewers=reviewers)
            logger.info(f"Requested reviews for PR #{pr_number} from: {reviewers}")

        except GithubException as e:
            logger.error(f"Failed to request reviews for PR #{pr_number}: {str(e)}")
            raise

    # Private helper methods

    def _extract_file_changes(self, comparison) -> List[FileChange]:
        """Extract file changes from comparison object."""
        file_changes = []

        for file in comparison.files:
            change = FileChange(
                path=file.filename,
                additions=file.additions,
                deletions=file.deletions,
                change_type=file.status,
            )
            file_changes.append(change)

        return file_changes

    def _generate_title(self, spec_id: Optional[str], file_changes: List[FileChange]) -> str:
        """Generate PR title from SPEC and changes."""
        if spec_id:
            # Try to read SPEC title
            spec_data = self._read_spec_file(spec_id)
            if spec_data and "title" in spec_data:
                return f"{spec_id}: {spec_data['title']}"

        # Fallback: generate from file changes
        change_type = self._determine_change_type(file_changes)
        return f"{change_type}: Changes from {len(file_changes)} files"

    def _determine_labels(self, file_changes: List[FileChange]) -> List[str]:
        """Determine appropriate labels based on file changes."""
        labels = set()

        # Label mapping rules
        label_rules = {
            "api": ["api/", "endpoints/", "routes/"],
            "frontend": ["ui/", "components/", "pages/"],
            "backend": ["core/", "services/", "models/"],
            "testing": ["tests/", "test_", "_test"],
            "documentation": ["docs/", "README", ".md"],
            "configuration": ["config/", ".yaml", ".json", ".toml"],
        }

        for change in file_changes:
            path = change.path.lower()

            # Check path-based rules
            for label, patterns in label_rules.items():
                if any(pattern in path for pattern in patterns):
                    labels.add(label)

        # Add size labels
        total_changes = sum(c.additions + c.deletions for c in file_changes)
        if total_changes < 50:
            labels.add("size:small")
        elif total_changes < 200:
            labels.add("size:medium")
        else:
            labels.add("size:large")

        return list(labels)

    def _determine_change_type(self, file_changes: List[FileChange]) -> str:
        """Determine the type of change (feature, fix, refactor, etc.)."""
        # Check file paths for clues
        has_tests = any("test" in c.path.lower() for c in file_changes)
        has_docs = any(".md" in c.path.lower() for c in file_changes)

        if has_docs and len(file_changes) == 1:
            return "docs"
        elif has_tests:
            return "test"
        else:
            return "feat"

    def _load_pr_template(self) -> str:
        """Load PR template from file or use default."""
        # Try to load MoAI Flow custom template first
        custom_template_path = Path(__file__).parent / "templates" / "pr_template.md"
        if custom_template_path.exists():
            return custom_template_path.read_text()

        # Fallback to project .github template
        github_template_path = Path(".github/PULL_REQUEST_TEMPLATE.md")
        if github_template_path.exists():
            return github_template_path.read_text()

        # Use default template as last resort
        return self._get_default_template()

    def _get_default_template(self) -> str:
        """Get default PR template."""
        return """## SPEC

Implements: {{SPEC_ID}}

## Summary

{{SUMMARY}}

## Changes

{{CHANGES}}

## Test Plan

{{TEST_PLAN}}

## Breaking Changes

{{BREAKING_CHANGES}}

## Deployment Notes

{{DEPLOYMENT_NOTES}}
"""

    def _read_spec_file(self, spec_id: str) -> Optional[Dict[str, str]]:
        """Read SPEC file and extract metadata."""
        try:
            spec_path = Path(f".moai/specs/{spec_id}/spec.md")
            if not spec_path.exists():
                return None

            content = spec_path.read_text()

            # Extract title (first # heading)
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else ""

            # Extract summary (content between ## Summary and next ##)
            summary_match = re.search(
                r"##\s+Summary\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL
            )
            summary = summary_match.group(1).strip() if summary_match else ""

            # Extract breaking changes
            breaking_match = re.search(
                r"##\s+Breaking Changes\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL
            )
            breaking_changes = breaking_match.group(1).strip() if breaking_match else ""

            # Extract deployment notes
            deployment_match = re.search(
                r"##\s+Deployment\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL
            )
            deployment_notes = deployment_match.group(1).strip() if deployment_match else ""

            return {
                "title": title,
                "summary": summary,
                "breaking_changes": breaking_changes,
                "deployment_notes": deployment_notes,
            }

        except Exception as e:
            logger.warning(f"Failed to read SPEC file {spec_id}: {str(e)}")
            return None

    def _format_file_changes(self, file_changes: List[FileChange]) -> str:
        """Format file changes as markdown table."""
        if not file_changes:
            return "No file changes"

        lines = ["| File | Changes | Type |", "|------|---------|------|"]

        for change in file_changes:
            total = change.additions + change.deletions
            lines.append(
                f"| `{change.path}` | +{change.additions}/-{change.deletions} | {change.change_type} |"
            )

        return "\n".join(lines)

    def _generate_test_plan(self, file_changes: List[FileChange]) -> str:
        """Generate test plan checklist."""
        has_tests = any("test" in c.path.lower() for c in file_changes)
        has_code = any(
            c.path.endswith((".py", ".ts", ".js", ".go", ".rs")) for c in file_changes
        )

        checklist = []

        if has_code:
            checklist.extend([
                "- [ ] Unit tests passing",
                "- [ ] Integration tests passing",
                "- [ ] Coverage >= 90%",
            ])

        if has_tests:
            checklist.append("- [ ] New tests added for changes")

        checklist.extend([
            "- [ ] Manual testing completed",
            "- [ ] No breaking changes (or documented)",
        ])

        return "\n".join(checklist)

    def _execute_graphql(self, mutation: str, variables: Dict[str, Any]) -> Dict:
        """Execute GraphQL mutation against GitHub API."""
        # This is a simplified version - in production, use proper GraphQL client
        import requests

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": mutation, "variables": variables},
            headers=headers,
        )

        response.raise_for_status()
        return response.json()
