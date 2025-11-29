"""GitHub Cleanup Workflows for Repository Health Management.

This package provides automated cleanup workflows for maintaining repository health:

- StaleIssueWorkflow: 30/60/90 day stale issue cleanup
- StalePRWorkflow: 14/30/60 day stale PR cleanup
- AutoLabelWorkflow: Auto-label PRs based on file changes
- NotificationWorkflow: Health degradation notifications

Example:
    >>> from moai_flow.github.workflows import (
    ...     StaleIssueWorkflow,
    ...     StalePRWorkflow,
    ...     AutoLabelWorkflow,
    ...     NotificationWorkflow
    ... )
    >>>
    >>> # Stale issue cleanup
    >>> workflow = StaleIssueWorkflow("owner", "repo")
    >>> result = workflow.preview()  # Dry run
    >>> result = workflow.execute()  # Execute
    >>>
    >>> # Auto-label PRs
    >>> auto_label = AutoLabelWorkflow("owner", "repo")
    >>> auto_label.add_label_rule("src/api/**", "api")
    >>> auto_label.execute()
"""

from .cleanup import (
    StaleIssueWorkflow,
    StalePRWorkflow,
    AutoLabelWorkflow,
    NotificationWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowAction,
)

__all__ = [
    "StaleIssueWorkflow",
    "StalePRWorkflow",
    "AutoLabelWorkflow",
    "NotificationWorkflow",
    "WorkflowConfig",
    "WorkflowResult",
    "WorkflowAction",
]
