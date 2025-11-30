"""GitHub automation and integration module (100% isolated).

This module provides GitHub-specific automation agents with ZERO moai_flow dependencies.
All classes are fully standalone and use only standard library + external packages (PyGithub, requests).

Available classes:
    PR Management:
        - GitHubPRAgent: Automated PR creation and management
        - PRMetadata: PR metadata dataclass
        - FileChange: File change representation

    Issue Management:
        - GitHubIssueAgent: Automated issue creation and triage
        - IssueTriage: Issue classification and priority assignment
        - IssueMetadata: Issue metadata dataclass
        - IssuePriority: Priority level enumeration
        - TriageRule: Custom triage rule definition

    Repository Health:
        - GitHubRepoAgent: Repository health monitoring and stale item management
        - HealthMetrics: Repository health metrics (from repo_agent)
        - HealthCategory: Health category enumeration
        - StaleItem: Stale issue/PR representation
        - Recommendation: Actionable recommendation dataclass
        - RecommendationPriority: Recommendation priority enumeration

    Health Metrics Analysis:
        - HealthMetricsAnalyzer: Comprehensive health metrics analysis
        - HealthMetrics: Health metrics snapshot (from health_metrics)
        - HealthTrend: Health trend enumeration
        - HealthComparison: Health metrics comparison

Note on HealthMetrics:
    - repo_agent.HealthMetrics: Basic health metrics for repo_agent
    - health_metrics.HealthMetrics: Advanced health metrics with trends
    Both are exported (no aliasing for clarity)

External Dependencies:
    - PyGithub (github): GitHub API client
    - requests: HTTP library for GraphQL mutations
    - Standard library only: os, re, sys, pathlib, typing, datetime, etc.
"""

# PR Agent exports
from moai_flow.github.pr_agent import (
    GitHubPRAgent,
    PRMetadata,
    FileChange,
)

# Issue Agent exports
from moai_flow.github.issue_agent import GitHubIssueAgent

# Triage System exports
from moai_flow.github.triage import (
    IssueTriage,
    IssueMetadata,
    IssuePriority,
    TriageRule,
)

# Repository Health Agent exports
from moai_flow.github.repo_agent import (
    GitHubRepoAgent,
    StaleItem,
    HealthMetrics as RepoHealthMetrics,  # Aliased to avoid confusion with health_metrics.HealthMetrics
    HealthCategory,
    Recommendation,
    RecommendationPriority,
)

# Health Metrics Analyzer exports
from moai_flow.github.health_metrics import (
    HealthMetricsAnalyzer,
    HealthMetrics,  # Advanced health metrics with trend analysis
    HealthTrend,
    HealthComparison,
)

__all__ = [
    # PR Agent
    "GitHubPRAgent",
    "PRMetadata",
    "FileChange",
    # Issue Agent
    "GitHubIssueAgent",
    # Triage System
    "IssueTriage",
    "IssueMetadata",
    "IssuePriority",
    "TriageRule",
    # Repository Health Agent
    "GitHubRepoAgent",
    "StaleItem",
    "RepoHealthMetrics",  # Alias of repo_agent.HealthMetrics
    "HealthCategory",
    "Recommendation",
    "RecommendationPriority",
    # Health Metrics Analyzer
    "HealthMetricsAnalyzer",
    "HealthMetrics",  # health_metrics.HealthMetrics (advanced)
    "HealthTrend",
    "HealthComparison",
]
