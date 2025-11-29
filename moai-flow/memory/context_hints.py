#!/usr/bin/env python3
"""
ContextHints - Session-Level User Preference and Workflow Pattern Management

Manages adaptive assistance through:
- User expertise level tracking (beginner, intermediate, expert)
- Preferred workflow patterns (TDD, documentation-first, implementation-first)
- Communication preferences (verbose, concise, balanced)
- Recent task pattern recognition
- Tool usage preference tracking
- Intelligent next-action suggestions

Architecture:
- Persistence via SwarmDB session_memory table
- Pattern learning from last 100 tasks
- Adaptive suggestion engine based on historical patterns
- Session-scoped preferences with optional TTL

Integration:
- Namespace: context_hints:{session_id}
- Storage: JSON-serialized preferences and patterns
- Memory Type: 'context_hint' in SwarmDB

Version: 1.0.0
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from .swarm_db import SwarmDB


# ============================================================================
# Preference Categories and Constants
# ============================================================================

class PreferenceCategory(str, Enum):
    """Preference category types"""
    COMMUNICATION = "communication"  # verbose, concise, balanced
    WORKFLOW = "workflow"  # tdd, doc-first, impl-first
    VALIDATION = "validation"  # strict, moderate, relaxed
    EXPERTISE = "expertise"  # beginner, intermediate, expert
    TOOLS = "tools"  # preferred tool usage patterns


class ExpertiseLevel(str, Enum):
    """User expertise levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class WorkflowPreference(str, Enum):
    """Workflow preference types"""
    TDD = "tdd"
    DOC_FIRST = "doc-first"
    IMPL_FIRST = "impl-first"
    ITERATIVE = "iterative"


class CommunicationStyle(str, Enum):
    """Communication style preferences"""
    VERBOSE = "verbose"
    CONCISE = "concise"
    BALANCED = "balanced"


