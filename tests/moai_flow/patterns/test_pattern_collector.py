"""
Tests for PatternCollector - PRD-05 Phase 1

Comprehensive test suite for pattern collection system.
Tests all pattern types, storage, querying, and maintenance operations.
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from moai_flow.patterns.pattern_collector import (
    PatternCollector,
    Pattern,
    PatternType
)


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def collector(temp_storage):
    """Create PatternCollector instance for testing."""
    return PatternCollector(storage_path=str(temp_storage))


@pytest.fixture
def config_file(temp_storage):
    """Create temporary config file."""
    config_path = temp_storage / "config.json"
    config = {
        "patterns": {
            "enabled": True,
            "storage": str(temp_storage),
            "collect": {
                "task_completion": True,
                "error_occurrence": True,
                "agent_usage": True,
                "user_correction": False
            },
            "retention_days": 30
        }
    }
    with open(config_path, 'w') as f:
        json.dump(config, f)
    return config_path


class TestPatternCollector:
    """Test PatternCollector initialization and basic operations."""

    def test_init_creates_storage_directory(self, temp_storage):
        """Test that initialization creates storage directory."""
        collector = PatternCollector(storage_path=str(temp_storage))
        assert temp_storage.exists()
        assert temp_storage.is_dir()

    def test_init_loads_config(self, temp_storage, config_file):
        """Test that configuration is loaded from config file."""
        collector = PatternCollector(
            storage_path=str(temp_storage),
            config_path=str(config_file)
        )
        assert collector.config["enabled"] is True
        assert collector.config["retention_days"] == 30

    def test_init_creates_date_hierarchy(self, temp_storage):
        """Test that initialization creates year/month/day directories."""
        collector = PatternCollector(storage_path=str(temp_storage))
        now = datetime.now()
        year_path = temp_storage / str(now.year)
        month_path = year_path / f"{now.month:02d}"
        day_path = month_path / f"{now.day:02d}"

        assert year_path.exists()
        assert month_path.exists()
        assert day_path.exists()


class TestTaskCompletionPatterns:
    """Test task completion pattern collection."""

    def test_collect_task_completion_basic(self, collector):
        """Test basic task completion pattern collection."""
        pattern_id = collector.collect_task_completion(
            task_type="api_implementation",
            agent="expert-backend",
            duration_ms=45000,
            success=True
        )

        assert pattern_id.startswith("pat-")
        assert collector.get_pattern_count(PatternType.TASK_COMPLETION) == 1

    def test_collect_task_completion_with_context(self, collector):
        """Test task completion with full context."""
        pattern_id = collector.collect_task_completion(
            task_type="api_implementation",
            agent="expert-backend",
            duration_ms=45000,
            success=True,
            files_created=3,
            tests_passed=12,
            context={
                "framework": "fastapi",
                "language": "python",
                "spec_id": "SPEC-001"
            }
        )

        patterns = collector.get_patterns(PatternType.TASK_COMPLETION)
        assert len(patterns) == 1
        assert patterns[0].data["files_created"] == 3
        assert patterns[0].data["tests_passed"] == 12
        assert patterns[0].context["framework"] == "fastapi"

    def test_collect_task_completion_failure(self, collector):
        """Test task completion pattern for failed tasks."""
        pattern_id = collector.collect_task_completion(
            task_type="database_migration",
            agent="expert-database",
            duration_ms=10000,
            success=False,
            files_created=0,
            tests_passed=0
        )

        patterns = collector.get_patterns(PatternType.TASK_COMPLETION)
        assert len(patterns) == 1
        assert patterns[0].data["success"] is False


class TestErrorOccurrencePatterns:
    """Test error occurrence pattern collection."""

    def test_collect_error_occurrence_basic(self, collector):
        """Test basic error pattern collection."""
        pattern_id = collector.collect_error_occurrence(
            error_type="ValidationError",
            error_message="Invalid API key format",
            context={"file": "api/auth.py", "line": 42}
        )

        assert pattern_id.startswith("pat-")
        assert collector.get_pattern_count(PatternType.ERROR_OCCURRENCE) == 1

    def test_collect_error_occurrence_with_resolution(self, collector):
        """Test error pattern with resolution."""
        pattern_id = collector.collect_error_occurrence(
            error_type="ImportError",
            error_message="Module 'fastapi' not found",
            context={"file": "main.py", "function": "init_app"},
            resolution="Added fastapi to requirements.txt"
        )

        patterns = collector.get_patterns(PatternType.ERROR_OCCURRENCE)
        assert len(patterns) == 1
        assert patterns[0].data["resolution"] == "Added fastapi to requirements.txt"

    def test_collect_multiple_errors(self, collector):
        """Test collecting multiple error patterns."""
        for i in range(5):
            collector.collect_error_occurrence(
                error_type=f"Error{i}",
                error_message=f"Error message {i}",
                context={"iteration": i}
            )

        assert collector.get_pattern_count(PatternType.ERROR_OCCURRENCE) == 5


class TestAgentUsagePatterns:
    """Test agent usage pattern collection."""

    def test_collect_agent_usage_basic(self, collector):
        """Test basic agent usage pattern."""
        pattern_id = collector.collect_agent_usage(
            agent_type="expert-backend",
            task_type="api_implementation",
            success=True,
            duration_ms=45000
        )

        assert pattern_id.startswith("pat-")
        assert collector.get_pattern_count(PatternType.AGENT_USAGE) == 1

    def test_collect_agent_usage_multiple_agents(self, collector):
        """Test collecting usage from multiple agents."""
        agents = ["expert-backend", "expert-frontend", "manager-tdd"]

        for agent in agents:
            collector.collect_agent_usage(
                agent_type=agent,
                task_type="implementation",
                success=True,
                duration_ms=30000
            )

        assert collector.get_pattern_count(PatternType.AGENT_USAGE) == 3


class TestUserCorrectionPatterns:
    """Test user correction pattern collection."""

    def test_collect_user_correction_basic(self, temp_storage):
        """Test basic user correction pattern."""
        # Create collector with user_correction enabled
        config_path = temp_storage / "config.json"
        config = {
            "patterns": {
                "enabled": True,
                "storage": str(temp_storage),
                "collect": {
                    "task_completion": True,
                    "error_occurrence": True,
                    "agent_usage": True,
                    "user_correction": True  # Enabled
                },
                "retention_days": 90
            }
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        collector = PatternCollector(
            storage_path=str(temp_storage),
            config_path=str(config_path)
        )

        pattern_id = collector.collect_user_correction(
            original_output="def add(a, b): return a + b",
            corrected_output="def add(a: int, b: int) -> int: return a + b",
            correction_type="type_hints_missing"
        )

        assert pattern_id.startswith("pat-")
        assert collector.get_pattern_count(PatternType.USER_CORRECTION) == 1

    def test_collect_user_correction_with_context(self, temp_storage):
        """Test user correction with context."""
        # Create collector with user_correction enabled
        config_path = temp_storage / "config.json"
        config = {
            "patterns": {
                "enabled": True,
                "storage": str(temp_storage),
                "collect": {
                    "task_completion": True,
                    "error_occurrence": True,
                    "agent_usage": True,
                    "user_correction": True  # Enabled
                },
                "retention_days": 90
            }
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        collector = PatternCollector(
            storage_path=str(temp_storage),
            config_path=str(config_path)
        )

        pattern_id = collector.collect_user_correction(
            original_output="print('hello')",
            corrected_output="logger.info('hello')",
            correction_type="logging_improvement",
            context={"file": "utils.py", "agent": "expert-backend"}
        )

        patterns = collector.get_patterns(PatternType.USER_CORRECTION)
        assert len(patterns) == 1
        assert patterns[0].context["agent"] == "expert-backend"


class TestPatternQuerying:
    """Test pattern querying and filtering."""

    def test_get_patterns_by_type(self, collector):
        """Test filtering patterns by type."""
        # Create different pattern types
        collector.collect_task_completion("task1", "agent1", 1000, True)
        collector.collect_error_occurrence("Error1", "msg1", {})
        collector.collect_agent_usage("agent1", "task1", True, 1000)

        task_patterns = collector.get_patterns(PatternType.TASK_COMPLETION)
        error_patterns = collector.get_patterns(PatternType.ERROR_OCCURRENCE)
        agent_patterns = collector.get_patterns(PatternType.AGENT_USAGE)

        assert len(task_patterns) == 1
        assert len(error_patterns) == 1
        assert len(agent_patterns) == 1

    def test_get_patterns_with_limit(self, collector):
        """Test pattern query with limit."""
        # Create 10 patterns
        for i in range(10):
            collector.collect_task_completion(
                f"task{i}", "agent", 1000, True
            )

        patterns = collector.get_patterns(limit=5)
        assert len(patterns) == 5

    def test_get_patterns_date_range(self, collector):
        """Test pattern query with date range."""
        # This test creates patterns and queries them
        # In real scenario, patterns would be from different dates
        collector.collect_task_completion("task1", "agent", 1000, True)

        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)

        patterns = collector.get_patterns(
            start_date=start_date,
            end_date=end_date
        )
        assert len(patterns) >= 1


class TestPatternCount:
    """Test pattern counting operations."""

    def test_get_pattern_count_total(self, collector):
        """Test getting total pattern count."""
        collector.collect_task_completion("task1", "agent", 1000, True)
        collector.collect_error_occurrence("Error1", "msg", {})

        total = collector.get_pattern_count()
        assert total == 2

    def test_get_pattern_count_by_type(self, collector):
        """Test getting pattern count by type."""
        # Create multiple patterns of same type
        for i in range(3):
            collector.collect_task_completion(f"task{i}", "agent", 1000, True)

        task_count = collector.get_pattern_count(PatternType.TASK_COMPLETION)
        assert task_count == 3

    def test_get_pattern_count_empty(self, collector):
        """Test pattern count when no patterns exist."""
        count = collector.get_pattern_count()
        assert count == 0


class TestPatternStorage:
    """Test pattern storage operations."""

    def test_pattern_file_structure(self, collector, temp_storage):
        """Test that patterns are stored in correct directory structure."""
        collector.collect_task_completion("task1", "agent", 1000, True)

        now = datetime.now()
        expected_path = (
            temp_storage /
            str(now.year) /
            f"{now.month:02d}" /
            f"{now.day:02d}"
        )

        assert expected_path.exists()
        pattern_files = list(expected_path.glob("*.json"))
        assert len(pattern_files) == 1

    def test_pattern_file_content(self, collector, temp_storage):
        """Test pattern file contains correct JSON structure."""
        pattern_id = collector.collect_task_completion(
            task_type="test_task",
            agent="test_agent",
            duration_ms=5000,
            success=True,
            files_created=2,
            tests_passed=10,
            context={"test": "context"}
        )

        # Find and read the pattern file
        now = datetime.now()
        pattern_dir = (
            temp_storage /
            str(now.year) /
            f"{now.month:02d}" /
            f"{now.day:02d}"
        )
        pattern_files = list(pattern_dir.glob("*.json"))
        assert len(pattern_files) == 1

        with open(pattern_files[0]) as f:
            pattern_data = json.load(f)

        assert pattern_data["pattern_id"] == pattern_id
        assert pattern_data["type"] == "task_completion"
        assert pattern_data["data"]["task_type"] == "test_task"
        assert pattern_data["data"]["files_created"] == 2
        assert pattern_data["context"]["test"] == "context"


class TestPatternCleanup:
    """Test pattern cleanup operations."""

    def test_cleanup_old_patterns(self, collector, temp_storage):
        """Test cleanup of patterns older than retention period."""
        # Create pattern in old directory
        old_date = datetime.now() - timedelta(days=100)
        old_dir = (
            temp_storage /
            str(old_date.year) /
            f"{old_date.month:02d}" /
            f"{old_date.day:02d}"
        )
        old_dir.mkdir(parents=True, exist_ok=True)

        # Create a pattern file
        pattern_file = old_dir / "task_completion_old.json"
        pattern_file.write_text(json.dumps({"test": "data"}))

        # Run cleanup
        deleted = collector.cleanup_old_patterns()
        assert deleted >= 1
        assert not pattern_file.exists()


class TestPatternCompression:
    """Test pattern compression operations."""

    def test_compress_old_patterns(self, collector, temp_storage):
        """Test compression of old patterns."""
        # Create pattern in old directory
        old_date = datetime.now() - timedelta(days=40)
        old_dir = (
            temp_storage /
            str(old_date.year) /
            f"{old_date.month:02d}" /
            f"{old_date.day:02d}"
        )
        old_dir.mkdir(parents=True, exist_ok=True)

        # Create a pattern file
        pattern_file = old_dir / "task_completion_20251101_100000.json"
        pattern_file.write_text(json.dumps({"test": "data"}))

        # Run compression
        compressed = collector.compress_old_patterns(days_old=30)
        assert compressed >= 1
        assert not pattern_file.exists()
        assert (old_dir / "task_completion_20251101_100000.json.gz").exists()


class TestPatternStatistics:
    """Test pattern statistics operations."""

    def test_get_statistics_empty(self, collector):
        """Test statistics when no patterns exist."""
        stats = collector.get_statistics()

        assert stats["total_patterns"] == 0
        assert stats["collection_enabled"] is True
        assert "by_type" in stats

    def test_get_statistics_with_patterns(self, collector):
        """Test statistics with various patterns."""
        # Create different pattern types
        collector.collect_task_completion("task1", "agent", 1000, True)
        collector.collect_task_completion("task2", "agent", 2000, True)
        collector.collect_error_occurrence("Error1", "msg", {})

        stats = collector.get_statistics()

        assert stats["total_patterns"] == 3
        assert stats["by_type"]["task_completion"] == 2
        assert stats["by_type"]["error_occurrence"] == 1
        assert stats["by_type"]["agent_usage"] == 0


class TestConfigIntegration:
    """Test configuration integration."""

    def test_config_disabled_collection(self, temp_storage):
        """Test that patterns are not collected when disabled."""
        config_path = temp_storage / "config.json"
        config = {
            "patterns": {
                "enabled": False,
                "storage": str(temp_storage),
                "collect": {
                    "task_completion": True,
                    "error_occurrence": True,
                    "agent_usage": True,
                    "user_correction": False
                },
                "retention_days": 90
            }
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        collector = PatternCollector(
            storage_path=str(temp_storage),
            config_path=str(config_path)
        )

        collector.collect_task_completion("task1", "agent", 1000, True)
        assert collector.get_pattern_count() == 0

    def test_config_selective_collection(self, temp_storage):
        """Test selective pattern collection based on config."""
        config_path = temp_storage / "config.json"
        config = {
            "patterns": {
                "enabled": True,
                "storage": str(temp_storage),
                "collect": {
                    "task_completion": True,
                    "error_occurrence": False,  # Disabled
                    "agent_usage": True,
                    "user_correction": False
                },
                "retention_days": 90
            }
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        collector = PatternCollector(
            storage_path=str(temp_storage),
            config_path=str(config_path)
        )

        collector.collect_task_completion("task1", "agent", 1000, True)
        collector.collect_error_occurrence("Error1", "msg", {})

        # Only task completion should be collected
        assert collector.get_pattern_count(PatternType.TASK_COMPLETION) == 1
        assert collector.get_pattern_count(PatternType.ERROR_OCCURRENCE) == 0


class TestThreadSafety:
    """Test thread safety of pattern collection."""

    def test_concurrent_pattern_collection(self, collector):
        """Test that concurrent pattern collection works correctly."""
        import threading

        def collect_patterns():
            for i in range(10):
                collector.collect_task_completion(
                    f"task{i}",
                    "agent",
                    1000,
                    True
                )

        threads = [threading.Thread(target=collect_patterns) for _ in range(3)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have 30 patterns (3 threads × 10 patterns)
        assert collector.get_pattern_count() == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
