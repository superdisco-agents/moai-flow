# Pattern Storage & Schema - Quick Start Guide

## 30-Second Overview

Pattern Storage & Schema provides type-safe pattern collection and storage for MoAI-Flow with dual backends (filesystem and SQLite).

## Install & Import

```python
from moai_flow.patterns import (
    Pattern, PatternType, PatternStorage, PatternSchema,
    TaskCompletionData, ErrorOccurrenceData,
    AgentUsageData, UserCorrectionData
)
from datetime import datetime
import uuid
```

## 5-Minute Quick Start

### 1. Create Storage

```python
# Filesystem (default)
storage = PatternStorage(backend="filesystem", base_path=".moai/patterns")

# SQLite (for large datasets)
storage = PatternStorage(backend="sqlite", base_path=".moai/patterns/patterns")
```

### 2. Create Pattern

```python
pattern: Pattern = {
    "pattern_id": str(uuid.uuid4()),
    "pattern_type": PatternType.TASK_COMPLETION,
    "timestamp": datetime.now().isoformat(),
    "data": {
        "task_type": "code_generation",
        "agent": "expert-backend",
        "duration_ms": 2500,
        "success": True
    },
    "context": {
        "project_name": "my-project",
        "environment": "development",
        "tags": ["backend", "api"]
    },
    "version": "1.0"
}
```

### 3. Save Pattern

```python
storage.save(pattern)  # Returns True on success
```

### 4. Load Pattern

```python
# Load by ID
loaded = storage.load(pattern["pattern_id"])

# Query patterns
patterns = storage.query(
    pattern_type=PatternType.TASK_COMPLETION,
    limit=10
)
```

## Pattern Types

### Task Completion (Agent Performance)

```python
data: TaskCompletionData = {
    "task_type": "code_generation",
    "agent": "expert-backend",
    "duration_ms": 2500,
    "success": True,
    "files_created": 2,
    "tests_passed": 15,
    "lines_of_code": 127,
    "coverage_percent": 92.5
}
```

### Error Occurrence (Learning from Errors)

```python
data: ErrorOccurrenceData = {
    "error_type": "TypeError",
    "error_message": "unsupported operand type",
    "stack_trace": "Traceback...",
    "file_path": "app.py",
    "line_number": 42,
    "resolution": "Convert value to int"
}
```

### Agent Usage (Resource Tracking)

```python
data: AgentUsageData = {
    "agent_type": "expert-backend",
    "task_type": "api_implementation",
    "success": True,
    "duration_ms": 5400,
    "tools_used": ["Read", "Write", "Edit"],
    "tokens_used": 4200
}
```

### User Correction (Learning from Feedback)

```python
data: UserCorrectionData = {
    "original_output": "def foo(): pass",
    "corrected_output": "def foo() -> None: pass",
    "correction_type": "type_hints",
    "agent": "expert-backend",
    "severity": "minor"
}
```

## Advanced Querying

```python
from datetime import timedelta

# Query by date range
patterns = storage.query(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    limit=50
)

# Query by tags
patterns = storage.query(
    tags=["backend", "authentication"],
    limit=20
)

# Query specific type
patterns = storage.query(
    pattern_type=PatternType.ERROR_OCCURRENCE,
    limit=100
)
```

## Lifecycle Management

```python
# Delete old patterns (>90 days)
deleted = storage.delete_old_patterns(retention_days=90)

# Compress old files (filesystem only)
compressed = storage.compress_old_files()
```

## Validation

```python
# Validate before saving
is_valid = PatternSchema.validate_pattern(pattern)

# Validate specific data
is_valid = PatternSchema.validate_task_completion(task_data)
```

## Storage Backends Comparison

| Feature | Filesystem | SQLite |
|---------|------------|--------|
| Setup | Zero config | Zero config |
| Speed (small) | Fast | Faster |
| Speed (large) | Slower | Much faster |
| Readability | High (JSON) | Low (binary) |
| Compression | Yes (auto) | No |
| Querying | O(n) scan | O(log n) indexed |
| Best for | <10K patterns | >10K patterns |

## Common Patterns

### Batch Save

```python
patterns = [create_pattern(i) for i in range(100)]
for pattern in patterns:
    storage.save(pattern)
```

### Migration

```python
# Export from filesystem
fs_storage = PatternStorage(backend="filesystem")
patterns = fs_storage.query(limit=10000)

# Import to SQLite
db_storage = PatternStorage(backend="sqlite")
for pattern in patterns:
    db_storage.save(pattern)
db_storage.close()
```

### Error Analysis

```python
# Get recent errors
errors = storage.query(
    pattern_type=PatternType.ERROR_OCCURRENCE,
    start_date=datetime.now() - timedelta(days=1),
    limit=100
)

# Analyze error patterns
error_types = {}
for error in errors:
    error_type = error["data"]["error_type"]
    error_types[error_type] = error_types.get(error_type, 0) + 1

print("Most common errors:", sorted(error_types.items(), key=lambda x: x[1], reverse=True))
```

## Next Steps

1. **Read README.md** - Comprehensive documentation
2. **Check example_usage.py** - Complete examples
3. **Run tests** - `pytest moai_flow/tests/test_pattern*.py -v`
4. **Explore API** - See API Reference in README.md

## Support

- Documentation: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/patterns/README.md`
- Examples: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/patterns/example_usage.py`
- Tests: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/tests/test_pattern*.py`

## Quick Tips

1. Use **filesystem** for development and debugging
2. Use **SQLite** for production and large datasets
3. Always validate patterns before saving
4. Set appropriate retention policies
5. Use tags for better organization
6. Close SQLite connections when done

---

Happy pattern collecting! 🚀