class ValidationStrictness(str, Enum):
    """Validation strictness levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    RELAXED = "relaxed"


# Default preferences
DEFAULT_PREFERENCES = {
    PreferenceCategory.COMMUNICATION: CommunicationStyle.BALANCED,
    PreferenceCategory.WORKFLOW: WorkflowPreference.TDD,
    PreferenceCategory.VALIDATION: ValidationStrictness.MODERATE,
    PreferenceCategory.EXPERTISE: ExpertiseLevel.INTERMEDIATE,
}

# Pattern learning constants
MAX_TASK_HISTORY = 100
PATTERN_CONFIDENCE_THRESHOLD = 0.7
SUGGESTION_DECAY_HOURS = 24


# ============================================================================
# ContextHints Implementation
# ============================================================================

class ContextHints:
    """
    Session-level context and user preference management.

    Stores and retrieves hints about:
    - User expertise level (beginner, intermediate, expert)
    - Preferred workflows (TDD, documentation-first, etc.)
    - Communication preferences (verbose, concise)
    - Recent task patterns
    - Tool usage preferences

    Example:
        >>> db = SwarmDB()
        >>> hints = ContextHints(db, session_id="session-123")
        >>>
        >>> # Set preferences
        >>> hints.set_preference("communication", "concise")
        >>> hints.set_expertise_level("expert")
        >>>
        >>> # Record task patterns
        >>> hints.record_task_pattern("implementation", {
        ...     "spec_id": "SPEC-001",
        ...     "agents_used": ["expert-backend", "manager-tdd"],
        ...     "success": True
        ... })
        >>>
        >>> # Get suggestions
        >>> next_action = hints.suggest_next_action()
    """

    def __init__(self, swarm_db: SwarmDB, session_id: str):
        """
        Initialize ContextHints

        Args:
            swarm_db: SwarmDB instance for persistence
            session_id: Unique session identifier
        """
        self.db = swarm_db
        self.session_id = session_id
        self.logger = logging.getLogger(__name__)

        # Memory namespace for this session
        self.namespace = f"context_hints:{session_id}"

        # Initialize preferences if not exists
        self._initialize_preferences()

    def _initialize_preferences(self) -> None:
        """Initialize default preferences if they don't exist"""
        for category, default_value in DEFAULT_PREFERENCES.items():
            existing = self.get_preference(category)
            if existing is None:
                self.set_preference(category, default_value)

    def _get_key(self, key: str) -> str:
        """Generate namespaced key"""
        return f"{self.namespace}:{key}"

    # ========================================================================
    # Preference Management
    # ========================================================================

    def set_preference(self, key: str, value: Any, ttl_hours: Optional[int] = None) -> None:
        """
        Set user preference

        Args:
            key: Preference key (use PreferenceCategory for standard keys)
            value: Preference value
            ttl_hours: Time-to-live in hours (None = permanent)

        Example:
            >>> hints.set_preference("communication", "verbose")
            >>> hints.set_preference("custom_setting", {"enabled": True}, ttl_hours=24)
        """
        try:
            self.db.store_memory(
                session_id=self.session_id,
                memory_type="context_hint",
                key=self._get_key(f"pref:{key}"),
                value=value,
                ttl_hours=ttl_hours
            )
            self.logger.debug(f"Set preference: {key} = {value}")
        except Exception as e:
            self.logger.error(f"Failed to set preference {key}: {e}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get user preference

        Args:
            key: Preference key
            default: Default value if preference not found

        Returns:
            Preference value or default

        Example:
            >>> style = hints.get_preference("communication", "balanced")
        """
        try:
            value = self.db.get_memory(
                session_id=self.session_id,
                memory_type="context_hint",
                key=self._get_key(f"pref:{key}")
            )
            return value if value is not None else default
        except Exception as e:
            self.logger.error(f"Failed to get preference {key}: {e}")
            return default

    def get_all_preferences(self) -> Dict[str, Any]:
        """
        Get all user preferences

        Returns:
            Dictionary of all preferences
        """
        preferences = {}
        for category in PreferenceCategory:
            value = self.get_preference(category)
            if value is not None:
                preferences[category] = value
        return preferences

    # ========================================================================
    # Expertise Level Management
    # ========================================================================

    def set_expertise_level(self, level: str) -> None:
        """
        Set user expertise level

        Args:
            level: ExpertiseLevel value (beginner, intermediate, expert)

        Example:
            >>> hints.set_expertise_level("expert")
        """
        if level not in [e.value for e in ExpertiseLevel]:
            self.logger.warning(f"Invalid expertise level: {level}")
            return

        self.set_preference(PreferenceCategory.EXPERTISE, level)

    def get_expertise_level(self) -> str:
        """
        Get user expertise level

        Returns:
            ExpertiseLevel value (default: intermediate)

        Example:
            >>> level = hints.get_expertise_level()  # 'intermediate'
        """
        return self.get_preference(
            PreferenceCategory.EXPERTISE,
            default=ExpertiseLevel.INTERMEDIATE
        )

    # ========================================================================
    # Task Pattern Recording
    # ========================================================================

    def record_task_pattern(self, task_type: str, metadata: Dict) -> None:
        """
        Record task pattern for learning

        Args:
            task_type: Type of task (e.g., 'implementation', 'planning', 'debugging')
            metadata: Task metadata including:
                - spec_id: SPEC identifier (optional)
                - agents_used: List of agent types used
                - success: Boolean success indicator
                - duration_ms: Task duration in milliseconds (optional)
                - tools_used: List of tools used (optional)
                - workflow: Workflow type used (optional)

        Example:
            >>> hints.record_task_pattern("implementation", {
            ...     "spec_id": "SPEC-001",
            ...     "agents_used": ["expert-backend", "manager-tdd"],
            ...     "success": True,
            ...     "duration_ms": 5000,
            ...     "workflow": "tdd"
            ... })
        """
        try:
            # Get current task history
            history = self._get_task_history()

            # Add new task with timestamp
            task_record = {
                "task_type": task_type,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
            history.append(task_record)

            # Keep only last MAX_TASK_HISTORY tasks
            if len(history) > MAX_TASK_HISTORY:
                history = history[-MAX_TASK_HISTORY:]

            # Store updated history
            self.db.store_memory(
                session_id=self.session_id,
                memory_type="context_hint",
                key=self._get_key("task_history"),
                value=history
            )

            self.logger.debug(f"Recorded task pattern: {task_type}")

            # Update tool usage statistics if provided
            if "tools_used" in metadata:
                for tool in metadata["tools_used"]:
                    self.record_tool_usage(tool)

        except Exception as e:
            self.logger.error(f"Failed to record task pattern: {e}")

    def _get_task_history(self) -> List[Dict]:
        """Get task history from storage"""
        try:
            history = self.db.get_memory(
                session_id=self.session_id,
                memory_type="context_hint",
                key=self._get_key("task_history")
            )
            return history if history else []
        except Exception as e:
            self.logger.error(f"Failed to get task history: {e}")
            return []

    def get_task_patterns(self, limit: int = 10) -> List[Dict]:
        """
        Get recent task patterns

        Args:
            limit: Maximum number of patterns to return

        Returns:
            List of recent task pattern dictionaries

        Example:
            >>> patterns = hints.get_task_patterns(limit=5)
            >>> for pattern in patterns:
            ...     print(pattern['task_type'], pattern['timestamp'])
        """
        history = self._get_task_history()
        return history[-limit:] if history else []

    # ========================================================================
    # Tool Usage Tracking
    # ========================================================================

    def record_tool_usage(self, tool_name: str) -> None:
        """
        Record tool usage for preference learning

        Args:
            tool_name: Name of tool used

        Example:
            >>> hints.record_tool_usage("expert-backend")
            >>> hints.record_tool_usage("manager-tdd")
        """
        try:
            # Get current tool stats
            tool_stats = self._get_tool_stats()

            # Increment usage count
            tool_stats[tool_name] = tool_stats.get(tool_name, 0) + 1

            # Store updated stats
            self.db.store_memory(
                session_id=self.session_id,
                memory_type="context_hint",
                key=self._get_key("tool_stats"),
                value=tool_stats
            )

            self.logger.debug(f"Recorded tool usage: {tool_name}")

        except Exception as e:
            self.logger.error(f"Failed to record tool usage: {e}")

    def _get_tool_stats(self) -> Dict[str, int]:
        """Get tool usage statistics"""
        try:
            stats = self.db.get_memory(
                session_id=self.session_id,
                memory_type="context_hint",
                key=self._get_key("tool_stats")
            )
            return stats if stats else {}
        except Exception as e:
            self.logger.error(f"Failed to get tool stats: {e}")
            return {}

    def get_tool_preferences(self) -> Dict[str, int]:
        """
        Get tool usage preferences

        Returns:
            Dictionary mapping tool names to usage counts

        Example:
            >>> prefs = hints.get_tool_preferences()
            >>> # {'expert-backend': 15, 'manager-tdd': 12, ...}
        """
        return self._get_tool_stats()

    def get_most_used_tools(self, limit: int = 5) -> List[tuple]:
        """
        Get most frequently used tools

        Args:
            limit: Number of tools to return

        Returns:
            List of (tool_name, usage_count) tuples

        Example:
            >>> top_tools = hints.get_most_used_tools(3)
            >>> # [('expert-backend', 15), ('manager-tdd', 12), ...]
        """
        stats = self._get_tool_stats()
        return Counter(stats).most_common(limit)

    # ========================================================================
    # Pattern Analysis and Suggestions
    # ========================================================================

    def suggest_next_action(self) -> Optional[str]:
        """
        Suggest next action based on task patterns

        Analyzes recent task history to predict likely next steps.

        Returns:
            Suggested next action string or None

        Example:
            >>> suggestion = hints.suggest_next_action()
            >>> # "Run /moai:3-sync to document recent implementation"
        """
        try:
            history = self._get_task_history()
            if not history:
                return None

            # Get recent tasks (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=SUGGESTION_DECAY_HOURS)
            recent_tasks = [
                task for task in history
                if datetime.fromisoformat(task["timestamp"]) > recent_cutoff
            ]

            if not recent_tasks:
                return None

            # Analyze patterns
            last_task = recent_tasks[-1]
            task_type = last_task.get("task_type")

            # Pattern-based suggestions
            if task_type == "implementation":
                # After implementation, suggest testing or documentation
                if last_task.get("success"):
                    return "Run /moai:3-sync to document recent implementation"
                else:
                    return "Debug implementation issues or run tests"

            elif task_type == "planning":
                # After planning, suggest implementation
                spec_id = last_task.get("spec_id")
                if spec_id:
                    return f"Run /moai:2-run {spec_id} to start implementation"
                else:
                    return "Start implementation phase"

            elif task_type == "testing":
                # After testing, suggest fixes or documentation
                if last_task.get("success"):
                    return "All tests passing - consider documentation or next feature"
                else:
                    return "Fix failing tests"

            elif task_type == "documentation":
                # After documentation, suggest next feature or review
                return "Documentation complete - start next feature or create PR"

            # Default: check workflow preference
            workflow = self.get_preference(PreferenceCategory.WORKFLOW)
            if workflow == WorkflowPreference.TDD:
                return "Write tests first, then implement"

            return None

        except Exception as e:
            self.logger.error(f"Failed to suggest next action: {e}")
            return None

    def analyze_workflow_patterns(self) -> Dict[str, Any]:
        """
        Analyze workflow patterns from task history

        Returns:
            Dictionary with pattern analysis:
                - common_sequences: Most common task sequences
                - success_rate: Success rate by task type
                - preferred_agents: Most frequently used agents
                - average_duration: Average task duration by type

        Example:
            >>> analysis = hints.analyze_workflow_patterns()
            >>> print(f"Success rate: {analysis['success_rate']}")
        """
        try:
            history = self._get_task_history()
            if not history:
                return {}

            # Analyze success rates by task type
            success_by_type = defaultdict(list)
            for task in history:
                if "success" in task:
                    success_by_type[task["task_type"]].append(task["success"])

            success_rate = {
                task_type: sum(successes) / len(successes)
                for task_type, successes in success_by_type.items()
            }

            # Find common task sequences
            sequences = []
            for i in range(len(history) - 1):
                sequence = (history[i]["task_type"], history[i + 1]["task_type"])
                sequences.append(sequence)

            common_sequences = Counter(sequences).most_common(5)

            # Find preferred agents
            all_agents = []
            for task in history:
                agents = task.get("agents_used", [])
                all_agents.extend(agents)

            preferred_agents = Counter(all_agents).most_common(5)

            # Calculate average duration by task type
            durations_by_type = defaultdict(list)
            for task in history:
                if "duration_ms" in task:
                    durations_by_type[task["task_type"]].append(task["duration_ms"])

            average_duration = {
                task_type: sum(durations) / len(durations)
                for task_type, durations in durations_by_type.items()
            }

            return {
                "common_sequences": common_sequences,
                "success_rate": success_rate,
                "preferred_agents": preferred_agents,
                "average_duration": average_duration,
                "total_tasks": len(history)
            }

        except Exception as e:
            self.logger.error(f"Failed to analyze patterns: {e}")
            return {}

    # ========================================================================
    # Context Adaptation
    # ========================================================================

    def should_show_verbose_output(self) -> bool:
        """
        Determine if verbose output should be shown

        Returns:
            True if verbose output preferred, False otherwise
        """
        comm_style = self.get_preference(PreferenceCategory.COMMUNICATION)
        expertise = self.get_expertise_level()

        # Verbose if:
        # - Explicitly set to verbose, OR
        # - Beginner level with balanced style
        return (
            comm_style == CommunicationStyle.VERBOSE or
            (expertise == ExpertiseLevel.BEGINNER and
             comm_style != CommunicationStyle.CONCISE)
        )

    def should_enforce_strict_validation(self) -> bool:
        """
        Determine if strict validation should be enforced

        Returns:
            True if strict validation preferred, False otherwise
        """
        validation = self.get_preference(PreferenceCategory.VALIDATION)
        return validation == ValidationStrictness.STRICT

    def get_recommended_workflow(self) -> str:
        """
        Get recommended workflow based on preferences and patterns

        Returns:
            Recommended workflow type
        """
        # Check explicit preference first
        workflow_pref = self.get_preference(PreferenceCategory.WORKFLOW)
        if workflow_pref:
            return workflow_pref

        # Analyze patterns to infer workflow
        analysis = self.analyze_workflow_patterns()
        sequences = analysis.get("common_sequences", [])

        # Look for TDD pattern (testing before implementation)
        for (first, second), count in sequences:
            if first == "testing" and second == "implementation":
                return WorkflowPreference.TDD

        return WorkflowPreference.ITERATIVE


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== ContextHints Example Usage ===\n")

    # Initialize
    db = SwarmDB()
    hints = ContextHints(db, session_id="example-session-001")
    print("✓ ContextHints initialized")

    # Example 1: Set preferences
    print("\n--- Example 1: Set Preferences ---")
    hints.set_preference(PreferenceCategory.COMMUNICATION, CommunicationStyle.CONCISE)
    hints.set_preference(PreferenceCategory.WORKFLOW, WorkflowPreference.TDD)
    hints.set_expertise_level(ExpertiseLevel.EXPERT)
    print("✓ Preferences set")
    print(f"  Communication: {hints.get_preference(PreferenceCategory.COMMUNICATION)}")
    print(f"  Workflow: {hints.get_preference(PreferenceCategory.WORKFLOW)}")
    print(f"  Expertise: {hints.get_expertise_level()}")

    # Example 2: Record task patterns
    print("\n--- Example 2: Record Task Patterns ---")
    hints.record_task_pattern("planning", {
        "spec_id": "SPEC-001",
        "agents_used": ["manager-spec"],
        "success": True,
        "duration_ms": 2000
    })
    hints.record_task_pattern("implementation", {
        "spec_id": "SPEC-001",
        "agents_used": ["expert-backend", "manager-tdd"],
        "success": True,
        "duration_ms": 5000,
        "tools_used": ["expert-backend", "manager-tdd"]
    })
    print("✓ Task patterns recorded")

    # Example 3: Get task patterns
    print("\n--- Example 3: Get Task Patterns ---")
    patterns = hints.get_task_patterns(limit=5)
    print(f"✓ Retrieved {len(patterns)} task patterns")
    for pattern in patterns:
        print(f"  - {pattern['task_type']} @ {pattern['timestamp']}")

    # Example 4: Tool preferences
    print("\n--- Example 4: Tool Preferences ---")
    tool_prefs = hints.get_tool_preferences()
    print(f"✓ Tool usage statistics: {tool_prefs}")
    most_used = hints.get_most_used_tools(3)
    print(f"✓ Most used tools: {most_used}")

    # Example 5: Next action suggestion
    print("\n--- Example 5: Next Action Suggestion ---")
    suggestion = hints.suggest_next_action()
    if suggestion:
        print(f"✓ Suggested next action: {suggestion}")
    else:
        print("  No suggestion available")

    # Example 6: Workflow analysis
    print("\n--- Example 6: Workflow Analysis ---")
    analysis = hints.analyze_workflow_patterns()
    print(f"✓ Workflow analysis:")
    print(f"  Total tasks: {analysis.get('total_tasks', 0)}")
    print(f"  Success rates: {analysis.get('success_rate', {})}")
    print(f"  Common sequences: {analysis.get('common_sequences', [])[:2]}")

    # Example 7: Context adaptation
    print("\n--- Example 7: Context Adaptation ---")
    print(f"✓ Show verbose output: {hints.should_show_verbose_output()}")
    print(f"✓ Enforce strict validation: {hints.should_enforce_strict_validation()}")
    print(f"✓ Recommended workflow: {hints.get_recommended_workflow()}")

    # Cleanup
    db.close()
    print("\n✅ ContextHints demonstration complete")
