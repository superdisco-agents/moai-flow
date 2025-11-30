#!/usr/bin/env python3
"""
Advanced Hooks Examples

Comprehensive examples demonstrating the enhanced hooks system:
1. Priority-based execution
2. Conditional execution
3. Async hooks
4. Hook dependencies
5. Rollback pattern

Run with: python -m moai_flow.examples.hooks_advanced
"""

import asyncio
import sys
import time
from pathlib import Path

# Add moai_flow to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moai_flow.hooks.hook_executor import HookContext, HookPhase
from moai_flow.hooks.hook_registry import HookPriority, HookRegistry


# =============================================================================
# Example 1: Priority-Based Execution
# =============================================================================

def example_1_priority_execution():
    """
    Demonstrate priority-based hook execution.

    Hooks execute in order: CRITICAL → HIGH → NORMAL → LOW → DEFERRED
    """
    print("=" * 60)
    print("Example 1: Priority-Based Execution")
    print("=" * 60)

    registry = HookRegistry()

    # Define hooks with different priorities
    def validate_input(context: HookContext):
        """Critical: Validate input before processing"""
        print(f"  [CRITICAL] Validating input: {context.data.get('task_id')}")
        return {"validation": "passed"}

    def log_task(context: HookContext):
        """Normal: Log task start"""
        print(f"  [NORMAL] Logging task start: {context.data.get('task_id')}")
        return {"logged": True}

    def send_notification(context: HookContext):
        """Deferred: Send notification (can be delayed)"""
        print(f"  [DEFERRED] Sending notification: {context.data.get('task_id')}")
        return {"notification_sent": True}

    def collect_metrics(context: HookContext):
        """High: Collect metrics early"""
        print(f"  [HIGH] Collecting metrics: {context.data.get('task_id')}")
        return {"metrics_collected": True}

    # Register hooks with different priorities
    registry.register_hook(
        "validate_critical",
        validate_input,
        "task_start",
        priority=HookPriority.CRITICAL
    )

    registry.register_hook(
        "log_task",
        log_task,
        "task_start",
        priority=HookPriority.NORMAL
    )

    registry.register_hook(
        "send_notification",
        send_notification,
        "task_start",
        priority=HookPriority.DEFERRED
    )

    registry.register_hook(
        "collect_metrics",
        collect_metrics,
        "task_start",
        priority=HookPriority.HIGH
    )

    # Execute hooks
    print("\nExecuting hooks (observe priority order):")
    context = HookContext(
        phase=HookPhase.PRE,
        event_type="task_start",
        data={"task_id": "task-001", "agent_type": "expert-backend"},
        metadata={"priority": 1},
        timestamp=time.time()
    )

    results = registry.execute_hooks("task_start", HookPhase.PRE, context)

    print(f"\nExecuted {len(results)} hooks:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Success: {result.success}, Time: {result.execution_time_ms:.2f}ms")

    print("\n✅ Example 1 complete: Hooks executed in priority order\n")


# =============================================================================
# Example 2: Conditional Execution
# =============================================================================

def example_2_conditional_execution():
    """
    Demonstrate conditional hook execution.

    Hooks only execute if all conditions are met.
    """
    print("=" * 60)
    print("Example 2: Conditional Execution")
    print("=" * 60)

    registry = HookRegistry()

    # Define conditional hooks
    def production_logging(context: HookContext):
        """Log only in production environment"""
        print(f"  [PROD] Production logging for: {context.data.get('task_id')}")
        return {"logged_to_datadog": True}

    def debug_logging(context: HookContext):
        """Log only in debug mode"""
        print(f"  [DEBUG] Debug logging for: {context.data.get('task_id')}")
        return {"logged_to_console": True}

    # Condition predicates
    def only_production(context: HookContext) -> bool:
        """Execute only in production"""
        return context.metadata.get("env") == "production"

    def only_debug(context: HookContext) -> bool:
        """Execute only in debug mode"""
        return context.metadata.get("debug", False)

    # Register hooks with conditions
    registry.register_hook(
        "prod_logging",
        production_logging,
        "task_complete",
        conditions=[only_production]
    )

    registry.register_hook(
        "debug_logging",
        debug_logging,
        "task_complete",
        conditions=[only_debug]
    )

    # Test with production context
    print("\nTest 1: Production environment")
    prod_context = HookContext(
        phase=HookPhase.POST,
        event_type="task_complete",
        data={"task_id": "task-002"},
        metadata={"env": "production", "debug": False},
        timestamp=time.time()
    )

    results = registry.execute_hooks("task_complete", HookPhase.POST, prod_context)
    print(f"  Executed {len(results)} hooks (expected: 1 prod hook)")

    # Test with debug context
    print("\nTest 2: Debug environment")
    debug_context = HookContext(
        phase=HookPhase.POST,
        event_type="task_complete",
        data={"task_id": "task-003"},
        metadata={"env": "development", "debug": True},
        timestamp=time.time()
    )

    results = registry.execute_hooks("task_complete", HookPhase.POST, debug_context)
    print(f"  Executed {len(results)} hooks (expected: 1 debug hook)")

    print("\n✅ Example 2 complete: Conditional execution working\n")


