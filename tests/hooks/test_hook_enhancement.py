#!/usr/bin/env python3
"""
Comprehensive Tests for Enhanced Hooks System

Tests cover:
- All 3 executors (IHookExecutor, StandardHookExecutor, AsyncHookExecutor)
- Priority ordering
- Conditional execution
- Dependencies resolution
- Timeout handling
- Graceful degradation
- Rollback patterns
- Concurrent execution (async)
- Error handling

Target: 90%+ test coverage
"""

import asyncio
import pytest
import time
from typing import Any

from moai_flow.hooks.hook_executor import (
    HookContext,
    HookPhase,
    HookResult,
    IHookExecutor,
)
from moai_flow.hooks.standard_executor import StandardHookExecutor, TimeoutException
from moai_flow.hooks.async_executor import AsyncHookExecutor
from moai_flow.hooks.hook_registry import (
    HookRegistry,
    HookPriority,
    HookRegistration,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def simple_hook():
    """Simple hook that returns success"""
    def hook(context: HookContext):
        return {"status": "success"}
    return hook


@pytest.fixture
def slow_hook():
    """Hook that takes 500ms"""
    def hook(context: HookContext):
        time.sleep(0.5)
        return {"status": "slow_success"}
    return hook


@pytest.fixture
def failing_hook():
    """Hook that raises exception"""
    def hook(context: HookContext):
        raise ValueError("Hook failed intentionally")
    return hook


@pytest.fixture
async def async_simple_hook():
    """Simple async hook"""
    async def hook(context: HookContext):
        await asyncio.sleep(0.1)
        return {"status": "async_success"}
    return hook


@pytest.fixture
def sample_context():
    """Sample HookContext for testing"""
    return HookContext(
        phase=HookPhase.PRE,
        event_type="test_event",
        data={"test_id": "test-001"},
        metadata={"priority": 1},
        timestamp=time.time()
    )


# =============================================================================
# Test HookContext and HookResult
# =============================================================================

class TestHookContext:
    """Test HookContext data class"""

    def test_context_creation(self):
        """Test creating HookContext"""
        context = HookContext(
            phase=HookPhase.PRE,
            event_type="task_start",
            data={"task_id": "task-001"},
            metadata={"priority": 1},
            timestamp=time.time()
        )

        assert context.phase == HookPhase.PRE
        assert context.event_type == "task_start"
        assert context.data["task_id"] == "task-001"
        assert context.metadata["priority"] == 1
        assert context.timestamp > 0

    def test_context_phase_conversion(self):
        """Test phase string to enum conversion"""
        context = HookContext(
            phase="pre",  # String
            event_type="test",
            data={},
            metadata={}
        )

        assert context.phase == HookPhase.PRE
        assert isinstance(context.phase, HookPhase)

    def test_context_defaults(self):
        """Test default values"""
        context = HookContext(
            phase=HookPhase.POST,
            event_type="test",
            data={}
        )

        assert context.metadata == {}
        assert context.timestamp > 0


class TestHookResult:
    """Test HookResult data class"""

    def test_result_success(self):
        """Test successful result"""
        result = HookResult(
            success=True,
            data={"result": "success"},
            error=None,
            execution_time_ms=100.5
        )

        assert result.success is True
        assert result.data["result"] == "success"
        assert result.error is None
        assert result.execution_time_ms == 100.5

    def test_result_failure(self):
        """Test failure result"""
        error = ValueError("Test error")
        result = HookResult(
            success=False,
            data=None,
            error=error,
            execution_time_ms=50.0
        )

        assert result.success is False
        assert result.data is None
        assert result.error == error
        assert result.execution_time_ms == 50.0

    def test_result_to_dict(self):
        """Test converting result to dict"""
        error = ValueError("Test error")
        result = HookResult(
            success=False,
            data=None,
            error=error,
            execution_time_ms=50.0,
            metadata={"retries": 2}
        )

        result_dict = result.to_dict()

        assert result_dict["success"] is False
        assert result_dict["data"] is None
        assert "Test error" in result_dict["error"]
        assert result_dict["error_type"] == "ValueError"
        assert result_dict["execution_time_ms"] == 50.0
        assert result_dict["metadata"]["retries"] == 2


# =============================================================================
# Test StandardHookExecutor
# =============================================================================

class TestStandardHookExecutor:
    """Test StandardHookExecutor"""

    def test_executor_initialization(self):
        """Test executor initialization"""
        executor = StandardHookExecutor(
            timeout_ms=3000,
            graceful_degradation=True,
            max_retries=2
        )

        assert executor.timeout_ms == 3000
        assert executor.graceful_degradation is True
        assert executor.max_retries == 2

    def test_executor_invalid_params(self):
        """Test invalid initialization parameters"""
        with pytest.raises(ValueError):
            StandardHookExecutor(timeout_ms=-100)

        with pytest.raises(ValueError):
            StandardHookExecutor(max_retries=5)  # Max is 3

    def test_execute_simple_hook(self, simple_hook, sample_context):
        """Test executing simple hook"""
        executor = StandardHookExecutor()
        result = executor.execute(simple_hook, sample_context)

        assert result.success is True
        assert result.data["status"] == "success"
        assert result.error is None
        assert result.execution_time_ms > 0

    def test_execute_failing_hook_graceful(self, failing_hook, sample_context):
        """Test failing hook with graceful degradation"""
        executor = StandardHookExecutor(graceful_degradation=True)
        result = executor.execute(failing_hook, sample_context)

        assert result.success is False
        assert result.data is None
        assert isinstance(result.error, ValueError)
        assert "Hook failed intentionally" in str(result.error)

    def test_execute_failing_hook_no_graceful(self, failing_hook, sample_context):
        """Test failing hook without graceful degradation"""
        executor = StandardHookExecutor(graceful_degradation=False)

        with pytest.raises(ValueError) as exc_info:
            executor.execute(failing_hook, sample_context)

        assert "Hook failed intentionally" in str(exc_info.value)

    def test_timeout_handling_graceful(self, slow_hook, sample_context):
        """Test timeout handling with graceful degradation"""
        executor = StandardHookExecutor(timeout_ms=100, graceful_degradation=True)
        result = executor.execute(slow_hook, sample_context)

        assert result.success is False
        assert isinstance(result.error, TimeoutException)

    def test_timeout_handling_no_graceful(self, slow_hook, sample_context):
        """Test timeout handling without graceful degradation"""
        executor = StandardHookExecutor(timeout_ms=100, graceful_degradation=False)

        with pytest.raises(TimeoutException):
            executor.execute(slow_hook, sample_context)

    def test_retry_logic(self, sample_context):
        """Test retry logic"""
        attempt_count = [0]

        def failing_then_success(context: HookContext):
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError(f"Attempt {attempt_count[0]} failed")
            return {"success": True, "attempts": attempt_count[0]}

        executor = StandardHookExecutor(max_retries=2)
        result = executor.execute(failing_then_success, sample_context)

        assert result.success is True
        assert result.data["attempts"] == 2

    def test_supports_async(self):
        """Test supports_async method"""
        executor = StandardHookExecutor()
        assert executor.supports_async() is False

    def test_get_timeout_ms(self):
        """Test get_timeout_ms method"""
        executor = StandardHookExecutor(timeout_ms=5000)
        assert executor.get_timeout_ms() == 5000

    def test_get_stats(self, simple_hook, failing_hook, sample_context):
        """Test execution statistics"""
        executor = StandardHookExecutor(graceful_degradation=True)

        # Execute some hooks
        executor.execute(simple_hook, sample_context)
        executor.execute(simple_hook, sample_context)
        executor.execute(failing_hook, sample_context)

        stats = executor.get_stats()

        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 2
        assert stats["failed_executions"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, rel=0.01)


# =============================================================================
# Test AsyncHookExecutor
# =============================================================================

class TestAsyncHookExecutor:
    """Test AsyncHookExecutor"""

    def test_executor_initialization(self):
        """Test async executor initialization"""
        executor = AsyncHookExecutor(
            timeout_ms=10000,
            concurrent_limit=20
        )

        assert executor.timeout_ms == 10000
        assert executor.concurrent_limit == 20

    def test_executor_invalid_params(self):
        """Test invalid initialization parameters"""
        with pytest.raises(ValueError):
            AsyncHookExecutor(timeout_ms=-100)

        with pytest.raises(ValueError):
            AsyncHookExecutor(concurrent_limit=0)

    @pytest.mark.asyncio
    async def test_execute_async_hook(self, sample_context):
        """Test executing async hook"""
        async def async_hook(context: HookContext):
            await asyncio.sleep(0.1)
            return {"status": "async_success"}

        executor = AsyncHookExecutor()
        result = await executor.execute_async(async_hook, sample_context)

        assert result.success is True
        assert result.data["status"] == "async_success"
        assert result.error is None
        assert result.execution_time_ms > 100

    @pytest.mark.asyncio
    async def test_execute_sync_hook_in_async(self, simple_hook, sample_context):
        """Test executing sync hook in async executor"""
        executor = AsyncHookExecutor()
        result = await executor.execute_async(simple_hook, sample_context)

        assert result.success is True
        assert result.data["status"] == "success"

    @pytest.mark.asyncio
    async def test_async_timeout(self, sample_context):
        """Test async timeout handling"""
        async def slow_async_hook(context: HookContext):
            await asyncio.sleep(1.0)
            return {"status": "never_reached"}

        executor = AsyncHookExecutor(timeout_ms=100)
        result = await executor.execute_async(slow_async_hook, sample_context)

        assert result.success is False
        assert isinstance(result.error, asyncio.TimeoutError)

    @pytest.mark.asyncio
    async def test_async_error_handling(self, sample_context):
        """Test async error handling"""
        async def failing_async_hook(context: HookContext):
            raise RuntimeError("Async hook failed")

        executor = AsyncHookExecutor()
        result = await executor.execute_async(failing_async_hook, sample_context)

        assert result.success is False
        assert isinstance(result.error, RuntimeError)
        assert "Async hook failed" in str(result.error)

    @pytest.mark.asyncio
    async def test_execute_batch(self, sample_context):
        """Test batch execution"""
        async def async_hook_1(context: HookContext):
            await asyncio.sleep(0.05)
            return {"hook": 1}

        async def async_hook_2(context: HookContext):
            await asyncio.sleep(0.05)
            return {"hook": 2}

        async def async_hook_3(context: HookContext):
            await asyncio.sleep(0.05)
            return {"hook": 3}

        hooks = [async_hook_1, async_hook_2, async_hook_3]

        executor = AsyncHookExecutor()
        results = await executor.execute_batch(hooks, sample_context)

        assert len(results) == 3
        assert all(r.success for r in results)
        assert results[0].data["hook"] == 1
        assert results[1].data["hook"] == 2
        assert results[2].data["hook"] == 3

    @pytest.mark.asyncio
    async def test_concurrent_limit(self, sample_context):
        """Test concurrent execution limit"""
        concurrent_count = [0]
        max_concurrent = [0]

        async def concurrent_hook(context: HookContext):
            nonlocal concurrent_count, max_concurrent
            concurrent_count[0] += 1
            if concurrent_count[0] > max_concurrent[0]:
                max_concurrent[0] = concurrent_count[0]

            await asyncio.sleep(0.1)

            concurrent_count[0] -= 1
            return {"concurrent": max_concurrent[0]}

        hooks = [concurrent_hook for _ in range(20)]

        executor = AsyncHookExecutor(concurrent_limit=5)
        results = await executor.execute_batch(hooks, sample_context)

        assert len(results) == 20
        assert max_concurrent[0] <= 5

    def test_supports_async(self):
        """Test supports_async method"""
        executor = AsyncHookExecutor()
        assert executor.supports_async() is True

    def test_get_timeout_ms(self):
        """Test get_timeout_ms method"""
        executor = AsyncHookExecutor(timeout_ms=10000)
        assert executor.get_timeout_ms() == 10000

    @pytest.mark.asyncio
    async def test_get_stats(self, simple_hook, failing_hook, sample_context):
        """Test async executor statistics"""
        executor = AsyncHookExecutor()

        # Execute some hooks
        await executor.execute_async(simple_hook, sample_context)
        await executor.execute_async(simple_hook, sample_context)
        await executor.execute_async(failing_hook, sample_context)

        stats = executor.get_stats()

        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 2
        assert stats["failed_executions"] == 1


# =============================================================================
# Test HookRegistry
# =============================================================================

class TestHookRegistry:
    """Test HookRegistry"""

    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = HookRegistry()

        # Should have default executors
        assert "standard" in registry._executors
        assert "async" in registry._executors

    def test_register_custom_executor(self):
        """Test registering custom executor"""
        registry = HookRegistry()

        class CustomExecutor(IHookExecutor):
            def execute(self, hook, context):
                return HookResult(success=True, data=None, execution_time_ms=0.0)

            def supports_async(self):
                return False

            def get_timeout_ms(self):
                return 1000

        custom_executor = CustomExecutor()
        registry.register_executor("custom", custom_executor)

        assert "custom" in registry._executors

    def test_register_executor_invalid_type(self):
        """Test registering invalid executor"""
        registry = HookRegistry()

        with pytest.raises(TypeError):
            registry.register_executor("invalid", "not_an_executor")

    def test_register_executor_duplicate(self):
        """Test registering duplicate executor"""
        registry = HookRegistry()

        class CustomExecutor(IHookExecutor):
            def execute(self, hook, context):
                return HookResult(success=True, data=None, execution_time_ms=0.0)

            def supports_async(self):
                return False

            def get_timeout_ms(self):
                return 1000

        executor = CustomExecutor()
        registry.register_executor("custom", executor)

        with pytest.raises(ValueError):
            registry.register_executor("custom", executor)

    def test_register_hook(self, simple_hook):
        """Test registering hook"""
        registry = HookRegistry()

        registry.register_hook(
            name="test_hook",
            hook=simple_hook,
            event_type="test_event",
            phase=HookPhase.PRE,
            priority=HookPriority.NORMAL
        )

        hooks = registry.get_registered_hooks("test_event", HookPhase.PRE)
        assert len(hooks) == 1
        assert hooks[0].name == "test_hook"

    def test_register_hook_duplicate(self, simple_hook):
        """Test registering duplicate hook"""
        registry = HookRegistry()

        registry.register_hook("test_hook", simple_hook, "test_event")

        with pytest.raises(ValueError):
            registry.register_hook("test_hook", simple_hook, "test_event")

    def test_register_hook_invalid_executor(self, simple_hook):
        """Test registering hook with invalid executor"""
        registry = HookRegistry()

        with pytest.raises(ValueError):
            registry.register_hook(
                "test_hook",
                simple_hook,
                "test_event",
                executor_type="nonexistent"
            )

    def test_unregister_hook(self, simple_hook):
        """Test unregistering hook"""
        registry = HookRegistry()

        registry.register_hook("test_hook", simple_hook, "test_event")
        assert registry.unregister_hook("test_hook", "test_event", HookPhase.PRE) is True
        assert registry.unregister_hook("test_hook", "test_event", HookPhase.PRE) is False

    def test_priority_ordering(self, sample_context):
        """Test hooks execute in priority order"""
        registry = HookRegistry()
        execution_order = []

        def make_hook(name):
            def hook(context: HookContext):
                execution_order.append(name)
                return {"name": name}
            return hook

        # Register hooks in reverse priority order
        registry.register_hook("low", make_hook("low"), "test", priority=HookPriority.LOW)
        registry.register_hook("critical", make_hook("critical"), "test", priority=HookPriority.CRITICAL)
        registry.register_hook("normal", make_hook("normal"), "test", priority=HookPriority.NORMAL)
        registry.register_hook("high", make_hook("high"), "test", priority=HookPriority.HIGH)

        registry.execute_hooks("test", HookPhase.PRE, sample_context)

        # Should execute: CRITICAL, HIGH, NORMAL, LOW
        assert execution_order == ["critical", "high", "normal", "low"]

    def test_conditional_execution(self, sample_context):
        """Test conditional hook execution"""
        registry = HookRegistry()
        execution_count = [0]

        def conditional_hook(context: HookContext):
            execution_count[0] += 1
            return {"executed": True}

        def condition_true(context: HookContext):
            return True

        def condition_false(context: HookContext):
            return False

        # Hook with passing condition
        registry.register_hook(
            "hook_true",
            conditional_hook,
            "test",
            conditions=[condition_true]
        )

        # Hook with failing condition
        registry.register_hook(
            "hook_false",
            conditional_hook,
            "test",
            conditions=[condition_false]
        )

        registry.execute_hooks("test", HookPhase.PRE, sample_context)

        # Only hook_true should execute
        assert execution_count[0] == 1

    def test_dependency_resolution(self, sample_context):
        """Test dependency resolution"""
        registry = HookRegistry()
        execution_order = []

        def make_hook(name):
            def hook(context: HookContext):
                execution_order.append(name)
                return {"name": name}
            return hook

        # Register hooks with dependencies
        # Dependency graph: A → B → C
        registry.register_hook("hook_a", make_hook("A"), "test")
        registry.register_hook("hook_b", make_hook("B"), "test", dependencies=["hook_a"])
        registry.register_hook("hook_c", make_hook("C"), "test", dependencies=["hook_b"])

        registry.execute_hooks("test", HookPhase.PRE, sample_context)

        # Should execute: A, B, C
        assert execution_order == ["A", "B", "C"]

    def test_circular_dependency_detection(self, simple_hook, sample_context):
        """Test circular dependency detection"""
        registry = HookRegistry()

        registry.register_hook("hook_a", simple_hook, "test")
        registry.register_hook("hook_b", simple_hook, "test", dependencies=["hook_c"])
        registry.register_hook("hook_c", simple_hook, "test", dependencies=["hook_b"])

        with pytest.raises(ValueError, match="Circular dependency"):
            registry.execute_hooks("test", HookPhase.PRE, sample_context)

    def test_enable_disable_hook(self, simple_hook, sample_context):
        """Test enabling/disabling hooks"""
        registry = HookRegistry()
        execution_count = [0]

        def counting_hook(context: HookContext):
            execution_count[0] += 1
            return {"count": execution_count[0]}

        registry.register_hook("test_hook", counting_hook, "test")

        # Execute (enabled by default)
        registry.execute_hooks("test", HookPhase.PRE, sample_context)
        assert execution_count[0] == 1

        # Disable and execute
        registry.disable_hook("test_hook")
        registry.execute_hooks("test", HookPhase.PRE, sample_context)
        assert execution_count[0] == 1  # Should not increment

        # Re-enable and execute
        registry.enable_hook("test_hook")
        registry.execute_hooks("test", HookPhase.PRE, sample_context)
        assert execution_count[0] == 2  # Should increment

    def test_get_hook_stats(self, simple_hook, failing_hook, sample_context):
        """Test hook statistics"""
        registry = HookRegistry()

        registry.register_hook("success_hook", simple_hook, "test")
        registry.register_hook("fail_hook", failing_hook, "test")

        # Execute hooks multiple times
        for _ in range(5):
            registry.execute_hooks("test", HookPhase.PRE, sample_context)

        # Get overall stats
        stats = registry.get_hook_stats()
        assert stats["total_hooks"] == 2
        assert stats["total_executions"] == 10  # 2 hooks × 5 executions

        # Get specific hook stats
        success_stats = registry.get_hook_stats("success_hook")
        assert success_stats["total_executions"] == 5
        assert success_stats["successful_executions"] == 5

    def test_get_registered_hooks(self, simple_hook):
        """Test getting registered hooks"""
        registry = HookRegistry()

        registry.register_hook("hook1", simple_hook, "event1", phase=HookPhase.PRE)
        registry.register_hook("hook2", simple_hook, "event1", phase=HookPhase.POST)
        registry.register_hook("hook3", simple_hook, "event2", phase=HookPhase.PRE)

        # Get all hooks for event1
        event1_hooks = registry.get_registered_hooks("event1")
        assert len(event1_hooks) == 2

        # Get hooks for event1/PRE
        event1_pre_hooks = registry.get_registered_hooks("event1", HookPhase.PRE)
        assert len(event1_pre_hooks) == 1
        assert event1_pre_hooks[0].name == "hook1"

        # Get all hooks
        all_hooks = registry.get_registered_hooks()
        assert len(all_hooks) == 3


# =============================================================================
# Integration Tests
# =============================================================================

class TestHooksIntegration:
    """Integration tests for complete hooks system"""

    def test_end_to_end_workflow(self):
        """Test complete workflow with multiple hooks"""
        registry = HookRegistry()
        workflow_state = {
            "validation": None,
            "processing": None,
            "cleanup": None
        }

        def validate_hook(context: HookContext):
            workflow_state["validation"] = "passed"
            return {"validated": True}

        def process_hook(context: HookContext):
            workflow_state["processing"] = "completed"
            return {"processed": True}

        def cleanup_hook(context: HookContext):
            workflow_state["cleanup"] = "done"
            return {"cleanup": True}

        # Register hooks
        registry.register_hook(
            "validate",
            validate_hook,
            "workflow",
            priority=HookPriority.CRITICAL
        )

        registry.register_hook(
            "process",
            process_hook,
            "workflow",
            priority=HookPriority.NORMAL,
            dependencies=["validate"]
        )

        registry.register_hook(
            "cleanup",
            cleanup_hook,
            "workflow",
            priority=HookPriority.LOW,
            dependencies=["process"]
        )

        # Execute workflow
        context = HookContext(
            phase=HookPhase.PRE,
            event_type="workflow",
            data={},
            metadata={},
            timestamp=time.time()
        )

        results = registry.execute_hooks("workflow", HookPhase.PRE, context)

        # Verify execution
        assert len(results) == 3
        assert all(r.success for r in results)

        # Verify state
        assert workflow_state["validation"] == "passed"
        assert workflow_state["processing"] == "completed"
        assert workflow_state["cleanup"] == "done"

    @pytest.mark.asyncio
    async def test_mixed_sync_async_execution(self):
        """Test mixing sync and async hooks"""
        registry = HookRegistry()
        execution_order = []

        def sync_hook(context: HookContext):
            execution_order.append("sync")
            return {"type": "sync"}

        async def async_hook(context: HookContext):
            await asyncio.sleep(0.05)
            execution_order.append("async")
            return {"type": "async"}

        registry.register_hook("sync", sync_hook, "mixed", executor_type="standard")
        registry.register_hook("async", async_hook, "mixed", executor_type="async")

        context = HookContext(
            phase=HookPhase.POST,
            event_type="mixed",
            data={},
            metadata={},
            timestamp=time.time()
        )

        results = registry.execute_hooks("mixed", HookPhase.POST, context)

        assert len(results) == 2
        assert all(r.success for r in results)
        assert "sync" in execution_order
        assert "async" in execution_order


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=moai_flow.hooks", "--cov-report=term-missing"])
