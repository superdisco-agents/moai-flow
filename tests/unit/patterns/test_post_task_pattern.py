#!/usr/bin/env python3
"""
Tests for PostTask Pattern Hook Integration

Tests the integration of pattern collection with Phase 7 hooks system.
"""

import time
import pytest
from pathlib import Path
from moai_flow.hooks import HookRegistry, HookContext, HookPhase
from moai_flow.hooks.post_task_pattern import (
    PostTaskPatternHook,
    ErrorPatternHook,
    register_pattern_hooks
)
from moai_flow.patterns import PatternCollector


@pytest.fixture
def temp_storage(tmp_path):
    """Temporary storage path for patterns"""
    return tmp_path / "patterns"


@pytest.fixture
def collector(temp_storage):
    """Pattern collector with temporary storage"""
    return PatternCollector(storage_path=str(temp_storage))


@pytest.fixture
def registry():
    """Hook registry"""
    return HookRegistry()


class TestPostTaskPatternHook:
    """Tests for PostTaskPatternHook"""

    def test_hook_initialization(self, collector):
        """Test hook initialization"""
        hook = PostTaskPatternHook(collector, enabled=True)

        assert hook.collector == collector
        assert hook.enabled is True

    def test_hook_execution_success(self, collector):
        """Test successful hook execution"""
        hook = PostTaskPatternHook(collector, enabled=True)

        context = HookContext(
            phase=HookPhase.POST,
            event_type="task_complete",
            data={
                "task_type": "api_implementation",
                "agent_id": "expert-backend",
                "duration_ms": 45000,
                "success": True,
                "files_created": 3,
                "tests_passed": 12
            },
            metadata={"framework": "fastapi"},
            timestamp=time.time()
        )

        result = hook(context)

        assert result.success is True
        assert "pattern_id" in result.metadata
        assert result.metadata["pattern_id"].startswith("pat-")

    def test_hook_execution_disabled(self):
        """Test hook execution when disabled"""
        hook = PostTaskPatternHook(enabled=False)

        context = HookContext(
            phase=HookPhase.POST,
            event_type="task_complete",
            data={"task_type": "test"},
            metadata={},
            timestamp=time.time()
        )

        result = hook(context)

        assert result.success is True
        assert result.metadata.get("skipped") is True

    def test_hook_graceful_degradation(self, tmp_path):
        """Test graceful degradation on error"""
        # Create collector and then disable it by setting config enabled=False
        import json
        config_dir = tmp_path / ".moai" / "config"
        config_dir.mkdir(parents=True)

        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "patterns": {
                "enabled": False  # Disable collection
            }
        }))

        collector = PatternCollector(
            storage_path=str(tmp_path / "patterns"),
            config_path=str(config_file)
        )

        hook = PostTaskPatternHook(collector, enabled=True)

        context = HookContext(
            phase=HookPhase.POST,
            event_type="task_complete",
            data={"task_type": "test"},
            metadata={},
            timestamp=time.time()
        )

        result = hook(context)

        # Should succeed but pattern_id will be empty string (collection disabled)
        assert result.success is True


class TestErrorPatternHook:
    """Tests for ErrorPatternHook"""

    def test_hook_initialization(self, collector):
        """Test error hook initialization"""
        hook = ErrorPatternHook(collector, enabled=True)

        assert hook.collector == collector
        assert hook.enabled is True

    def test_hook_execution_success(self, collector):
        """Test successful error hook execution"""
        hook = ErrorPatternHook(collector, enabled=True)

        context = HookContext(
            phase=HookPhase.ERROR,
            event_type="task_failed",
            data={
                "error_type": "ValidationError",
                "error_message": "Invalid API key",
                "resolution": "Added validation"
            },
            metadata={"endpoint": "/api/v1/users"},
            timestamp=time.time()
        )

        result = hook(context)

        assert result.success is True
        assert "pattern_id" in result.metadata
        assert result.metadata["pattern_id"].startswith("pat-")

    def test_hook_execution_disabled(self):
        """Test error hook when disabled"""
        hook = ErrorPatternHook(enabled=False)

        context = HookContext(
            phase=HookPhase.ERROR,
            event_type="task_failed",
            data={"error_type": "TestError"},
            metadata={},
            timestamp=time.time()
        )

        result = hook(context)

        assert result.success is True
        assert result.metadata.get("skipped") is True


