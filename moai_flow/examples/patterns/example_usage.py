"""
Pattern Storage & Schema Usage Examples
========================================

Comprehensive examples demonstrating pattern storage and schema validation.
"""

from datetime import datetime
import uuid

from moai_flow.patterns import (
    # Schema types
    Pattern,
    PatternType,
    TaskCompletionData,
    ErrorOccurrenceData,
    AgentUsageData,
    UserCorrectionData,
    PatternContext,
    PatternSchema,
    # Storage
    PatternStorage,
    StorageConfig
)


def example_task_completion():
    """Example: Task completion pattern."""

    # Create task completion data
    task_data: TaskCompletionData = {
        "task_type": "code_generation",
        "agent": "expert-backend",
        "duration_ms": 2500,
        "success": True,
        "files_created": 2,
        "files_modified": 1,
        "tests_passed": 15,
        "tests_failed": 0,
        "lines_of_code": 127,
        "coverage_percent": 92.5,
        "retry_count": 0
    }

    # Create context
    context: PatternContext = {
        "project_name": "moai-adk",
        "session_id": "session-123",
        "environment": "development",
        "git_branch": "feature/pattern-storage",
        "timestamp": datetime.now().isoformat(),
        "tags": ["backend", "fastapi", "authentication"]
    }

    # Create complete pattern
    pattern: Pattern = {
        "pattern_id": str(uuid.uuid4()),
        "pattern_type": PatternType.TASK_COMPLETION,
        "timestamp": datetime.now().isoformat(),
        "data": task_data,
        "context": context,
        "version": "1.0"
    }

    # Validate pattern
    is_valid = PatternSchema.validate_pattern(pattern)
    print(f"Pattern valid: {is_valid}")

    # Save to filesystem storage
    storage = PatternStorage(backend="filesystem", base_path=".moai/patterns")
    storage.save(pattern)
    print(f"Pattern saved: {pattern['pattern_id']}")

    # Query patterns
    patterns = storage.query(
        pattern_type=PatternType.TASK_COMPLETION,
        limit=10
    )
    print(f"Found {len(patterns)} task completion patterns")

    return pattern


def example_error_occurrence():
    """Example: Error occurrence pattern."""

    error_data: ErrorOccurrenceData = {
        "error_type": "TypeError",
        "error_message": "unsupported operand type(s) for +: 'int' and 'str'",
        "stack_trace": """Traceback (most recent call last):
  File "app.py", line 42, in process_data
    result = count + value
TypeError: unsupported operand type(s) for +: 'int' and 'str'""",
        "file_path": "app.py",
        "line_number": 42,
        "function_name": "process_data",
        "resolution": "Convert value to int before addition",
        "resolution_time_ms": 3200,
        "similar_errors_count": 2,
        "auto_resolved": False,
        "user_intervention": True
    }

    context: PatternContext = {
        "project_name": "moai-adk",
        "session_id": "session-123",
        "environment": "development",
        "timestamp": datetime.now().isoformat(),
        "tags": ["error", "type-error", "data-processing"]
    }

    pattern: Pattern = {
        "pattern_id": str(uuid.uuid4()),
        "pattern_type": PatternType.ERROR_OCCURRENCE,
        "timestamp": datetime.now().isoformat(),
        "data": error_data,
        "context": context,
        "version": "1.0"
    }

    # Validate and save
    assert PatternSchema.validate_pattern(pattern), "Invalid error pattern"

    storage = PatternStorage(backend="filesystem")
    storage.save(pattern)
    print(f"Error pattern saved: {pattern['pattern_id']}")

    return pattern


def example_agent_usage():
    """Example: Agent usage pattern."""

    usage_data: AgentUsageData = {
        "agent_type": "expert-backend",
        "task_type": "api_implementation",
        "success": True,
        "duration_ms": 5400,
        "retry_count": 1,
        "tools_used": ["Read", "Write", "Edit", "Bash"],
        "files_accessed": 8,
        "api_calls": 3,
        "tokens_used": 4200,
        "memory_mb": 125.5,
        "cpu_percent": 45.2,
        "parallel_tasks": 2
    }

    context: PatternContext = {
        "project_name": "moai-adk",
        "session_id": "session-123",
        "environment": "development",
        "timestamp": datetime.now().isoformat(),
        "tags": ["backend", "agent-usage", "performance"]
    }

    pattern: Pattern = {
        "pattern_id": str(uuid.uuid4()),
        "pattern_type": PatternType.AGENT_USAGE,
        "timestamp": datetime.now().isoformat(),
        "data": usage_data,
        "context": context,
        "version": "1.0"
    }

    # Validate and save
    assert PatternSchema.validate_pattern(pattern), "Invalid agent usage pattern"

    storage = PatternStorage(backend="filesystem")
    storage.save(pattern)
    print(f"Agent usage pattern saved: {pattern['pattern_id']}")

    return pattern


