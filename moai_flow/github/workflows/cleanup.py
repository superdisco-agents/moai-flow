"""GitHub Cleanup Workflows for PRD-06 Repo Health.

This module provides automated cleanup workflows for maintaining repository health:
- StaleIssueWorkflow: Auto-label and close stale issues (30/60/90 day workflow)
- StalePRWorkflow: Auto-label and close stale pull requests (14/30/60 day workflow)
- AutoLabelWorkflow: Auto-label based on file changes
- NotificationWorkflow: Notify on health degradation

Example:
    >>> from moai_flow.github.workflows.cleanup import StaleIssueWorkflow
    >>> workflow = StaleIssueWorkflow(repo_owner="moai", repo_name="adk")
    >>> affected = workflow.preview()  # Dry run
    >>> workflow.execute()  # Execute cleanup
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

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


class WorkflowAction(Enum):
    """Workflow action types."""
    LABEL = "label"
    COMMENT = "comment"
    CLOSE = "close"
    NOTIFY = "notify"
    SKIP = "skip"


@dataclass
class WorkflowConfig:
    """Configuration for cleanup workflows.

    Attributes:
        stale_issue_days_warning: Days before marking issue as stale
        stale_issue_days_comment: Days before adding close warning comment
        stale_issue_days_close: Days before auto-closing
        stale_pr_days_warning: Days before marking PR as stale
        stale_pr_days_comment: Days before adding close warning comment
        stale_pr_days_close: Days before auto-closing
        exempt_labels: Labels that exempt issues/PRs from cleanup
        auto_label_enabled: Enable auto-labeling based on file changes
        notification_enabled: Enable health degradation notifications
        dry_run: Preview mode (no actual changes)
    """
    stale_issue_days_warning: int = 30
    stale_issue_days_comment: int = 60
    stale_issue_days_close: int = 90
    stale_pr_days_warning: int = 14
    stale_pr_days_comment: int = 30
    stale_pr_days_close: int = 60
    exempt_labels: List[str] = None
    auto_label_enabled: bool = True
    notification_enabled: bool = True
    dry_run: bool = False

    def __post_init__(self):
        """Initialize default exempt labels."""
        if self.exempt_labels is None:
            self.exempt_labels = [
                "pinned",
                "security",
                "priority:critical",
                "priority:high",
                "wip",
                "in-progress"
            ]


@dataclass
class WorkflowResult:
    """Result of workflow execution.

    Attributes:
        workflow_name: Name of executed workflow
        actions_taken: List of actions performed
        items_affected: Number of items processed
        items_labeled: Number of items labeled
        items_commented: Number of items commented
        items_closed: Number of items closed
        notifications_sent: Number of notifications sent
        errors: List of errors encountered
        dry_run: Whether this was a dry run
    """
    workflow_name: str
    actions_taken: List[str]
    items_affected: int = 0
    items_labeled: int = 0
    items_commented: int = 0
    items_closed: int = 0
    notifications_sent: int = 0
    errors: List[str] = None
    dry_run: bool = False

    def __post_init__(self):
        """Initialize errors list."""
        if self.errors is None:
            self.errors = []


class BaseWorkflow:
    """Base class for cleanup workflows.

    Provides common functionality for all workflow types:
    - GitHub API client initialization
    - Configuration management
    - Preview mode (dry run)
    - Error handling and logging

    Attributes:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        github_token: GitHub API authentication token
        config: Workflow configuration
        github_client: PyGithub client instance
        repo: GitHub repository object
    """

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: Optional[str] = None,
        config: Optional[WorkflowConfig] = None
    ):
        """Initialize base workflow.

        Args:
            repo_owner: Repository owner username/organization
            repo_name: Repository name
            github_token: GitHub API token (defaults to GITHUB_TOKEN env var)
            config: Workflow configuration (defaults to WorkflowConfig())

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
        self.config = config or WorkflowConfig()

        if not self.github_token:
            raise ValueError(
                "GitHub token is required. Provide via parameter or GITHUB_TOKEN env var"
            )

        # Initialize GitHub client
        auth = Auth.Token(self.github_token)
        self.github_client = Github(auth=auth)
        self.repo = self.github_client.get_repo(f"{repo_owner}/{repo_name}")

        logger.info(f"Initialized {self.__class__.__name__} for {repo_owner}/{repo_name}")

    def execute(self) -> WorkflowResult:
        """Execute workflow.

        Must be implemented by subclasses.

        Returns:
            WorkflowResult with execution details
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def preview(self) -> WorkflowResult:
        """Preview workflow execution (dry run).

        Shows what would happen without making changes.

        Returns:
            WorkflowResult with preview details
        """
        original_dry_run = self.config.dry_run
        self.config.dry_run = True
        try:
            result = self.execute()
            result.dry_run = True
            return result
        finally:
            self.config.dry_run = original_dry_run

    def configure(self, **kwargs) -> None:
        """Update workflow configuration.

        Args:
            **kwargs: Configuration parameters to update

        Example:
            >>> workflow.configure(stale_issue_days_close=120)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")

    def get_affected_items(self) -> List[Any]:
        """Get list of items that would be affected by workflow.

        Must be implemented by subclasses.

        Returns:
            List of GitHub items (Issues or PullRequests)
        """
        raise NotImplementedError("Subclasses must implement get_affected_items()")