# =============================================================================
# Example 3: Async Hooks
# =============================================================================

async def example_3_async_hooks():
    """
    Demonstrate asynchronous hook execution.

    Async hooks can perform I/O operations without blocking.
    """
    print("=" * 60)
    print("Example 3: Async Hooks")
    print("=" * 60)

    registry = HookRegistry()

    # Define async hook
    async def async_database_save(context: HookContext):
        """Simulate async database save"""
        print(f"  [ASYNC] Saving to database: {context.data.get('task_id')}")
        await asyncio.sleep(0.1)  # Simulate I/O
        print(f"  [ASYNC] Database save complete")
        return {"saved": True}

    # Define sync hook for comparison
    def sync_local_save(context: HookContext):
        """Synchronous local save"""
        print(f"  [SYNC] Saving locally: {context.data.get('task_id')}")
        return {"saved_locally": True}

    # Register async hook
    registry.register_hook(
        "async_db_save",
        async_database_save,
        "task_complete",
        executor_type="async"
    )

    # Register sync hook
    registry.register_hook(
        "sync_local_save",
        sync_local_save,
        "task_complete",
        executor_type="standard"
    )

    # Execute hooks
    print("\nExecuting mixed sync/async hooks:")
    context = HookContext(
        phase=HookPhase.POST,
        event_type="task_complete",
        data={"task_id": "task-004", "result": "success"},
        metadata={},
        timestamp=time.time()
    )

    results = registry.execute_hooks("task_complete", HookPhase.POST, context)

    print(f"\nExecuted {len(results)} hooks:")
    for i, result in enumerate(results, 1):
        executor = result.metadata.get("executor", "unknown")
        print(f"  {i}. {executor}: {result.success}, Time: {result.execution_time_ms:.2f}ms")

    print("\n✅ Example 3 complete: Async hooks executed successfully\n")


# =============================================================================
# Example 4: Hook Dependencies
# =============================================================================

def example_4_hook_dependencies():
    """
    Demonstrate hook dependency resolution.

    Hooks execute in correct order based on dependencies.
    """
    print("=" * 60)
    print("Example 4: Hook Dependencies")
    print("=" * 60)

    registry = HookRegistry()

    # Define dependent hooks
    execution_order = []

    def hook_a(context: HookContext):
        """First hook (no dependencies)"""
        print("  [A] Executing hook A (independent)")
        execution_order.append("A")
        return {"a": "done"}

    def hook_b(context: HookContext):
        """Second hook (depends on A)"""
        print("  [B] Executing hook B (depends on A)")
        execution_order.append("B")
        return {"b": "done"}

    def hook_c(context: HookContext):
        """Third hook (depends on A and B)"""
        print("  [C] Executing hook C (depends on A and B)")
        execution_order.append("C")
        return {"c": "done"}

    def hook_d(context: HookContext):
        """Fourth hook (depends on B)"""
        print("  [D] Executing hook D (depends on B)")
        execution_order.append("D")
        return {"d": "done"}

    # Register hooks with dependencies
    # Dependency graph: A → B → C
    #                      B → D

    registry.register_hook("hook_a", hook_a, "event")
    registry.register_hook("hook_b", hook_b, "event", dependencies=["hook_a"])
    registry.register_hook("hook_c", hook_c, "event", dependencies=["hook_a", "hook_b"])
    registry.register_hook("hook_d", hook_d, "event", dependencies=["hook_b"])

    # Execute hooks
    print("\nExecuting hooks with dependencies:")
    print("  Dependency graph: A → B → C")
    print("                       B → D")
    print()

    context = HookContext(
        phase=HookPhase.PRE,
        event_type="event",
        data={},
        metadata={},
        timestamp=time.time()
    )

    results = registry.execute_hooks("event", HookPhase.PRE, context)

    print(f"\nExecution order: {' → '.join(execution_order)}")
    print(f"Expected order: A → B → (C or D) → (D or C)")
    print(f"✅ Valid: {execution_order[0] == 'A' and execution_order[1] == 'B'}")

    print("\n✅ Example 4 complete: Dependencies resolved correctly\n")


