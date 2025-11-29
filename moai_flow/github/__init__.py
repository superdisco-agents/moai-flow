"""GitHub automation and integration module.

This module provides GitHub-specific automation agents for:
- PR creation and management (GitHubPRAgent)
- Issue triage and management (GitHubIssueAgent, IssueTriage)
- Repository health monitoring (GitHubRepoAgent)
- Repository analysis and health metrics (HealthMetricsAnalyzer)
- Cleanup workflows for repository health (StaleIssueWorkflow, StalePRWorkflow, etc.)

Available classes:
    - GitHubPRAgent: Automated PR creation and management
    - GitHubIssueAgent: Automated issue creation and triage
    - GitHubRepoAgent: Repository health monitoring and stale item management
    - IssueTriage: Issue classification and priority assignment
    - IssueMetadata: Issue metadata dataclass
    - IssuePriority: Priority level enumeration
    - TriageRule: Custom triage rule definition
    - HealthMetricsAnalyzer: Repository health metrics analysis
    - HealthMetrics: Health metrics dataclass
    - HealthTrend: Health trend enumeration
    - HealthComparison: Health metrics comparison
    - StaleIssueWorkflow: Automated stale issue cleanup (30/60/90 days)
    - StalePRWorkflow: Automated stale PR cleanup (14/30/60 days)
    - AutoLabelWorkflow: Auto-label PRs based on file changes
    - NotificationWorkflow: Health degradation notifications
    - WorkflowConfig: Cleanup workflow configuration
    - WorkflowResult: Cleanup workflow execution result
    - StaleItem: Stale issue/PR representation
    - RepoHealthMetrics: Repository health metrics
    - HealthCategory: Health category enumeration
    - Recommendation: Actionable recommendation dataclass
    - RecommendationPriority: Recommendation priority enumeration
"""

from moai_flow.github.pr_agent import GitHubPRAgent
from moai_flow.github.issue_agent import GitHubIssueAgent
from moai_flow.github.repo_agent import (
    GitHubRepoAgent,
    StaleItem,
    HealthMetrics as RepoHealthMetrics,
    HealthCategory,
    Recommendation,
    RecommendationPriority,
)
from moai_flow.github.triage import (
    IssueTriage,
    IssueMetadata,
    IssuePriority,
    TriageRule,
)
from moai_flow.github.health_metrics import (
    HealthMetricsAnalyzer,
    HealthMetrics,
    HealthTrend,
    HealthComparison,
)
from moai_flow.github.workflows import (
    StaleIssueWorkflow,
    StalePRWorkflow,
    AutoLabelWorkflow,
    NotificationWorkflow,
    WorkflowConfig,
    WorkflowResult,
)

__all__ = [
    "GitHubPRAgent",
    "GitHubIssueAgent",
    "GitHubRepoAgent",
    "IssueTriage",
    "IssueMetadata",
    "IssuePriority",
    "TriageRule",
    "HealthMetricsAnalyzer",
    "HealthMetrics",
    "HealthTrend",
    "HealthComparison",
    "StaleIssueWorkflow",
    "StalePRWorkflow",
    "AutoLabelWorkflow",
    "NotificationWorkflow",
    "WorkflowConfig",
    "WorkflowResult",
    "StaleItem",
    "RepoHealthMetrics",
    "HealthCategory",
    "Recommendation",
    "RecommendationPriority",
]