class StaleIssueWorkflow(BaseWorkflow):
    """Stale issue cleanup workflow.

    Implements 30/60/90 day stale issue workflow:
    - Day 30: Add "stale" label
    - Day 60: Add comment "Will close in 30 days"
    - Day 90: Auto-close with comment

    Example:
        >>> workflow = StaleIssueWorkflow("owner", "repo")
        >>> workflow.configure(stale_issue_days_close=120)
        >>> affected = workflow.get_affected_items()
        >>> result = workflow.execute()
    """

    def execute(self) -> WorkflowResult:
        """Execute stale issue cleanup.

        Returns:
            WorkflowResult with execution details
        """
        result = WorkflowResult(
            workflow_name="StaleIssueWorkflow",
            actions_taken=[],
            dry_run=self.config.dry_run
        )

        try:
            now = datetime.now()
            issues = self.repo.get_issues(state="open")

            for issue in issues:
                # Skip PRs (they have a different workflow)
                if issue.pull_request:
                    continue

                # Skip exempt issues
                issue_labels = [label.name for label in issue.labels]
                if any(exempt in issue_labels for exempt in self.config.exempt_labels):
                    logger.debug(f"Skipping exempt issue #{issue.number}")
                    continue

                # Calculate days since last update
                last_updated = issue.updated_at
                days_stale = (now - last_updated).days

                # Determine action based on staleness
                action = self._determine_action(days_stale, issue_labels)

                if action == WorkflowAction.SKIP:
                    continue

                # Execute action
                self._execute_action(issue, action, days_stale, result)

            logger.info(
                f"StaleIssueWorkflow completed: {result.items_affected} items processed"
            )
            return result

        except Exception as e:
            logger.error(f"StaleIssueWorkflow failed: {str(e)}")
            result.errors.append(str(e))
            return result

    def get_affected_items(self) -> List[Issue]:
        """Get list of issues that would be affected.

        Returns:
            List of Issue objects that would be processed
        """
        affected = []
        now = datetime.now()
        issues = self.repo.get_issues(state="open")

        for issue in issues:
            # Skip PRs
            if issue.pull_request:
                continue

            # Skip exempt issues
            issue_labels = [label.name for label in issue.labels]
            if any(exempt in issue_labels for exempt in self.config.exempt_labels):
                continue

            # Check if stale
            last_updated = issue.updated_at
            days_stale = (now - last_updated).days

            if days_stale >= self.config.stale_issue_days_warning:
                affected.append(issue)

        return affected

    def _determine_action(self, days_stale: int, labels: List[str]) -> WorkflowAction:
        """Determine action based on staleness.

        Args:
            days_stale: Days since last update
            labels: Current issue labels

        Returns:
            WorkflowAction to take
        """
        # Already has stale label
        has_stale_label = "stale" in labels

        # Day 90: Close
        if days_stale >= self.config.stale_issue_days_close:
            return WorkflowAction.CLOSE

        # Day 60: Comment (if has stale label)
        if days_stale >= self.config.stale_issue_days_comment and has_stale_label:
            return WorkflowAction.COMMENT

        # Day 30: Label
        if days_stale >= self.config.stale_issue_days_warning and not has_stale_label:
            return WorkflowAction.LABEL

        return WorkflowAction.SKIP

    def _execute_action(
        self,
        issue: Issue,
        action: WorkflowAction,
        days_stale: int,
        result: WorkflowResult
    ) -> None:
        """Execute action on issue.

        Args:
            issue: GitHub Issue object
            action: Action to execute
            days_stale: Days since last update
            result: WorkflowResult to update
        """
        try:
            if action == WorkflowAction.LABEL:
                self._add_stale_label(issue, result)
            elif action == WorkflowAction.COMMENT:
                self._add_close_warning(issue, result)
            elif action == WorkflowAction.CLOSE:
                self._close_stale_issue(issue, result)

            result.items_affected += 1

        except Exception as e:
            logger.error(f"Failed to execute action on issue #{issue.number}: {str(e)}")
            result.errors.append(f"Issue #{issue.number}: {str(e)}")

    def _add_stale_label(self, issue: Issue, result: WorkflowResult) -> None:
        """Add 'stale' label to issue.

        Args:
            issue: GitHub Issue object
            result: WorkflowResult to update
        """
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would add 'stale' label to issue #{issue.number}")
            result.actions_taken.append(f"Label #{issue.number}")
        else:
            issue.add_to_labels("stale")
            logger.info(f"Added 'stale' label to issue #{issue.number}")
            result.actions_taken.append(f"Labeled #{issue.number}")
            result.items_labeled += 1

    def _add_close_warning(self, issue: Issue, result: WorkflowResult) -> None:
        """Add close warning comment to issue.

        Args:
            issue: GitHub Issue object
            result: WorkflowResult to update
        """
        days_until_close = self.config.stale_issue_days_close - self.config.stale_issue_days_comment

        comment = f"""## Stale Issue Notice

This issue has been inactive for {self.config.stale_issue_days_comment} days and will be automatically closed in **{days_until_close} days** if no further activity occurs.

**To keep this issue open:**
- Add a comment with updates or progress
- Remove the `stale` label
- Add a `pinned` label to exempt from auto-closure

If you believe this issue is still relevant, please provide an update.

*This is an automated message from the repository cleanup workflow.*
"""

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would add close warning to issue #{issue.number}")
            result.actions_taken.append(f"Comment #{issue.number}")
        else:
            issue.create_comment(comment)
            logger.info(f"Added close warning to issue #{issue.number}")
            result.actions_taken.append(f"Commented #{issue.number}")
            result.items_commented += 1

    def _close_stale_issue(self, issue: Issue, result: WorkflowResult) -> None:
        """Close stale issue.

        Args:
            issue: GitHub Issue object
            result: WorkflowResult to update
        """
        comment = f"""## Auto-Closing Stale Issue

This issue has been inactive for {self.config.stale_issue_days_close} days and is being automatically closed.

**Why was this closed?**
- No activity for {self.config.stale_issue_days_close} days
- Marked as stale at day {self.config.stale_issue_days_warning}
- Close warning added at day {self.config.stale_issue_days_comment}

**To reopen:**
If this issue is still relevant, please reopen it and provide an update on its current status.

*This is an automated closure from the repository cleanup workflow.*
"""

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would close issue #{issue.number}")
            result.actions_taken.append(f"Close #{issue.number}")
        else:
            issue.create_comment(comment)
            issue.edit(state="closed")
            logger.info(f"Closed stale issue #{issue.number}")
            result.actions_taken.append(f"Closed #{issue.number}")
            result.items_closed += 1


