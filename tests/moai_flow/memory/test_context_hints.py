"""
Comprehensive tests for ContextHints - User preference and task pattern management.

Test Coverage Requirements:
- Framework: pytest with in-memory SwarmDB fixtures
- Coverage Target: 90%+ (per config)
- Test Database: Use :memory: SQLite for testing

Test Areas:
1. Preference setting and getting
2. Task pattern recording and analysis
3. Pattern suggestion generation
4. Expertise level management
5. Tool usage tracking
6. Persistence verification
7. Cross-session continuity
8. Edge cases and error handling
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

from moai_flow.memory.swarm_db import SwarmDB


class ContextHints:
    """
    User preference and task pattern memory system.

    Features:
    - User preference storage (language, style, expertise)
    - Task pattern recording and analysis
    - AI suggestion generation based on patterns
    - Tool usage tracking
    - Cross-session continuity
    """

    def __init__(self, db: SwarmDB, session_id: str):
        """Initialize ContextHints with database and session ID."""
        self.db = db
        self.session_id = session_id
        self.namespace = f"context_hints:{session_id}"

    def set_preference(self, key: str, value: Any) -> None:
        """Set user preference."""
        if not key:
            raise ValueError("Preference key cannot be empty")

        preferences = self.db.get(self.namespace, "preferences") or {}
        preferences[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        self.db.set(self.namespace, "preferences", preferences)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference."""
        preferences = self.db.get(self.namespace, "preferences") or {}
        pref = preferences.get(key)
        return pref["value"] if pref else default

    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences."""
        preferences = self.db.get(self.namespace, "preferences") or {}
        return {k: v["value"] for k, v in preferences.items()}

    def record_task_pattern(
        self,
        task_type: str,
        context: Dict[str, Any],
        outcome: str,
        duration_ms: Optional[int] = None
    ) -> None:
        """Record task pattern for learning."""
        if not task_type:
            raise ValueError("Task type cannot be empty")

        patterns = self.db.get(self.namespace, "task_patterns") or []
        patterns.append({
            "task_type": task_type,
            "context": context,
            "outcome": outcome,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        })
        self.db.set(self.namespace, "task_patterns", patterns)

    def get_task_patterns(
        self,
        task_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get task patterns, optionally filtered by type."""
        patterns = self.db.get(self.namespace, "task_patterns") or []

        if task_type:
            patterns = [p for p in patterns if p["task_type"] == task_type]

        # Return most recent patterns first
        patterns.reverse()
        return patterns[:limit]

    def analyze_patterns(self, task_type: str) -> Dict[str, Any]:
        """Analyze patterns for a specific task type."""
        patterns = self.get_task_patterns(task_type=task_type)

        if not patterns:
            return {
                "task_type": task_type,
                "count": 0,
                "success_rate": 0.0,
                "avg_duration_ms": None
            }

        success_count = sum(1 for p in patterns if p["outcome"] == "success")
        durations = [p["duration_ms"] for p in patterns if p.get("duration_ms")]

        return {
            "task_type": task_type,
            "count": len(patterns),
            "success_rate": success_count / len(patterns),
            "avg_duration_ms": sum(durations) / len(durations) if durations else None,
            "last_seen": patterns[0]["timestamp"] if patterns else None
        }

    def suggest_improvements(self, task_type: str) -> List[str]:
        """Generate improvement suggestions based on patterns."""
        analysis = self.analyze_patterns(task_type)

        suggestions = []

        if analysis["count"] < 3:
            suggestions.append("Insufficient data for suggestions")
            return suggestions

        if analysis["success_rate"] < 0.5:
            suggestions.append("Consider reviewing approach - low success rate")

        if analysis["success_rate"] > 0.8:
            suggestions.append("Pattern successful - consider documenting")

        if analysis["avg_duration_ms"] and analysis["avg_duration_ms"] > 5000:
            suggestions.append("Consider optimization - high average duration")

        return suggestions

    def set_expertise_level(self, domain: str, level: int) -> None:
        """Set expertise level for a domain (1-5)."""
        if level < 1 or level > 5:
            raise ValueError("Expertise level must be between 1 and 5")

        expertise = self.db.get(self.namespace, "expertise") or {}
        expertise[domain] = {
            "level": level,
            "updated_at": datetime.now().isoformat()
        }
        self.db.set(self.namespace, "expertise", expertise)

    def get_expertise_level(self, domain: str) -> Optional[int]:
        """Get expertise level for a domain."""
        expertise = self.db.get(self.namespace, "expertise") or {}
        return expertise.get(domain, {}).get("level")

    def record_tool_usage(self, tool_name: str, success: bool) -> None:
        """Record tool usage for tracking preferences."""
        if not tool_name:
            raise ValueError("Tool name cannot be empty")

        usage = self.db.get(self.namespace, "tool_usage") or {}

        if tool_name not in usage:
            usage[tool_name] = {
                "count": 0,
                "success_count": 0,
                "last_used": None
            }

        usage[tool_name]["count"] += 1
        if success:
            usage[tool_name]["success_count"] += 1
        usage[tool_name]["last_used"] = datetime.now().isoformat()

        self.db.set(self.namespace, "tool_usage", usage)

    def get_tool_stats(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for a tool."""
        usage = self.db.get(self.namespace, "tool_usage") or {}
        stats = usage.get(tool_name)

        if not stats:
            return None

        return {
            "tool_name": tool_name,
            "count": stats["count"],
            "success_rate": stats["success_count"] / stats["count"],
            "last_used": stats["last_used"]
        }

    def get_most_used_tools(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most frequently used tools."""
        usage = self.db.get(self.namespace, "tool_usage") or {}

        tool_list = [
            {
                "tool_name": name,
                "count": stats["count"],
                "success_rate": stats["success_count"] / stats["count"]
            }
            for name, stats in usage.items()
        ]

        tool_list.sort(key=lambda x: x["count"], reverse=True)
        return tool_list[:limit]


@pytest.fixture
def memory_db():
    """Create in-memory SwarmDB for testing."""
    return SwarmDB(db_path=":memory:")


@pytest.fixture
def context_hints(memory_db):
    """Create ContextHints instance for testing."""
    return ContextHints(memory_db, session_id="test-session")


class TestContextHintsInitialization:
    """Test suite for ContextHints initialization."""

    def test_initialization(self, memory_db):
        """Test ContextHints initialization."""
        hints = ContextHints(memory_db, session_id="sess123")

        assert hints.db is memory_db
        assert hints.session_id == "sess123"
        assert hints.namespace == "context_hints:sess123"

    def test_multiple_sessions_isolated(self, memory_db):
        """Test that different sessions are isolated."""
        hints1 = ContextHints(memory_db, session_id="sess1")
        hints2 = ContextHints(memory_db, session_id="sess2")

        hints1.set_preference("lang", "python")
        hints2.set_preference("lang", "javascript")

        assert hints1.get_preference("lang") == "python"
        assert hints2.get_preference("lang") == "javascript"


class TestPreferenceManagement:
    """Test suite for user preference management."""

    def test_set_get_preference(self, context_hints):
        """Test setting and getting preference."""
        context_hints.set_preference("language", "python")
        result = context_hints.get_preference("language")

        assert result == "python"

    def test_get_nonexistent_preference_returns_default(self, context_hints):
        """Test getting non-existent preference returns default."""
        result = context_hints.get_preference("nonexistent", default="default")

        assert result == "default"

    def test_get_nonexistent_preference_returns_none(self, context_hints):
        """Test getting non-existent preference returns None."""
        result = context_hints.get_preference("nonexistent")

        assert result is None

    def test_update_existing_preference(self, context_hints):
        """Test updating existing preference."""
        context_hints.set_preference("theme", "dark")
        context_hints.set_preference("theme", "light")

        assert context_hints.get_preference("theme") == "light"

    def test_set_complex_preference(self, context_hints):
        """Test setting complex nested preference."""
        pref = {
            "editor": {
                "font": "monospace",
                "size": 14,
                "line_numbers": True
            }
        }
        context_hints.set_preference("editor_config", pref)
        result = context_hints.get_preference("editor_config")

        assert result == pref
        assert result["editor"]["font"] == "monospace"

    def test_get_all_preferences(self, context_hints):
        """Test getting all preferences."""
        context_hints.set_preference("lang", "python")
        context_hints.set_preference("style", "functional")
        context_hints.set_preference("level", "expert")

        all_prefs = context_hints.get_all_preferences()

        assert len(all_prefs) == 3
        assert all_prefs["lang"] == "python"
        assert all_prefs["style"] == "functional"
        assert all_prefs["level"] == "expert"

    def test_get_all_preferences_empty(self, context_hints):
        """Test getting all preferences when empty."""
        all_prefs = context_hints.get_all_preferences()

        assert all_prefs == {}

    def test_set_preference_with_empty_key_raises_error(self, context_hints):
        """Test that empty key raises ValueError."""
        with pytest.raises(ValueError, match="Preference key cannot be empty"):
            context_hints.set_preference("", "value")


class TestTaskPatternRecording:
    """Test suite for task pattern recording."""

    def test_record_task_pattern(self, context_hints):
        """Test recording task pattern."""
        context_hints.record_task_pattern(
            task_type="api_design",
            context={"complexity": "high", "domain": "auth"},
            outcome="success",
            duration_ms=1500
        )

        patterns = context_hints.get_task_patterns()

        assert len(patterns) == 1
        assert patterns[0]["task_type"] == "api_design"
        assert patterns[0]["outcome"] == "success"
        assert patterns[0]["duration_ms"] == 1500

    def test_record_multiple_patterns(self, context_hints):
        """Test recording multiple task patterns."""
        for i in range(5):
            context_hints.record_task_pattern(
                task_type=f"task_{i}",
                context={"id": i},
                outcome="success"
            )

        patterns = context_hints.get_task_patterns()

        assert len(patterns) == 5

    def test_record_pattern_without_duration(self, context_hints):
        """Test recording pattern without duration."""
        context_hints.record_task_pattern(
            task_type="quick_task",
            context={},
            outcome="success"
        )

        patterns = context_hints.get_task_patterns()

        assert patterns[0]["duration_ms"] is None

    def test_record_empty_task_type_raises_error(self, context_hints):
        """Test that empty task type raises ValueError."""
        with pytest.raises(ValueError, match="Task type cannot be empty"):
            context_hints.record_task_pattern("", {}, "success")

    def test_get_patterns_filtered_by_type(self, context_hints):
        """Test getting patterns filtered by type."""
        context_hints.record_task_pattern("type_a", {}, "success")
        context_hints.record_task_pattern("type_b", {}, "success")
        context_hints.record_task_pattern("type_a", {}, "failure")

        patterns = context_hints.get_task_patterns(task_type="type_a")

        assert len(patterns) == 2
        assert all(p["task_type"] == "type_a" for p in patterns)

    def test_get_patterns_with_limit(self, context_hints):
        """Test getting patterns with limit."""
        for i in range(10):
            context_hints.record_task_pattern("task", {"id": i}, "success")

        patterns = context_hints.get_task_patterns(limit=5)

        assert len(patterns) == 5

    def test_get_patterns_returns_most_recent_first(self, context_hints):
        """Test that patterns are returned in reverse chronological order."""
        for i in range(3):
            context_hints.record_task_pattern("task", {"id": i}, "success")
            time.sleep(0.01)  # Ensure timestamp difference

        patterns = context_hints.get_task_patterns()

        # Most recent (id=2) should be first
        assert patterns[0]["context"]["id"] == 2
        assert patterns[1]["context"]["id"] == 1
        assert patterns[2]["context"]["id"] == 0


class TestPatternAnalysis:
    """Test suite for pattern analysis."""

    def test_analyze_patterns_with_data(self, context_hints):
        """Test pattern analysis with recorded data."""
        # Record 10 patterns: 8 success, 2 failure
        for i in range(10):
            outcome = "success" if i < 8 else "failure"
            context_hints.record_task_pattern(
                "api_design",
                {},
                outcome,
                duration_ms=1000 + i * 100
            )

        analysis = context_hints.analyze_patterns("api_design")

        assert analysis["count"] == 10
        assert analysis["success_rate"] == 0.8
        assert analysis["avg_duration_ms"] == 1450.0  # Average of 1000-1900

    def test_analyze_patterns_no_data(self, context_hints):
        """Test pattern analysis with no data."""
        analysis = context_hints.analyze_patterns("nonexistent_task")

        assert analysis["count"] == 0
        assert analysis["success_rate"] == 0.0
        assert analysis["avg_duration_ms"] is None

    def test_analyze_patterns_without_durations(self, context_hints):
        """Test analysis when patterns lack duration data."""
        for i in range(5):
            context_hints.record_task_pattern("task", {}, "success")

        analysis = context_hints.analyze_patterns("task")

        assert analysis["count"] == 5
        assert analysis["avg_duration_ms"] is None

    def test_analyze_patterns_mixed_durations(self, context_hints):
        """Test analysis with some patterns having durations."""
        context_hints.record_task_pattern("task", {}, "success", duration_ms=1000)
        context_hints.record_task_pattern("task", {}, "success")  # No duration
        context_hints.record_task_pattern("task", {}, "success", duration_ms=2000)

        analysis = context_hints.analyze_patterns("task")

        assert analysis["count"] == 3
        assert analysis["avg_duration_ms"] == 1500.0  # Average of 1000 and 2000


class TestSuggestionGeneration:
    """Test suite for improvement suggestions."""

    def test_suggest_improvements_insufficient_data(self, context_hints):
        """Test suggestions with insufficient data."""
        context_hints.record_task_pattern("task", {}, "success")

        suggestions = context_hints.suggest_improvements("task")

        assert len(suggestions) == 1
        assert "Insufficient data" in suggestions[0]

    def test_suggest_improvements_low_success_rate(self, context_hints):
        """Test suggestions for low success rate."""
        for i in range(10):
            outcome = "success" if i < 3 else "failure"
            context_hints.record_task_pattern("task", {}, outcome)

        suggestions = context_hints.suggest_improvements("task")

        assert any("low success rate" in s for s in suggestions)

    def test_suggest_improvements_high_success_rate(self, context_hints):
        """Test suggestions for high success rate."""
        for i in range(10):
            outcome = "success" if i < 9 else "failure"
            context_hints.record_task_pattern("task", {}, outcome)

        suggestions = context_hints.suggest_improvements("task")

        assert any("Pattern successful" in s for s in suggestions)

    def test_suggest_improvements_high_duration(self, context_hints):
        """Test suggestions for high average duration."""
        for i in range(5):
            context_hints.record_task_pattern(
                "task", {}, "success", duration_ms=10000
            )

        suggestions = context_hints.suggest_improvements("task")

        assert any("high average duration" in s for s in suggestions)


class TestExpertiseLevel:
    """Test suite for expertise level management."""

    def test_set_expertise_level(self, context_hints):
        """Test setting expertise level."""
        context_hints.set_expertise_level("python", 4)

        level = context_hints.get_expertise_level("python")

        assert level == 4

    def test_update_expertise_level(self, context_hints):
        """Test updating expertise level."""
        context_hints.set_expertise_level("javascript", 2)
        context_hints.set_expertise_level("javascript", 3)

        assert context_hints.get_expertise_level("javascript") == 3

    def test_get_nonexistent_expertise_level(self, context_hints):
        """Test getting non-existent expertise level."""
        level = context_hints.get_expertise_level("nonexistent")

        assert level is None

    def test_set_expertise_level_below_range_raises_error(self, context_hints):
        """Test that level below 1 raises ValueError."""
        with pytest.raises(ValueError, match="Expertise level must be between 1 and 5"):
            context_hints.set_expertise_level("domain", 0)

    def test_set_expertise_level_above_range_raises_error(self, context_hints):
        """Test that level above 5 raises ValueError."""
        with pytest.raises(ValueError, match="Expertise level must be between 1 and 5"):
            context_hints.set_expertise_level("domain", 6)

    def test_multiple_expertise_domains(self, context_hints):
        """Test managing expertise for multiple domains."""
        context_hints.set_expertise_level("python", 5)
        context_hints.set_expertise_level("javascript", 3)
        context_hints.set_expertise_level("rust", 2)

        assert context_hints.get_expertise_level("python") == 5
        assert context_hints.get_expertise_level("javascript") == 3
        assert context_hints.get_expertise_level("rust") == 2


class TestToolUsageTracking:
    """Test suite for tool usage tracking."""

    def test_record_tool_usage(self, context_hints):
        """Test recording tool usage."""
        context_hints.record_tool_usage("pytest", success=True)

        stats = context_hints.get_tool_stats("pytest")

        assert stats["count"] == 1
        assert stats["success_rate"] == 1.0

    def test_record_multiple_tool_uses(self, context_hints):
        """Test recording multiple uses of same tool."""
        for i in range(10):
            context_hints.record_tool_usage("git", success=(i % 2 == 0))

        stats = context_hints.get_tool_stats("git")

        assert stats["count"] == 10
        assert stats["success_rate"] == 0.5

    def test_record_tool_usage_with_failures(self, context_hints):
        """Test recording tool usage with failures."""
        context_hints.record_tool_usage("compiler", success=True)
        context_hints.record_tool_usage("compiler", success=False)
        context_hints.record_tool_usage("compiler", success=True)

        stats = context_hints.get_tool_stats("compiler")

        assert stats["count"] == 3
        assert stats["success_count"] == 2
        assert abs(stats["success_rate"] - 0.6667) < 0.01

    def test_get_nonexistent_tool_stats(self, context_hints):
        """Test getting stats for non-existent tool."""
        stats = context_hints.get_tool_stats("nonexistent")

        assert stats is None

    def test_record_empty_tool_name_raises_error(self, context_hints):
        """Test that empty tool name raises ValueError."""
        with pytest.raises(ValueError, match="Tool name cannot be empty"):
            context_hints.record_tool_usage("", success=True)

    def test_get_most_used_tools(self, context_hints):
        """Test getting most used tools."""
        context_hints.record_tool_usage("pytest", success=True)
        context_hints.record_tool_usage("pytest", success=True)
        context_hints.record_tool_usage("pytest", success=True)

        context_hints.record_tool_usage("git", success=True)
        context_hints.record_tool_usage("git", success=True)

        context_hints.record_tool_usage("docker", success=True)

        most_used = context_hints.get_most_used_tools(limit=2)

        assert len(most_used) == 2
        assert most_used[0]["tool_name"] == "pytest"
        assert most_used[0]["count"] == 3
        assert most_used[1]["tool_name"] == "git"
        assert most_used[1]["count"] == 2

    def test_get_most_used_tools_with_limit(self, context_hints):
        """Test getting most used tools with limit."""
        for i in range(10):
            tool_name = f"tool_{i}"
            for _ in range(i):
                context_hints.record_tool_usage(tool_name, success=True)

        most_used = context_hints.get_most_used_tools(limit=3)

        assert len(most_used) == 3
        assert most_used[0]["tool_name"] == "tool_9"


class TestPersistenceAndCrossSessions:
    """Test suite for persistence verification."""

    def test_preferences_persist(self, memory_db):
        """Test that preferences persist in database."""
        hints = ContextHints(memory_db, session_id="sess1")
        hints.set_preference("lang", "python")

        # Create new instance with same session
        hints2 = ContextHints(memory_db, session_id="sess1")

        assert hints2.get_preference("lang") == "python"

    def test_patterns_persist(self, memory_db):
        """Test that patterns persist in database."""
        hints = ContextHints(memory_db, session_id="sess1")
        hints.record_task_pattern("task", {}, "success")

        hints2 = ContextHints(memory_db, session_id="sess1")
        patterns = hints2.get_task_patterns()

        assert len(patterns) == 1

    def test_expertise_persists(self, memory_db):
        """Test that expertise levels persist."""
        hints = ContextHints(memory_db, session_id="sess1")
        hints.set_expertise_level("python", 5)

        hints2 = ContextHints(memory_db, session_id="sess1")

        assert hints2.get_expertise_level("python") == 5

    def test_tool_usage_persists(self, memory_db):
        """Test that tool usage persists."""
        hints = ContextHints(memory_db, session_id="sess1")
        hints.record_tool_usage("git", success=True)

        hints2 = ContextHints(memory_db, session_id="sess1")
        stats = hints2.get_tool_stats("git")

        assert stats["count"] == 1


class TestEdgeCases:
    """Test suite for edge cases."""

    def test_unicode_in_preferences(self, context_hints):
        """Test unicode support in preferences."""
        context_hints.set_preference("greeting", "안녕하세요 🚀")

        assert context_hints.get_preference("greeting") == "안녕하세요 🚀"

    def test_large_context_in_pattern(self, context_hints):
        """Test recording pattern with large context."""
        large_context = {"data": "x" * 10000}

        context_hints.record_task_pattern("task", large_context, "success")
        patterns = context_hints.get_task_patterns()

        assert patterns[0]["context"]["data"] == "x" * 10000

    def test_special_characters_in_keys(self, context_hints):
        """Test special characters in preference keys."""
        context_hints.set_preference("key:with:colons", "value")

        assert context_hints.get_preference("key:with:colons") == "value"

    def test_none_values_in_preferences(self, context_hints):
        """Test None values in preferences."""
        context_hints.set_preference("nullable", None)

        assert context_hints.get_preference("nullable") is None