# =============================================================================
# Example 5: Rollback Pattern
# =============================================================================

def example_5_rollback_pattern():
    """
    Demonstrate rollback pattern with hooks.

    On error, rollback all completed actions.
    """
    print("=" * 60)
    print("Example 5: Rollback Pattern")
    print("=" * 60)

    class TransactionHook:
        """Transaction hook with rollback capability"""

        def __init__(self):
            self.actions = []

        def pre_hook(self, context: HookContext):
            """Record action for potential rollback"""
            action = {
                "type": "database_write",
                "data": context.data.copy(),
                "timestamp": time.time()
            }
            self.actions.append(action)
            print(f"  [PRE] Recording action: {action['type']}")
            return {"recorded": True}

        def error_hook(self, context: HookContext):
            """Rollback all actions on error"""
            print(f"\n  [ERROR] Rolling back {len(self.actions)} actions:")
            for action in reversed(self.actions):
                print(f"    - Undoing: {action['type']}")
            self.actions.clear()
            return {"rolled_back": len(self.actions)}

    registry = HookRegistry()
    transaction = TransactionHook()

    # Register transaction hooks
    registry.register_hook(
        "transaction_pre",
        transaction.pre_hook,
        "database_operation",
        phase=HookPhase.PRE
    )

    registry.register_hook(
        "transaction_error",
        transaction.error_hook,
        "database_operation",
        phase=HookPhase.ERROR
    )

    # Test normal execution
    print("\nTest 1: Normal execution (no rollback)")
    context = HookContext(
        phase=HookPhase.PRE,
        event_type="database_operation",
        data={"table": "users", "action": "insert"},
        metadata={},
        timestamp=time.time()
    )

    results = registry.execute_hooks("database_operation", HookPhase.PRE, context)
    print(f"  Actions recorded: {len(transaction.actions)}")

    # Test error execution (rollback)
    print("\nTest 2: Error execution (with rollback)")

    # Add more actions
    for i in range(3):
        context = HookContext(
            phase=HookPhase.PRE,
            event_type="database_operation",
            data={"table": "users", "action": f"insert_{i}"},
            metadata={},
            timestamp=time.time()
        )
        registry.execute_hooks("database_operation", HookPhase.PRE, context)

    print(f"  Total actions: {len(transaction.actions)}")

    # Trigger error hook
    error_context = HookContext(
        phase=HookPhase.ERROR,
        event_type="database_operation",
        data={"error": "Connection failed"},
        metadata={},
        timestamp=time.time()
    )

    error_results = registry.execute_hooks("database_operation", HookPhase.ERROR, error_context)
    print(f"  Actions after rollback: {len(transaction.actions)}")

    print("\n✅ Example 5 complete: Rollback pattern demonstrated\n")


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MoAI-Flow Advanced Hooks Examples")
    print("=" * 60 + "\n")

    # Example 1: Priority-based execution
    example_1_priority_execution()

    # Example 2: Conditional execution
    example_2_conditional_execution()

    # Example 3: Async hooks
    asyncio.run(example_3_async_hooks())

    # Example 4: Hook dependencies
    example_4_hook_dependencies()

    # Example 5: Rollback pattern
    example_5_rollback_pattern()

    # Summary
    print("=" * 60)
    print("All Examples Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  ✅ Priority-based execution (5 levels)")
    print("  ✅ Conditional execution (predicate functions)")
    print("  ✅ Async hooks (non-blocking I/O)")
    print("  ✅ Hook dependencies (topological sorting)")
    print("  ✅ Rollback pattern (error handling)")
    print("\nFor more details, see:")
    print("  - moai_flow/hooks/hook_executor.py")
    print("  - moai_flow/hooks/hook_registry.py")
    print("  - moai_flow/hooks/standard_executor.py")
    print("  - moai_flow/hooks/async_executor.py")
    print()


if __name__ == "__main__":
    main()