class StalePRWorkflow(BaseWorkflow):
    """Stale pull request cleanup workflow.

    Implements 14/30/60 day stale PR workflow:
    - Day 14: Add "stale" label
    - Day 30: Add comment "Will close in 30 days"
    - Day 60: Auto-close with comment

    Example:
        >>> workflow = StalePRWorkflow("owner", "repo")
        >>> workflow.configure(stale_pr_days_close=90)
        >>> result = workflow.preview()  # Dry run
    """

    def execute(self) -> WorkflowResult:
        """Execute stale PR cleanup.

        Returns:
            WorkflowResult with execution details
        """
        result = WorkflowResult(
            workflow_name="StalePRWorkflow",
            actions_taken=[],
            dry_run=self.config.dry_run
        )

        try:
            now = datetime.now()
            prs = self.repo.get_pulls(state="open")

            for pr in prs:
                # Skip exempt PRs
                pr_labels = [label.name for label in pr.labels]
                if any(exempt in pr_labels for exempt in self.config.exempt_labels):
                    logger.debug(f"Skipping exempt PR #{pr.number}")
                    continue

                # Calculate days since last update
                last_updated = pr.updated_at
                days_stale = (now - last_updated).days

                # Determine action
                action = self._determine_action(days_stale, pr_labels)

                if action == WorkflowAction.SKIP:
                    continue

                # Execute action
                self._execute_action(pr, action, days_stale, result)

            logger.info(
                f"StalePRWorkflow completed: {result.items_affected} PRs processed"
            )
            return result

        except Exception as e:
            logger.error(f"StalePRWorkflow failed: {str(e)}")
            result.errors.append(str(e))
            return result

    def get_affected_items(self) -> List[PullRequest]:
        """Get list of PRs that would be affected.

        Returns:
            List of PullRequest objects that would be processed
        """
        affected = []
        now = datetime.now()
        prs = self.repo.get_pulls(state="open")

        for pr in prs:
            # Skip exempt PRs
            pr_labels = [label.name for label in pr.labels]
            if any(exempt in pr_labels for exempt in self.config.exempt_labels):
                continue

            # Check if stale
            last_updated = pr.updated_at
            days_stale = (now - last_updated).days

            if days_stale >= self.config.stale_pr_days_warning:
                affected.append(pr)

        return affected

    def _determine_action(self, days_stale: int, labels: List[str]) -> WorkflowAction:
        """Determine action based on staleness.

        Args:
            days_stale: Days since last update
            labels: Current PR labels

        Returns:
            WorkflowAction to take
        """
        has_stale_label = "stale" in labels

        # Day 60: Close
        if days_stale >= self.config.stale_pr_days_close:
            return WorkflowAction.CLOSE

        # Day 30: Comment
        if days_stale >= self.config.stale_pr_days_comment and has_stale_label:
            return WorkflowAction.COMMENT

        # Day 14: Label
        if days_stale >= self.config.stale_pr_days_warning and not has_stale_label:
            return WorkflowAction.LABEL

        return WorkflowAction.SKIP

    def _execute_action(
        self,
        pr: PullRequest,
        action: WorkflowAction,
        days_stale: int,
        result: WorkflowResult
    ) -> None:
        """Execute action on PR.

        Args:
            pr: GitHub PullRequest object
            action: Action to execute
            days_stale: Days since last update
            result: WorkflowResult to update
        """
        try:
            if action == WorkflowAction.LABEL:
                self._add_stale_label(pr, result)
            elif action == WorkflowAction.COMMENT:
                self._add_close_warning(pr, result)
            elif action == WorkflowAction.CLOSE:
                self._close_stale_pr(pr, result)

            result.items_affected += 1

        except Exception as e:
            logger.error(f"Failed to execute action on PR #{pr.number}: {str(e)}")
            result.errors.append(f"PR #{pr.number}: {str(e)}")

    def _add_stale_label(self, pr: PullRequest, result: WorkflowResult) -> None:
        """Add 'stale' label to PR."""
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would add 'stale' label to PR #{pr.number}")
            result.actions_taken.append(f"Label PR #{pr.number}")
        else:
            pr.add_to_labels("stale")
            logger.info(f"Added 'stale' label to PR #{pr.number}")
            result.actions_taken.append(f"Labeled PR #{pr.number}")
            result.items_labeled += 1

    def _add_close_warning(self, pr: PullRequest, result: WorkflowResult) -> None:
        """Add close warning comment to PR."""
        days_until_close = self.config.stale_pr_days_close - self.config.stale_pr_days_comment

        comment = f"""## Stale Pull Request Notice

This pull request has been inactive for {self.config.stale_pr_days_comment} days and will be automatically closed in **{days_until_close} days** if no further activity occurs.

**To keep this PR open:**
- Push new commits or respond to review comments
- Remove the `stale` label
- Add a `wip` label if still in progress
- Add a `pinned` label to exempt from auto-closure

If this PR is ready for review, please request reviews. If it's blocked, please explain what's blocking it.

*This is an automated message from the repository cleanup workflow.*
"""

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would add close warning to PR #{pr.number}")
            result.actions_taken.append(f"Comment PR #{pr.number}")
        else:
            pr.create_issue_comment(comment)
            logger.info(f"Added close warning to PR #{pr.number}")
            result.actions_taken.append(f"Commented PR #{pr.number}")
            result.items_commented += 1

    def _close_stale_pr(self, pr: PullRequest, result: WorkflowResult) -> None:
        """Close stale PR."""
        comment = f"""## Auto-Closing Stale Pull Request

This pull request has been inactive for {self.config.stale_pr_days_close} days and is being automatically closed.

**Why was this closed?**
- No activity for {self.config.stale_pr_days_close} days
- Marked as stale at day {self.config.stale_pr_days_warning}
- Close warning added at day {self.config.stale_pr_days_comment}

**To reopen:**
If this PR is still relevant, please reopen it and:
1. Rebase on the latest main branch
2. Resolve any merge conflicts
3. Address review comments
4. Request fresh reviews

*This is an automated closure from the repository cleanup workflow.*
"""

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would close PR #{pr.number}")
            result.actions_taken.append(f"Close PR #{pr.number}")
        else:
            pr.create_issue_comment(comment)
            pr.edit(state="closed")
            logger.info(f"Closed stale PR #{pr.number}")
            result.actions_taken.append(f"Closed PR #{pr.number}")
            result.items_closed += 1