class TestHookRegistration:
    """Tests for hook registration"""

    def test_register_pattern_hooks(self, registry, temp_storage):
        """Test pattern hooks registration"""
        collector = PatternCollector(storage_path=temp_storage)

        register_pattern_hooks(registry, collector, enabled=True)

        # Verify PostTask hook registered
        post_hooks = registry.get_registered_hooks("task_complete", HookPhase.POST)
        assert len(post_hooks) > 0
        assert any(h.name == "post_task_pattern_collection" for h in post_hooks)

        # Verify error hook registered
        error_hooks = registry.get_registered_hooks("task_failed", HookPhase.ERROR)
        assert len(error_hooks) > 0
        assert any(h.name == "error_pattern_collection" for h in error_hooks)

    def test_register_hooks_disabled(self, registry):
        """Test hook registration when disabled"""
        register_pattern_hooks(registry, enabled=False)

        # No hooks should be registered
        post_hooks = registry.get_registered_hooks("task_complete", HookPhase.POST)
        error_hooks = registry.get_registered_hooks("task_failed", HookPhase.ERROR)

        # Should be empty or not contain pattern hooks
        post_pattern_hooks = [h for h in post_hooks if "pattern" in h.name]
        error_pattern_hooks = [h for h in error_hooks if "pattern" in h.name]

        assert len(post_pattern_hooks) == 0
        assert len(error_pattern_hooks) == 0


class TestIntegration:
    """Integration tests for pattern collection via hooks"""

    def test_full_integration_task_complete(self, registry, temp_storage):
        """Test full integration: task completion"""
        # Create config to enable pattern collection
        import json
        config_dir = temp_storage / ".moai" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "patterns": {
                "enabled": True,
                "collect": {
                    "task_completion": True
                }
            }
        }))

        collector = PatternCollector(
            storage_path=str(temp_storage / "patterns"),
            config_path=str(config_file)
        )
        register_pattern_hooks(registry, collector, enabled=True)

        # Execute task completion event
        context = HookContext(
            phase=HookPhase.POST,
            event_type="task_complete",
            data={
                "task_type": "database_migration",
                "agent_id": "expert-database",
                "duration_ms": 30000,
                "success": True,
                "files_created": 2,
                "tests_passed": 8
            },
            metadata={"database": "postgresql"},
            timestamp=time.time()
        )

        results = registry.execute_hooks("task_complete", HookPhase.POST, context)

        # Verify pattern was collected
        assert len(results) > 0

        # The hook executor wraps our HookResult as `data`, so we need to extract it
        pattern_result = None
        for r in results:
            if r.data and hasattr(r.data, 'metadata') and "pattern_id" in r.data.metadata:
                pattern_result = r.data
                break

        assert pattern_result is not None
        assert pattern_result.success is True

        # Verify pattern stored
        stats = collector.get_statistics()
        assert stats["total_patterns"] > 0

    def test_full_integration_error(self, registry, temp_storage):
        """Test full integration: error occurrence"""
        # Create config to enable pattern collection
        import json
        config_dir = temp_storage / ".moai" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "patterns": {
                "enabled": True,
                "collect": {
                    "error_occurrence": True
                }
            }
        }))

        collector = PatternCollector(
            storage_path=str(temp_storage / "patterns"),
            config_path=str(config_file)
        )
        register_pattern_hooks(registry, collector, enabled=True)

        # Execute error event
        context = HookContext(
            phase=HookPhase.ERROR,
            event_type="task_failed",
            data={
                "error_type": "ConnectionError",
                "error_message": "Database connection failed",
                "resolution": "Retry with backoff"
            },
            metadata={"database": "postgresql"},
            timestamp=time.time()
        )

        results = registry.execute_hooks("task_failed", HookPhase.ERROR, context)

        # Verify error pattern was collected
        assert len(results) > 0

        # The hook executor wraps our HookResult as `data`, so we need to extract it
        error_result = None
        for r in results:
            if r.data and hasattr(r.data, 'metadata') and "pattern_id" in r.data.metadata:
                error_result = r.data
                break

        assert error_result is not None
        assert error_result.success is True

    def test_hook_statistics(self, registry, temp_storage):
        """Test hook execution statistics"""
        collector = PatternCollector(storage_path=temp_storage)
        register_pattern_hooks(registry, collector, enabled=True)

        # Execute multiple events
        for i in range(5):
            context = HookContext(
                phase=HookPhase.POST,
                event_type="task_complete",
                data={
                    "task_type": f"task_{i}",
                    "agent_id": "expert-backend",
                    "duration_ms": 20000,
                    "success": True
                },
                metadata={},
                timestamp=time.time()
            )

            registry.execute_hooks("task_complete", HookPhase.POST, context)

        # Get statistics
        stats = registry.get_hook_stats("post_task_pattern_collection")

        assert stats["total_executions"] == 5
        assert stats["successful_executions"] == 5
        assert stats["success_rate"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
