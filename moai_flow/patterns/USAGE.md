# Pattern Collector Usage Examples

Quick reference for using the Pattern Collection System (PRD-05 Phase 1).

## Basic Usage

```python
from moai_flow.patterns.pattern_collector import PatternCollector, PatternType

# Initialize (uses .moai/patterns by default)
collector = PatternCollector()

# Collect task completion
pattern_id = collector.collect_task_completion(
    task_type="api_implementation",
    agent="expert-backend",
    duration_ms=45000,
    success=True,
    files_created=3,
    tests_passed=12,
    context={"framework": "fastapi", "spec_id": "SPEC-001"}
)
```

## Pattern Types

### 1. Task Completion
```python
collector.collect_task_completion(
    task_type="api_implementation",
    agent="expert-backend",
    duration_ms=45000,
    success=True,
    files_created=3,
    tests_passed=12,
    context={"framework": "fastapi", "language": "python"}
)
```

### 2. Error Occurrence
```python
collector.collect_error_occurrence(
    error_type="ValidationError",
    error_message="Invalid API key",
    context={"file": "api/auth.py", "line": 42},
    resolution="Added validation"
)
```

### 3. Agent Usage
```python
collector.collect_agent_usage(
    agent_type="expert-backend",
    task_type="api_implementation",
    success=True,
    duration_ms=45000
)
```

### 4. User Correction (must enable in config)
```python
collector.collect_user_correction(
    original_output="def add(a, b): return a + b",
    corrected_output="def add(a: int, b: int) -> int: return a + b",
    correction_type="type_hints_missing"
)
```

## Querying

```python
# Get all task completions
patterns = collector.get_patterns(PatternType.TASK_COMPLETION)

# Get with date range
from datetime import datetime
patterns = collector.get_patterns(
    pattern_type=PatternType.ERROR_OCCURRENCE,
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2025, 11, 30),
    limit=50
)

# Get count
total = collector.get_pattern_count()
task_count = collector.get_pattern_count(PatternType.TASK_COMPLETION)

# Get statistics
stats = collector.get_statistics()
print(stats)
```

## Maintenance

```python
# Cleanup old patterns (older than retention_days)
deleted = collector.cleanup_old_patterns()

# Compress old patterns (older than 30 days)
compressed = collector.compress_old_patterns(days_old=30)
```

## Configuration

Add to `.moai/config/config.json`:

```json
{
  "patterns": {
    "enabled": true,
    "storage": ".moai/patterns/",
    "collect": {
      "task_completion": true,
      "error_occurrence": true,
      "agent_usage": true,
      "user_correction": false
    },
    "retention_days": 90
  }
}
```

## Storage Structure

```
.moai/patterns/
└── 2025/
    └── 11/
        └── 29/
            ├── task_completion_20251129_100000_123456.json
            ├── error_occurrence_20251129_120000_234567.json
            └── agent_usage_20251129_150000_345678.json
```

## Example Pattern File

```json
{
  "pattern_id": "pat-20251129-100000-001",
  "type": "task_completion",
  "timestamp": "2025-11-29T10:00:00.123456",
  "data": {
    "task_type": "api_implementation",
    "agent": "expert-backend",
    "duration_ms": 45000,
    "success": true,
    "files_created": 3,
    "tests_passed": 12
  },
  "context": {
    "framework": "fastapi",
    "language": "python",
    "spec_id": "SPEC-001"
  }
}
```