class AutoLabelWorkflow(BaseWorkflow):
    """Auto-label workflow based on file changes.

    Automatically labels PRs based on changed files:
    - backend/** → label: "backend"
    - frontend/** → label: "frontend"
    - tests/** → label: "testing"
    - docs/** → label: "documentation"

    Example:
        >>> workflow = AutoLabelWorkflow("owner", "repo")
        >>> workflow.add_label_rule("src/api/**", "api")
        >>> result = workflow.execute()
    """

    def __init__(self, *args, **kwargs):
        """Initialize auto-label workflow."""
        super().__init__(*args, **kwargs)
        self._label_rules = self._get_default_label_rules()

    def execute(self) -> WorkflowResult:
        """Execute auto-labeling on open PRs.

        Returns:
            WorkflowResult with execution details
        """
        result = WorkflowResult(
            workflow_name="AutoLabelWorkflow",
            actions_taken=[],
            dry_run=self.config.dry_run
        )

        if not self.config.auto_label_enabled:
            logger.info("AutoLabelWorkflow is disabled in config")
            return result

        try:
            prs = self.repo.get_pulls(state="open")

            for pr in prs:
                labels_to_add = self._determine_labels(pr)

                if labels_to_add:
                    self._add_labels(pr, labels_to_add, result)
                    result.items_affected += 1

            logger.info(
                f"AutoLabelWorkflow completed: {result.items_labeled} labels added"
            )
            return result

        except Exception as e:
            logger.error(f"AutoLabelWorkflow failed: {str(e)}")
            result.errors.append(str(e))
            return result

    def get_affected_items(self) -> List[PullRequest]:
        """Get list of PRs that would be labeled.

        Returns:
            List of PullRequest objects that would receive labels
        """
        affected = []
        prs = self.repo.get_pulls(state="open")

        for pr in prs:
            labels_to_add = self._determine_labels(pr)
            if labels_to_add:
                affected.append(pr)

        return affected

    def add_label_rule(self, path_pattern: str, label: str) -> None:
        """Add custom label rule.

        Args:
            path_pattern: File path pattern (supports wildcards)
            label: Label to apply

        Example:
            >>> workflow.add_label_rule("src/api/**", "api")
        """
        self._label_rules[path_pattern] = label
        logger.info(f"Added label rule: {path_pattern} → {label}")

    def _get_default_label_rules(self) -> Dict[str, str]:
        """Get default label rules.

        Returns:
            Dict mapping path patterns to labels
        """
        return {
            "backend/**": "backend",
            "src/backend/**": "backend",
            "api/**": "backend",
            "src/api/**": "backend",
            "frontend/**": "frontend",
            "src/frontend/**": "frontend",
            "ui/**": "frontend",
            "src/ui/**": "frontend",
            "tests/**": "testing",
            "test/**": "testing",
            "src/tests/**": "testing",
            "docs/**": "documentation",
            "*.md": "documentation",
            "README*": "documentation",
            ".github/**": "ci-cd",
            ".gitlab-ci.yml": "ci-cd",
            "docker/**": "infrastructure",
            "Dockerfile": "infrastructure",
            "k8s/**": "infrastructure",
            "terraform/**": "infrastructure",
        }

    def _determine_labels(self, pr: PullRequest) -> Set[str]:
        """Determine labels for PR based on changed files.

        Args:
            pr: GitHub PullRequest object

        Returns:
            Set of labels to add
        """
        labels_to_add = set()
        existing_labels = {label.name for label in pr.labels}

        # Get changed files
        try:
            changed_files = [f.filename for f in pr.get_files()]
        except Exception as e:
            logger.warning(f"Failed to get changed files for PR #{pr.number}: {str(e)}")
            return labels_to_add

        # Match files against rules
        for file_path in changed_files:
            for pattern, label in self._label_rules.items():
                if self._matches_pattern(file_path, pattern):
                    if label not in existing_labels:
                        labels_to_add.add(label)

        return labels_to_add

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern.

        Args:
            file_path: File path to check
            pattern: Pattern (supports ** and * wildcards)

        Returns:
            True if matches
        """
        import fnmatch

        # Convert ** to * for fnmatch (simple implementation)
        pattern = pattern.replace("**", "*")
        return fnmatch.fnmatch(file_path, pattern)

    def _add_labels(self, pr: PullRequest, labels: Set[str], result: WorkflowResult) -> None:
        """Add labels to PR.

        Args:
            pr: GitHub PullRequest object
            labels: Labels to add
            result: WorkflowResult to update
        """
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would add labels {labels} to PR #{pr.number}")
            result.actions_taken.append(f"Label PR #{pr.number}: {', '.join(labels)}")
            result.items_labeled += len(labels)
        else:
            for label in labels:
                pr.add_to_labels(label)
            logger.info(f"Added labels {labels} to PR #{pr.number}")
            result.actions_taken.append(f"Labeled PR #{pr.number}: {', '.join(labels)}")
            result.items_labeled += len(labels)


class NotificationWorkflow(BaseWorkflow):
    """Notification workflow for health degradation.

    Monitors repository health metrics and sends notifications when
    thresholds are exceeded:
    - High stale issue ratio
    - High stale PR ratio
    - Low review participation
    - Slow PR merge time

    Example:
        >>> workflow = NotificationWorkflow("owner", "repo")
        >>> workflow.configure_thresholds(stale_issue_ratio=0.3)
        >>> result = workflow.execute()
    """

    def __init__(self, *args, **kwargs):
        """Initialize notification workflow."""
        super().__init__(*args, **kwargs)
        self._thresholds = {
            "stale_issue_ratio": 0.25,  # 25% of open issues are stale
            "stale_pr_ratio": 0.20,  # 20% of open PRs are stale
            "avg_pr_age_days": 14,  # Average PR age exceeds 14 days
        }

    def execute(self) -> WorkflowResult:
        """Execute health monitoring and notifications.

        Returns:
            WorkflowResult with notification details
        """
        result = WorkflowResult(
            workflow_name="NotificationWorkflow",
            actions_taken=[],
            dry_run=self.config.dry_run
        )

        if not self.config.notification_enabled:
            logger.info("NotificationWorkflow is disabled in config")
            return result

        try:
            # Calculate health metrics
            metrics = self._calculate_health_metrics()

            # Check thresholds and send notifications
            violations = self._check_thresholds(metrics)

            if violations:
                self._send_notification(violations, metrics, result)
                result.notifications_sent = 1
                result.items_affected = len(violations)

            logger.info(
                f"NotificationWorkflow completed: {result.notifications_sent} notifications sent"
            )
            return result

        except Exception as e:
            logger.error(f"NotificationWorkflow failed: {str(e)}")
            result.errors.append(str(e))
            return result

    def get_affected_items(self) -> List[str]:
        """Get list of health metrics that violate thresholds.

        Returns:
            List of metric names that would trigger notifications
        """
        metrics = self._calculate_health_metrics()
        violations = self._check_thresholds(metrics)
        return violations

    def configure_thresholds(self, **kwargs) -> None:
        """Configure notification thresholds.

        Args:
            **kwargs: Threshold parameters to update

        Example:
            >>> workflow.configure_thresholds(stale_issue_ratio=0.30)
        """
        for key, value in kwargs.items():
            if key in self._thresholds:
                self._thresholds[key] = value
                logger.info(f"Updated threshold: {key} = {value}")
            else:
                logger.warning(f"Unknown threshold parameter: {key}")

    def _calculate_health_metrics(self) -> Dict[str, float]:
        """Calculate repository health metrics.

        Returns:
            Dict of metric names to values
        """
        metrics = {}

        # Issue metrics
        open_issues = list(self.repo.get_issues(state="open"))
        open_issues = [i for i in open_issues if not i.pull_request]  # Exclude PRs
        stale_issues = [i for i in open_issues if "stale" in [l.name for l in i.labels]]

        if open_issues:
            metrics["stale_issue_ratio"] = len(stale_issues) / len(open_issues)
        else:
            metrics["stale_issue_ratio"] = 0.0

        # PR metrics
        open_prs = list(self.repo.get_pulls(state="open"))
        stale_prs = [pr for pr in open_prs if "stale" in [l.name for l in pr.labels]]

        if open_prs:
            metrics["stale_pr_ratio"] = len(stale_prs) / len(open_prs)

            # Average PR age
            now = datetime.now()
            pr_ages = [(now - pr.created_at).days for pr in open_prs]
            metrics["avg_pr_age_days"] = sum(pr_ages) / len(pr_ages) if pr_ages else 0.0
        else:
            metrics["stale_pr_ratio"] = 0.0
            metrics["avg_pr_age_days"] = 0.0

        return metrics

    def _check_thresholds(self, metrics: Dict[str, float]) -> List[str]:
        """Check if metrics violate thresholds.

        Args:
            metrics: Calculated health metrics

        Returns:
            List of violated metric names
        """
        violations = []

        for metric_name, threshold in self._thresholds.items():
            if metric_name in metrics and metrics[metric_name] > threshold:
                violations.append(metric_name)

        return violations

    def _send_notification(
        self,
        violations: List[str],
        metrics: Dict[str, float],
        result: WorkflowResult
    ) -> None:
        """Send health degradation notification.

        Args:
            violations: List of violated metrics
            metrics: All calculated metrics
            result: WorkflowResult to update
        """
        # Create notification issue
        title = "🚨 Repository Health Alert: Cleanup Required"

        body = f"""## Repository Health Degradation Detected

