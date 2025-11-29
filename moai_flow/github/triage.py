"""Automatic issue triage system for GitHub issues.

This module provides intelligent issue classification, priority assignment,
and assignee suggestions based on error patterns, context, and historical data.

Example:
    >>> triage = IssueTriage()
    >>> metadata = triage.classify(error, context)
    >>> print(f"Priority: {metadata.priority}")
    >>> print(f"Labels: {metadata.labels}")
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IssuePriority(Enum):
    """Issue priority levels based on severity and impact."""

    CRITICAL = "critical"  # Production down, security issues, data loss
    HIGH = "high"  # Major functionality broken, significant user impact
    MEDIUM = "medium"  # Feature bugs, performance issues
    LOW = "low"  # Minor bugs, documentation, enhancements


@dataclass
class IssueMetadata:
    """Metadata for a GitHub issue.

    Attributes:
        title: Issue title (concise summary)
        body: Issue body (detailed description)
        labels: List of label names to apply
        priority: Issue priority level
        assignees: List of GitHub usernames to assign
        milestone: Optional milestone name
    """

    title: str
    body: str
    labels: List[str]
    priority: IssuePriority
    assignees: List[str] = field(default_factory=list)
    milestone: Optional[str] = None


@dataclass
class TriageRule:
    """Triage rule definition for automatic classification.

    Attributes:
        error_patterns: List of regex patterns to match error messages
        labels: Labels to apply when pattern matches
        priority: Priority to assign when pattern matches
        assignees: Users to assign when pattern matches
        auto_close: Whether to auto-close matching issues (e.g., known duplicates)
    """

    error_patterns: List[str]
    labels: List[str]
    priority: IssuePriority
    assignees: List[str] = field(default_factory=list)
    auto_close: bool = False


class IssueTriage:
    """Automatic issue triage system.

    Classifies issues based on error type, stack trace, affected components,
    and historical patterns. Assigns appropriate labels, priority, and assignees.

    Example:
        >>> triage = IssueTriage()
        >>> metadata = triage.classify(
        ...     error=TimeoutError("Request timeout"),
        ...     context={"component": "api", "environment": "production"}
        ... )
        >>> print(metadata.priority)  # IssuePriority.HIGH
        >>> print(metadata.labels)  # ['timeout', 'api', 'production']
    """

    def __init__(self, custom_rules: Optional[List[TriageRule]] = None):
        """Initialize triage system with default or custom rules.

        Args:
            custom_rules: Optional list of custom triage rules to extend defaults
        """
        self._rules = self._load_default_rules()
        if custom_rules:
            self._rules.extend(custom_rules)

        logger.info(f"Initialized triage system with {len(self._rules)} rules")

    def classify(
        self, error: Exception, context: Dict[str, Any]
    ) -> IssueMetadata:
        """Classify issue based on error and context.

        Classification process:
        1. Error type matching (TimeoutError, PermissionError, etc.)
        2. Stack trace analysis (affected files, components)
        3. Context evaluation (environment, component, frequency)
        4. Historical pattern matching
        5. Priority and assignee calculation

        Args:
            error: Exception that triggered issue creation
            context: Additional context (environment, component, metadata)

        Returns:
            IssueMetadata with labels, priority, assignees, and description
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Initialize metadata
        labels = set()
        priority = IssuePriority.MEDIUM
        assignees = []

        # 1. Apply triage rules based on error patterns
        for rule in self._rules:
            # Check both error type and error message
            if self._matches_patterns(error_type, rule.error_patterns) or self._matches_patterns(error_message, rule.error_patterns):
                labels.update(rule.labels)
                priority = max(priority, rule.priority, key=lambda p: self._priority_rank(p))
                assignees.extend(rule.assignees)

        # 2. Add error type label
        labels.add(self._normalize_label(error_type))

        # 3. Add context-based labels
        if "component" in context:
            labels.add(context["component"])

        if "environment" in context and context["environment"] == "production":
            labels.add("production")
            priority = max(priority, IssuePriority.HIGH, key=lambda p: self._priority_rank(p))

        # 4. Calculate priority based on context
        priority = self.assign_priority(error, context)

        # 5. Suggest assignees based on component ownership
        suggested_assignees = self.suggest_assignees(error, context)
        assignees.extend(suggested_assignees)

        # Remove duplicates
        assignees = list(set(assignees))

        # Generate title and body
        title = self._generate_title(error, context)
        body = self._generate_body(error, context)

        return IssueMetadata(
            title=title,
            body=body,
            labels=sorted(list(labels)),
            priority=priority,
            assignees=assignees,
        )

    def assign_priority(
        self, error: Exception, context: Dict[str, Any]
    ) -> IssuePriority:
        """Calculate priority based on error severity and context.

        Priority calculation formula:
        - Error severity: 40% weight
        - Affected environment: 30% weight
        - Frequency: 20% weight
        - Business impact: 10% weight

        Args:
            error: Exception that triggered issue
            context: Additional context

        Returns:
            IssuePriority level
        """
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Calculate weighted score (0-100)
        score = 0.0

        # 1. Error severity (40% weight)
        severity_score = self._calculate_severity_score(error_type, error_message)
        score += severity_score * 0.4

        # 2. Affected environment (30% weight)
        environment_score = self._calculate_environment_score(context)
        score += environment_score * 0.3

        # 3. Frequency (20% weight)
        frequency_score = self._calculate_frequency_score(context)
        score += frequency_score * 0.2

        # 4. Business impact (10% weight)
        business_score = self._calculate_business_impact_score(context, error_message)
        score += business_score * 0.1

        # Map score to priority level
        if score >= 80:
            return IssuePriority.CRITICAL
        elif score >= 60:
            return IssuePriority.HIGH
        elif score >= 30:
            return IssuePriority.MEDIUM
        else:
            return IssuePriority.LOW

    def _calculate_severity_score(self, error_type: str, error_message: str) -> float:
        """Calculate error severity score (0-100).

        Args:
            error_type: Exception type name
            error_message: Error message text

        Returns:
            Severity score (0-100)
        """
        # CRITICAL severity (100 points)
        if error_type in ["MemoryError", "SystemExit", "PermissionError"]:
            return 100.0
        if any(kw in error_message for kw in ["data loss", "unauthorized", "access denied"]):
            return 100.0

        # HIGH severity (75 points)
        if error_type in ["TimeoutError", "ConnectionError", "DatabaseError", "ImportError", "AssertionError"]:
            return 75.0

        # MEDIUM severity (50 points)
        if error_type in ["TypeError", "ValueError", "KeyError", "AttributeError", "FileNotFoundError"]:
            return 50.0

        # LOW severity (25 points)
        return 25.0

    def _calculate_environment_score(self, context: Dict[str, Any]) -> float:
        """Calculate environment impact score (0-100).

        Args:
            context: Issue context with environment information

        Returns:
            Environment score (0-100)
        """
        environment = context.get("environment", "unknown")

        if environment == "production":
            return 100.0
        elif environment == "staging":
            return 60.0
        elif environment in ["development", "test"]:
            return 30.0
        else:
            return 50.0  # Unknown environment, moderate score

    def _calculate_frequency_score(self, context: Dict[str, Any]) -> float:
        """Calculate frequency impact score (0-100).

        Args:
            context: Issue context with frequency information

        Returns:
            Frequency score (0-100)
        """
        frequency = context.get("frequency", 1)

        if frequency >= 20:
            return 100.0
        elif frequency >= 10:
            return 75.0
        elif frequency >= 5:
            return 50.0
        elif frequency >= 2:
            return 25.0
        else:
            return 10.0  # First occurrence

    def _calculate_business_impact_score(
        self, context: Dict[str, Any], error_message: str
    ) -> float:
        """Calculate business impact score (0-100).

        Args:
            context: Issue context with business impact information
            error_message: Error message text

        Returns:
            Business impact score (0-100)
        """
        user_impact = context.get("user_impact", 0)
        tags = context.get("tags", [])

        # Revenue-affecting issues
        if "revenue" in tags or "payment" in error_message:
            return 100.0

        # High user impact
        if user_impact > 1000:
            return 100.0
        elif user_impact > 100:
            return 75.0
        elif user_impact > 10:
            return 50.0
        elif user_impact > 0:
            return 25.0

        # Security issues
        if "security" in tags:
            return 100.0

        return 10.0  # Default minimal impact

    def suggest_assignees(
        self, error: Exception, context: Dict[str, Any]
    ) -> List[str]:
        """Suggest assignees based on component ownership and expertise.

        Assignee suggestion based on:
        1. File ownership (git blame analysis)
        2. Component ownership (CODEOWNERS file)
        3. Recent contributors to affected files
        4. Team assignment rules

        Args:
            error: Exception that triggered issue
            context: Additional context with component/file information

        Returns:
            List of suggested GitHub usernames
        """
        assignees = []

        # Component-based assignment
        component = context.get("component", "")
        component_map = {
            "api": ["backend-team"],
            "backend": ["backend-team"],
            "frontend": ["frontend-team"],
            "ui": ["frontend-team"],
            "database": ["database-team", "backend-team"],
            "ci-cd": ["devops-team"],
            "infrastructure": ["devops-team"],
            "security": ["security-team"],
            "monitoring": ["devops-team", "backend-team"],
        }

        if component in component_map:
            assignees.extend(component_map[component])

        # File-based assignment (from stack trace)
        affected_files = context.get("affected_files", [])
        if affected_files:
            # TODO: Integrate with git blame or CODEOWNERS
            # For now, use component mapping
            pass

        return list(set(assignees))

    def calculate_sla(self, priority: IssuePriority) -> int:
        """Calculate SLA in hours based on priority level.

        SLA (Service Level Agreement) targets:
        - CRITICAL: 4 hours (immediate response required)
        - HIGH: 24 hours (next business day)
        - MEDIUM: 72 hours (3 business days)
        - LOW: 168 hours (1 week)

        Args:
            priority: Issue priority level

        Returns:
            SLA in hours
        """
        sla_map = {
            IssuePriority.CRITICAL: 4,
            IssuePriority.HIGH: 24,
            IssuePriority.MEDIUM: 72,
            IssuePriority.LOW: 168,
        }
        return sla_map.get(priority, 168)

    # Private helper methods

    def _load_default_rules(self) -> List[TriageRule]:
        """Load default triage rules for common error patterns.

        Returns:
            List of default TriageRule objects
        """
        return [
            # Timeout errors
            TriageRule(
                error_patterns=[r"timeout", r"timed out", r"deadline exceeded"],
                labels=["timeout", "performance"],
                priority=IssuePriority.HIGH,
                assignees=["backend-team"],
            ),
            # Security errors
            TriageRule(
                error_patterns=[
                    r"permission denied",
                    r"access denied",
                    r"unauthorized",
                    r"forbidden",
                    r"authentication",
                ],
                labels=["security", "access-control"],
                priority=IssuePriority.CRITICAL,
                assignees=["security-team"],
            ),
            # Type errors
            TriageRule(
                error_patterns=[r"TypeError", r"type mismatch", r"expected .* got"],
                labels=["bug", "type-safety"],
                priority=IssuePriority.MEDIUM,
            ),
            # Value errors
            TriageRule(
                error_patterns=[r"ValueError", r"invalid value", r"out of range"],
                labels=["bug", "validation"],
                priority=IssuePriority.MEDIUM,
            ),
            # Import errors
            TriageRule(
                error_patterns=[r"ImportError", r"ModuleNotFoundError", r"cannot import"],
                labels=["dependency", "build"],
                priority=IssuePriority.HIGH,
            ),
            # Network errors
            TriageRule(
                error_patterns=[
                    r"ConnectionError",
                    r"network error",
                    r"DNS",
                    r"unreachable",
                ],
                labels=["infrastructure", "network"],
                priority=IssuePriority.MEDIUM,
                assignees=["devops-team"],
            ),
            # Memory errors
            TriageRule(
                error_patterns=[r"MemoryError", r"out of memory", r"OOM"],
                labels=["performance", "memory"],
                priority=IssuePriority.CRITICAL,
                assignees=["backend-team"],
            ),
            # Database errors
            TriageRule(
                error_patterns=[
                    r"DatabaseError",
                    r"SQL",
                    r"transaction",
                    r"deadlock",
                ],
                labels=["database", "backend"],
                priority=IssuePriority.HIGH,
                assignees=["database-team"],
            ),
            # File system errors
            TriageRule(
                error_patterns=[
                    r"FileNotFoundError",
                    r"file not found",
                    r"no such file",
                    r"path does not exist",
                ],
                labels=["bug", "filesystem"],
                priority=IssuePriority.MEDIUM,
            ),
            # Data structure errors
            TriageRule(
                error_patterns=[r"KeyError", r"key not found", r"missing key"],
                labels=["bug", "data"],
                priority=IssuePriority.MEDIUM,
            ),
            # Test failures
            TriageRule(
                error_patterns=[
                    r"AssertionError",
                    r"assertion failed",
                    r"assert .* failed",
                ],
                labels=["test", "bug"],
                priority=IssuePriority.HIGH,
            ),
        ]

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the regex patterns.

        Args:
            text: Text to match against
            patterns: List of regex patterns

        Returns:
            True if any pattern matches
        """
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    def _normalize_label(self, label: str) -> str:
        """Normalize label name for GitHub.

        Args:
            label: Raw label name

        Returns:
            Normalized label (lowercase, hyphenated)
        """
        # Convert to lowercase
        label = label.lower()
        # Replace spaces with hyphens
        label = label.replace(" ", "-")
        # Remove special characters except hyphens
        label = re.sub(r"[^a-z0-9-]", "", label)
        return label

    def _priority_rank(self, priority: IssuePriority) -> int:
        """Get numeric rank for priority comparison.

        Args:
            priority: Priority level

        Returns:
            Numeric rank (higher = more urgent)
        """
        rank_map = {
            IssuePriority.CRITICAL: 4,
            IssuePriority.HIGH: 3,
            IssuePriority.MEDIUM: 2,
            IssuePriority.LOW: 1,
        }
        return rank_map.get(priority, 0)

    def _generate_title(self, error: Exception, context: Dict[str, Any]) -> str:
        """Generate concise issue title.

        Args:
            error: Exception object
            context: Additional context

        Returns:
            Issue title string
        """
        error_type = type(error).__name__
        component = context.get("component", "")
        agent_id = context.get("agent_id", "")

        if component:
            return f"[{component}] {error_type}: {str(error)[:80]}"
        elif agent_id:
            return f"[{agent_id}] {error_type}: {str(error)[:80]}"
        else:
            return f"{error_type}: {str(error)[:100]}"

    def _generate_body(self, error: Exception, context: Dict[str, Any]) -> str:
        """Generate initial issue body (will be enhanced by GitHubIssueAgent).

        Args:
            error: Exception object
            context: Additional context

        Returns:
            Issue body string
        """
        error_type = type(error).__name__
        error_message = str(error)

        body = f"""## Error

**Type**: `{error_type}`
**Message**: {error_message}

## Context

"""

        # Add context details
        for key, value in context.items():
            if key not in ["stack_trace", "environment_vars"]:
                body += f"- **{key}**: {value}\n"

        return body