def example_user_correction():
    """Example: User correction pattern."""

    correction_data: UserCorrectionData = {
        "original_output": "def process_data(data):\n    return data + 1",
        "corrected_output": "def process_data(data: List[int]) -> List[int]:\n    \"\"\"Process data list.\"\"\"\n    return [x + 1 for x in data]",
        "correction_type": "type_safety",
        "agent": "expert-backend",
        "task_type": "code_generation",
        "correction_category": "code_quality",
        "user_feedback": "Add type hints and handle list input properly",
        "severity": "moderate",
        "pattern_matched": None
    }

    context: PatternContext = {
        "project_name": "moai-adk",
        "session_id": "session-123",
        "environment": "development",
        "timestamp": datetime.now().isoformat(),
        "tags": ["correction", "type-safety", "code-quality"]
    }

    pattern: Pattern = {
        "pattern_id": str(uuid.uuid4()),
        "pattern_type": PatternType.USER_CORRECTION,
        "timestamp": datetime.now().isoformat(),
        "data": correction_data,
        "context": context,
        "version": "1.0"
    }

    # Validate and save
    assert PatternSchema.validate_pattern(pattern), "Invalid user correction pattern"

    storage = PatternStorage(backend="filesystem")
    storage.save(pattern)
    print(f"User correction pattern saved: {pattern['pattern_id']}")

    return pattern


def example_sqlite_storage():
    """Example: Using SQLite storage backend."""

    # Create SQLite storage
    storage = PatternStorage(
        backend="sqlite",
        base_path=".moai/patterns/patterns",
        retention_days=90
    )

    # Create and save multiple patterns
    patterns = []
    for i in range(5):
        task_data: TaskCompletionData = {
            "task_type": f"task_{i}",
            "agent": "expert-backend",
            "duration_ms": 1000 + i * 100,
            "success": True,
            "files_created": i,
            "files_modified": i + 1,
            "tests_passed": 10 + i,
            "tests_failed": 0,
            "lines_of_code": 50 + i * 10,
            "retry_count": 0
        }

        pattern: Pattern = {
            "pattern_id": str(uuid.uuid4()),
            "pattern_type": PatternType.TASK_COMPLETION,
            "timestamp": datetime.now().isoformat(),
            "data": task_data,
            "context": {"project_name": "moai-adk", "timestamp": datetime.now().isoformat()},
            "version": "1.0"
        }

        storage.save(pattern)
        patterns.append(pattern)

    print(f"Saved {len(patterns)} patterns to SQLite")

    # Query patterns
    results = storage.query(pattern_type=PatternType.TASK_COMPLETION, limit=10)
    print(f"Query returned {len(results)} patterns")

    # Load specific pattern
    loaded = storage.load(patterns[0]["pattern_id"])
    if loaded:
        print(f"Loaded pattern: {loaded['pattern_id']}")

    storage.close()
    return patterns


def example_querying():
    """Example: Advanced pattern querying."""

    storage = PatternStorage(backend="filesystem")

    # Query by date range
    from datetime import timedelta

    patterns = storage.query(
        pattern_type=PatternType.TASK_COMPLETION,
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        limit=50
    )
    print(f"Patterns in last 7 days: {len(patterns)}")

    # Query by tags
    patterns_with_tags = storage.query(
        tags=["backend", "authentication"],
        limit=20
    )
    print(f"Patterns with tags: {len(patterns_with_tags)}")

    return patterns


def example_cleanup():
    """Example: Pattern cleanup and compression."""

    storage = PatternStorage(
        backend="filesystem",
        compression_threshold_days=30,
        retention_days=90
    )

    # Compress old files (>30 days)
    compressed = storage.compress_old_files()
    print(f"Compressed {compressed} old files")

    # Delete old patterns (>90 days)
    deleted = storage.delete_old_patterns(retention_days=90)
    print(f"Deleted {deleted} old patterns")

    return compressed, deleted


def main():
    """Run all examples."""
    print("=== Pattern Storage & Schema Examples ===\n")

    print("1. Task Completion Pattern:")
    example_task_completion()
    print()

    print("2. Error Occurrence Pattern:")
    example_error_occurrence()
    print()

    print("3. Agent Usage Pattern:")
    example_agent_usage()
    print()

    print("4. User Correction Pattern:")
    example_user_correction()
    print()

    print("5. SQLite Storage:")
    example_sqlite_storage()
    print()

    print("6. Advanced Querying:")
    example_querying()
    print()

    print("7. Cleanup & Compression:")
    example_cleanup()
    print()

    print("=== All examples completed successfully ===")


if __name__ == "__main__":
    main()