The automated health monitoring system has detected metrics exceeding thresholds.

### Violations

"""

        for violation in violations:
            metric_value = metrics[violation]
            threshold = self._thresholds[violation]
            body += f"- **{violation}**: {metric_value:.2f} (threshold: {threshold:.2f})\n"

        body += f"""

### Current Metrics

- Stale Issue Ratio: {metrics['stale_issue_ratio']:.2%}
- Stale PR Ratio: {metrics['stale_pr_ratio']:.2%}
- Average PR Age: {metrics['avg_pr_age_days']:.1f} days

### Recommended Actions

1. Review and close stale issues
2. Review and merge or close stale PRs
3. Update cleanup workflow thresholds if needed
4. Consider increasing team review capacity

### Cleanup Workflows

Run the following workflows to improve health:

```python
from moai_flow.github.workflows.cleanup import StaleIssueWorkflow, StalePRWorkflow

# Preview what would be cleaned
stale_issues = StaleIssueWorkflow("owner", "repo")
stale_issues.preview()

stale_prs = StalePRWorkflow("owner", "repo")
stale_prs.preview()

# Execute cleanup
stale_issues.execute()
stale_prs.execute()
```

*This is an automated notification from the repository health monitoring system.*
"""

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would create health alert issue")
            result.actions_taken.append("Create health alert issue")
        else:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=["health-alert", "cleanup-needed"]
            )
            logger.info(f"Created health alert issue #{issue.number}")
            result.actions_taken.append(f"Created health alert issue #{issue.number}")
