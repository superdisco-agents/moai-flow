#!/usr/bin/env python3
"""
Pattern Collection Integration Example

Demonstrates how to integrate pattern collection with hook system.
"""

import time
from moai_flow.hooks import HookRegistry, HookContext, HookPhase
from moai_flow.hooks.post_task_pattern import register_pattern_hooks
from moai_flow.patterns import PatternCollector


def example_basic_pattern_collection():
    """Example: Basic pattern collection without hooks"""
    print("\n=== Example 1: Basic Pattern Collection ===\n")

    # Initialize collector
    collector = PatternCollector()

    # Collect task completion pattern
    pattern_id = collector.collect_task_completion(
        task_type="api_implementation",
        agent="expert-backend",
        duration_ms=45000,
        success=True,
        files_created=3,
        tests_passed=12,
        context={"framework": "fastapi", "language": "python"}
    )

    print(f"Collected task pattern: {pattern_id}")

    # Collect error pattern
    error_pattern_id = collector.collect_error_occurrence(
        error_type="ValidationError",
        error_message="Invalid API key format",
        context={"endpoint": "/api/v1/users"},
        resolution="Added API key validation middleware"
    )

    print(f"Collected error pattern: {error_pattern_id}")

    # Get statistics
    stats = collector.get_pattern_stats()
    print(f"\nPattern Statistics:")
    print(f"  Total patterns: {stats['total_patterns']}")
    print(f"  By type: {stats['by_type']}")


def example_hook_integration():
    """Example: Pattern collection via hook integration"""
    print("\n=== Example 2: Hook Integration ===\n")

    # Initialize hook registry
    registry = HookRegistry()

    # Register pattern hooks
    register_pattern_hooks(registry)

    # Simulate task completion event
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
        metadata={
            "database": "postgresql",
            "migration_type": "schema_update"
        },
        timestamp=time.time()
    )

    # Execute hooks (pattern collection happens automatically)
    results = registry.execute_hooks("task_complete", HookPhase.POST, context)

    for result in results:
        if result.success:
            pattern_id = result.metadata.get("pattern_id", "N/A")
            print(f"Pattern collected via hook: {pattern_id}")
        else:
            print(f"Hook failed: {result.error}")


def example_error_hook():
    """Example: Error pattern collection via hook"""
    print("\n=== Example 3: Error Hook ===\n")

    # Initialize hook registry
    registry = HookRegistry()

    # Register pattern hooks
    register_pattern_hooks(registry)

    # Simulate error event
    error_context = HookContext(
        phase=HookPhase.ERROR,
        event_type="task_failed",
        data={
            "error_type": "DatabaseConnectionError",
            "error_message": "Connection timeout after 30s",
            "resolution": "Increased connection timeout to 60s"
        },
        metadata={
            "database": "postgresql",
            "host": "db.example.com"
        },
        timestamp=time.time()
    )

    # Execute error hooks
    results = registry.execute_hooks("task_failed", HookPhase.ERROR, error_context)

    for result in results:
        if result.success:
            pattern_id = result.metadata.get("pattern_id", "N/A")
            print(f"Error pattern collected: {pattern_id}")


def example_custom_collector():
    """Example: Custom collector with specific storage path"""
    print("\n=== Example 4: Custom Collector ===\n")

    from pathlib import Path

    # Custom storage path
    custom_path = Path("/tmp/moai_patterns")

    # Initialize collector with custom path
    collector = PatternCollector(storage_path=custom_path, enabled=True)

    # Collect pattern
    pattern_id = collector.collect_agent_usage(
        agent="manager-tdd",
        task_type="test_generation",
        duration_ms=25000,
        success=True
    )

    print(f"Collected agent usage pattern: {pattern_id}")
    print(f"Storage path: {custom_path}")


def example_hook_stats():
    """Example: Get hook execution statistics"""
    print("\n=== Example 5: Hook Statistics ===\n")

    # Initialize and register hooks
    registry = HookRegistry()
    register_pattern_hooks(registry)

    # Simulate multiple task completions
    for i in range(5):
        context = HookContext(
            phase=HookPhase.POST,
            event_type="task_complete",
            data={
                "task_type": f"task_{i}",
                "agent_id": "expert-backend",
                "duration_ms": 20000 + (i * 5000),
                "success": i % 2 == 0  # Alternate success/failure
            },
            metadata={},
            timestamp=time.time()
        )

        registry.execute_hooks("task_complete", HookPhase.POST, context)

    # Get hook statistics
    hook_stats = registry.get_hook_stats("post_task_pattern_collection")

    print("Hook Execution Statistics:")
    print(f"  Hook name: {hook_stats['hook_name']}")
    print(f"  Total executions: {hook_stats['total_executions']}")
    print(f"  Successful: {hook_stats['successful_executions']}")
    print(f"  Failed: {hook_stats['failed_executions']}")
    print(f"  Success rate: {hook_stats['success_rate']}%")


def example_graceful_degradation():
    """Example: Graceful degradation on pattern collection errors"""
    print("\n=== Example 6: Graceful Degradation ===\n")

    from pathlib import Path

    # Create collector with invalid path (to simulate error)
    invalid_path = Path("/root/forbidden_path")  # Typically no write access

    collector = PatternCollector(storage_path=invalid_path, enabled=True)

    # Try to collect pattern (should fail gracefully)
    pattern_id = collector.collect_task_completion(
        task_type="test_task",
        agent="test-agent",
        duration_ms=1000,
        success=True
    )

    if pattern_id:
        print(f"Pattern collected: {pattern_id}")
    else:
        print("Pattern collection failed, but execution continued gracefully")


if __name__ == "__main__":
    # Run all examples
    example_basic_pattern_collection()
    example_hook_integration()
    example_error_hook()
    example_custom_collector()
    example_hook_stats()
    example_graceful_degradation()

    print("\n=== All Examples Complete ===\n")
