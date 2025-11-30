"""
Pattern Schema Definitions for MoAI-Flow
=========================================

Comprehensive schema definitions and validators for pattern storage.
Supports task completion, error occurrence, agent usage, and user correction patterns.
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class PatternType(str, Enum):
    """Pattern type enumeration."""
    TASK_COMPLETION = "task_completion"
    ERROR_OCCURRENCE = "error_occurrence"
    AGENT_USAGE = "agent_usage"
    USER_CORRECTION = "user_correction"


class TaskCompletionData(TypedDict, total=False):
    """
    Task completion pattern data schema.

    Captures task execution metrics and outcomes.
    """
    task_type: str  # Type of task (e.g., "code_generation", "testing", "documentation")
    agent: str  # Agent that executed the task
    duration_ms: int  # Task duration in milliseconds
    success: bool  # Whether task completed successfully
    files_created: int  # Number of files created
    files_modified: int  # Number of files modified
    tests_passed: int  # Number of tests passed
    tests_failed: int  # Number of tests failed
    lines_of_code: int  # Lines of code added/modified
    coverage_percent: Optional[float]  # Test coverage percentage
    error_message: Optional[str]  # Error message if failed
    retry_count: int  # Number of retries attempted


class ErrorOccurrenceData(TypedDict, total=False):
    """
    Error occurrence pattern data schema.

    Captures error details for pattern analysis and learning.
    """
    error_type: str  # Error type (e.g., "SyntaxError", "TypeError", "RuntimeError")
    error_message: str  # Error message
    stack_trace: str  # Full stack trace
    file_path: str  # File where error occurred
    line_number: int  # Line number where error occurred
    function_name: Optional[str]  # Function/method where error occurred
    resolution: Optional[str]  # How error was resolved
    resolution_time_ms: Optional[int]  # Time to resolution
    similar_errors_count: int  # Count of similar errors seen before
    auto_resolved: bool  # Whether error was auto-resolved
    user_intervention: bool  # Whether user intervention was required


class AgentUsageData(TypedDict, total=False):
    """
    Agent usage pattern data schema.

    Tracks agent performance and behavior patterns.
    """
    agent_type: str  # Agent type (e.g., "code-backend", "workflow-tdd")
    task_type: str  # Type of task performed
    success: bool  # Task success status
    duration_ms: int  # Task duration
    retry_count: int  # Number of retries
    tools_used: List[str]  # Tools utilized (Read, Write, Edit, Bash, etc.)
    files_accessed: int  # Number of files accessed
    api_calls: int  # Number of API calls made
    tokens_used: int  # Tokens consumed
    memory_mb: Optional[float]  # Memory usage in MB
    cpu_percent: Optional[float]  # CPU usage percentage
    parallel_tasks: int  # Number of parallel tasks executed


class UserCorrectionData(TypedDict, total=False):
    """
    User correction pattern data schema.

    Captures user corrections to learn from mistakes.
    """
    original_output: str  # Original agent output
    corrected_output: str  # User-corrected output
    correction_type: str  # Type of correction (e.g., "syntax", "logic", "style")
    agent: str  # Agent that produced original output
    task_type: str  # Type of task
    correction_category: str  # Category (e.g., "code_quality", "security", "performance")
    user_feedback: Optional[str]  # User's explanation of correction
    severity: Literal["minor", "moderate", "critical"]  # Correction severity
    pattern_matched: Optional[str]  # Existing pattern that should have prevented this


class PatternContext(TypedDict, total=False):
    """
    Pattern context metadata.

    Additional context for pattern analysis.
    """
    project_name: str  # Project identifier
    session_id: str  # Session identifier
    user_id: Optional[str]  # User identifier
    environment: Literal["development", "staging", "production"]  # Environment
    git_branch: Optional[str]  # Git branch
    git_commit: Optional[str]  # Git commit hash
    timestamp: str  # ISO 8601 timestamp
    tags: List[str]  # Custom tags for categorization
    metadata: Dict[str, Any]  # Additional metadata


class Pattern(TypedDict):
    """
    Complete pattern structure.

    Root structure for all pattern types.
    """
    pattern_id: str  # Unique pattern identifier
    pattern_type: PatternType  # Pattern type
    timestamp: str  # ISO 8601 timestamp
    data: Dict[str, Any]  # Pattern-specific data (TaskCompletionData, etc.)
    context: PatternContext  # Pattern context
    version: str  # Schema version


class PatternSchema:
    """
    Pattern schema validator.

    Validates pattern data against schema definitions.
    """

    # Required fields for each pattern type
    REQUIRED_FIELDS = {
        PatternType.TASK_COMPLETION: ["task_type", "agent", "duration_ms", "success"],
        PatternType.ERROR_OCCURRENCE: ["error_type", "error_message"],
        PatternType.AGENT_USAGE: ["agent_type", "task_type", "success", "duration_ms"],
        PatternType.USER_CORRECTION: ["original_output", "corrected_output", "correction_type", "agent"]
    }

    # Valid values for literal types
    VALID_SEVERITIES = {"minor", "moderate", "critical"}
    VALID_ENVIRONMENTS = {"development", "staging", "production"}

    @staticmethod
    def validate_task_completion(data: Dict[str, Any]) -> bool:
        """
        Validate task completion data.

        Args:
            data: Task completion data dictionary

        Returns:
            True if valid, False otherwise
        """
        required = PatternSchema.REQUIRED_FIELDS[PatternType.TASK_COMPLETION]
        if not all(field in data for field in required):
            return False

        # Type validation
        if not isinstance(data.get("task_type"), str):
            return False
        if not isinstance(data.get("agent"), str):
            return False
        if not isinstance(data.get("duration_ms"), int) or data.get("duration_ms", -1) < 0:
            return False
        if not isinstance(data.get("success"), bool):
            return False

        # Optional field validation
        if "coverage_percent" in data:
            coverage = data["coverage_percent"]
            if not isinstance(coverage, (int, float)) or not (0 <= coverage <= 100):
                return False

        return True

    @staticmethod
    def validate_error_occurrence(data: Dict[str, Any]) -> bool:
        """
        Validate error occurrence data.

        Args:
            data: Error occurrence data dictionary

        Returns:
            True if valid, False otherwise
        """
        required = PatternSchema.REQUIRED_FIELDS[PatternType.ERROR_OCCURRENCE]
        if not all(field in data for field in required):
            return False

        # Type validation
        if not isinstance(data.get("error_type"), str):
            return False
        if not isinstance(data.get("error_message"), str):
            return False

        # Optional field validation
        if "line_number" in data:
            if not isinstance(data["line_number"], int) or data["line_number"] < 0:
                return False

        return True

    @staticmethod
    def validate_agent_usage(data: Dict[str, Any]) -> bool:
        """
        Validate agent usage data.

        Args:
            data: Agent usage data dictionary

        Returns:
            True if valid, False otherwise
        """
        required = PatternSchema.REQUIRED_FIELDS[PatternType.AGENT_USAGE]
        if not all(field in data for field in required):
            return False

        # Type validation
        if not isinstance(data.get("agent_type"), str):
            return False
        if not isinstance(data.get("task_type"), str):
            return False
        if not isinstance(data.get("success"), bool):
            return False
        if not isinstance(data.get("duration_ms"), int) or data.get("duration_ms", -1) < 0:
            return False

        # Optional list validation
        if "tools_used" in data:
            if not isinstance(data["tools_used"], list):
                return False
            if not all(isinstance(tool, str) for tool in data["tools_used"]):
                return False

        return True

    @staticmethod
    def validate_user_correction(data: Dict[str, Any]) -> bool:
        """
        Validate user correction data.

        Args:
            data: User correction data dictionary

        Returns:
            True if valid, False otherwise
        """
        required = PatternSchema.REQUIRED_FIELDS[PatternType.USER_CORRECTION]
        if not all(field in data for field in required):
            return False

        # Type validation
        if not isinstance(data.get("original_output"), str):
            return False
        if not isinstance(data.get("corrected_output"), str):
            return False
        if not isinstance(data.get("correction_type"), str):
            return False
        if not isinstance(data.get("agent"), str):
            return False

        # Severity validation
        if "severity" in data:
            if data["severity"] not in PatternSchema.VALID_SEVERITIES:
                return False

        return True

    @staticmethod
    def validate_context(context: Dict[str, Any]) -> bool:
        """
        Validate pattern context.

        Args:
            context: Pattern context dictionary

        Returns:
            True if valid, False otherwise
        """
        # Environment validation
        if "environment" in context:
            if context["environment"] not in PatternSchema.VALID_ENVIRONMENTS:
                return False

        # Tags validation
        if "tags" in context:
            if not isinstance(context["tags"], list):
                return False
            if not all(isinstance(tag, str) for tag in context["tags"]):
                return False

        # Timestamp validation
        if "timestamp" in context:
            try:
                datetime.fromisoformat(context["timestamp"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return False

        return True

    @staticmethod
    def validate_pattern(pattern: Dict[str, Any]) -> bool:
        """
        Validate complete pattern structure.

        Args:
            pattern: Complete pattern dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check required root fields
        required_root = ["pattern_id", "pattern_type", "timestamp", "data"]
        if not all(field in pattern for field in required_root):
            return False

        # Validate pattern type
        try:
            pattern_type = PatternType(pattern["pattern_type"])
        except ValueError:
            return False

        # Validate timestamp
        try:
            datetime.fromisoformat(pattern["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False

        # Validate context if present
        if "context" in pattern:
            if not PatternSchema.validate_context(pattern["context"]):
                return False

        # Validate pattern-specific data
        data = pattern["data"]
        validators = {
            PatternType.TASK_COMPLETION: PatternSchema.validate_task_completion,
            PatternType.ERROR_OCCURRENCE: PatternSchema.validate_error_occurrence,
            PatternType.AGENT_USAGE: PatternSchema.validate_agent_usage,
            PatternType.USER_CORRECTION: PatternSchema.validate_user_correction
        }

        validator = validators.get(pattern_type)
        if validator and not validator(data):
            return False

        return True


__all__ = [
    "PatternType",
    "TaskCompletionData",
    "ErrorOccurrenceData",
    "AgentUsageData",
    "UserCorrectionData",
    "PatternContext",
    "Pattern",
    "PatternSchema"
]
