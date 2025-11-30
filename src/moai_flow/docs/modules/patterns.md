# Pattern Storage & Schema System

## Overview

The Pattern Storage & Schema system provides a robust foundation for collecting, storing, and analyzing patterns across MoAI-Flow. It supports multiple pattern types (task completion, error occurrence, agent usage, user corrections) with flexible storage backends (filesystem and SQLite).

## Features

- **Comprehensive Schema Definitions**: TypedDict-based schemas with strict validation
- **Multiple Storage Backends**: Filesystem (date-based hierarchy) and SQLite (relational)
- **Pattern Types**: Task completion, error occurrence, agent usage, user corrections
- **Flexible Querying**: Filter by type, date range, tags
- **Lifecycle Management**: Automatic compression and retention policies
- **Type Safety**: Full type hints with mypy compatibility

## Architecture

```
moai_flow/patterns/
├── schema.py           # Pattern schema definitions and validators
├── storage.py          # Storage backend implementation
├── example_usage.py    # Usage examples
├── __init__.py         # Module exports
└── README.md           # This file

tests/
├── test_pattern_schema.py   # Schema validation tests (31 tests)
└── test_pattern_storage.py  # Storage backend tests (21 tests)
```

## Pattern Types

### 1. Task Completion Pattern

Captures task execution metrics and outcomes.

```python
from moai_flow.patterns import TaskCompletionData

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
```

### 2. Error Occurrence Pattern

Captures error details for pattern analysis and learning.

```python
from moai_flow.patterns import ErrorOccurrenceData

error_data: ErrorOccurrenceData = {
    "error_type": "TypeError",
    "error_message": "unsupported operand type(s) for +: 'int' and 'str'",
    "stack_trace": "Traceback...",
    "file_path": "app.py",
    "line_number": 42,
    "function_name": "process_data",
    "resolution": "Convert value to int before addition",
    "resolution_time_ms": 3200,
    "similar_errors_count": 2,
    "auto_resolved": False,
    "user_intervention": True
}
```

### 3. Agent Usage Pattern

Tracks agent performance and behavior patterns.

```python
from moai_flow.patterns import AgentUsageData

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
```

### 4. User Correction Pattern

Captures user corrections to learn from mistakes.

```python
from moai_flow.patterns import UserCorrectionData

correction_data: UserCorrectionData = {
    "original_output": "def process_data(data):\n    return data + 1",
    "corrected_output": "def process_data(data: List[int]) -> List[int]:\n    return [x + 1 for x in data]",
    "correction_type": "type_safety",
    "agent": "expert-backend",
    "task_type": "code_generation",
    "correction_category": "code_quality",
    "user_feedback": "Add type hints and handle list input properly",
    "severity": "moderate"
}
```

## Storage Backends

### Filesystem Backend (Default)

Date-based hierarchical storage with optional compression.

**Directory Structure**:
```
.moai/patterns/
├── 2025/
│   ├── 11/
│   │   ├── 29/
│   │   │   ├── task_20251129_100000.json
│   │   │   ├── task_20251129_110000.json
│   │   │   └── error_20251129_120000.json
│   │   └── 30/
│   └── 12/
└── index.json  # Optional index for fast queries
```

**Features**:
- Date-based hierarchy (YYYY/MM/DD)
- Automatic compression for files > 30 days old (gzip)
- Optional indexing for fast lookups
- Pretty-printed JSON for readability

**Usage**:
```python
from moai_flow.patterns import PatternStorage

storage = PatternStorage(
    backend="filesystem",
    base_path=".moai/patterns",
    compression_threshold_days=30,
    retention_days=90
)
```

### SQLite Backend

Relational database with indexing for fast queries.

**Schema**:
```sql
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    data TEXT NOT NULL,  -- JSON blob
    context TEXT,        -- JSON blob
    version TEXT DEFAULT '1.0',
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX idx_type_timestamp ON patterns(pattern_type, timestamp);
```

**Features**:
- Efficient querying with indexes
- ACID transactions
- Compact storage
- Full-text search capabilities

**Usage**:
```python
from moai_flow.patterns import PatternStorage

storage = PatternStorage(
    backend="sqlite",
    base_path=".moai/patterns/patterns",  # Creates patterns.db
    retention_days=90
)
```

## Basic Usage

### Saving Patterns

```python
from datetime import datetime
import uuid
from moai_flow.patterns import Pattern, PatternType, PatternStorage

# Create pattern
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
        "project_name": "moai-adk",
        "environment": "development",
        "tags": ["backend", "test"]
    },
    "version": "1.0"
}

# Save pattern
storage = PatternStorage(backend="filesystem")
storage.save(pattern)
```

### Loading Patterns

```python
# Load by ID
pattern = storage.load("pattern-id-123")

# Query by type
patterns = storage.query(
    pattern_type=PatternType.TASK_COMPLETION,
    limit=10
)

# Query by date range
from datetime import timedelta

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
```

### Pattern Validation

```python
from moai_flow.patterns import PatternSchema

# Validate complete pattern
is_valid = PatternSchema.validate_pattern(pattern)

# Validate specific pattern data
is_valid = PatternSchema.validate_task_completion(task_data)
is_valid = PatternSchema.validate_error_occurrence(error_data)
is_valid = PatternSchema.validate_agent_usage(usage_data)
is_valid = PatternSchema.validate_user_correction(correction_data)
```

### Lifecycle Management

```python
# Delete patterns older than 90 days
deleted_count = storage.delete_old_patterns(retention_days=90)

# Compress files older than 30 days (filesystem only)
compressed_count = storage.compress_old_files()
```

## Advanced Usage

### Custom Context

```python
from moai_flow.patterns import PatternContext

context: PatternContext = {
    "project_name": "moai-adk",
    "session_id": "session-123",
    "user_id": "user-456",
    "environment": "production",
    "git_branch": "main",
    "git_commit": "abc123",
    "timestamp": datetime.now().isoformat(),
    "tags": ["production", "critical", "security"],
    "metadata": {
        "deployment_id": "deploy-789",
        "region": "us-west-2"
    }
}
```

### Batch Operations

```python
# Save multiple patterns
patterns = [create_pattern() for _ in range(100)]
for pattern in patterns:
    storage.save(pattern)

# Query in batches
offset = 0
batch_size = 50

while True:
    batch = storage.query(
        pattern_type=PatternType.AGENT_USAGE,
        limit=batch_size
    )
    if not batch:
        break

    process_batch(batch)
    offset += batch_size
```

### Migration Between Backends

```python
# Export from filesystem
fs_storage = PatternStorage(backend="filesystem", base_path=".moai/patterns")
patterns = fs_storage.query(limit=1000)

# Import to SQLite
db_storage = PatternStorage(backend="sqlite", base_path=".moai/patterns/patterns")
for pattern in patterns:
    db_storage.save(pattern)

db_storage.close()
```

## Schema Validation Rules

### Required Fields

| Pattern Type | Required Fields |
|--------------|-----------------|
| TaskCompletion | task_type, agent, duration_ms, success |
| ErrorOccurrence | error_type, error_message |
| AgentUsage | agent_type, task_type, success, duration_ms |
| UserCorrection | original_output, corrected_output, correction_type, agent |

### Field Constraints

- **duration_ms**: Must be >= 0
- **coverage_percent**: Must be 0-100
- **line_number**: Must be >= 0
- **severity**: Must be one of: "minor", "moderate", "critical"
- **environment**: Must be one of: "development", "staging", "production"
- **timestamp**: Must be valid ISO 8601 format

### Type Constraints

- All string fields: Must be non-empty strings
- All list fields: Must contain only strings
- All numeric fields: Must be int or float (as appropriate)
- All boolean fields: Must be true or false

## Performance Characteristics

### Filesystem Backend

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Save | O(1) | Constant time write |
| Load by ID | O(n) or O(1) | O(n) without index, O(1) with index |
| Query by type | O(n) | Must scan all files |
| Delete old | O(n) | Must check all files |
| Compress | O(n) | Must check all files |

**Best for**: Small to medium datasets (<10K patterns), human-readable storage, debugging

### SQLite Backend

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| Save | O(log n) | B-tree insert |
| Load by ID | O(log n) | Indexed lookup |
| Query by type | O(log n + k) | Indexed scan + k results |
| Delete old | O(log n + k) | Indexed scan + delete |

**Best for**: Large datasets (>10K patterns), fast queries, production use

## Testing

Run comprehensive test suite:

```bash
# Schema validation tests (31 tests)
python3 -m pytest moai_flow/tests/test_pattern_schema.py -v

# Storage backend tests (21 tests)
python3 -m pytest moai_flow/tests/test_pattern_storage.py -v

# All pattern tests
python3 -m pytest moai_flow/tests/test_pattern*.py -v
```

## Examples

See `example_usage.py` for comprehensive examples:

```bash
python3 moai_flow/patterns/example_usage.py
```

## Future Enhancements

Planned features for future phases:

1. **Pattern Analysis** (Phase 2)
   - Statistical analysis of patterns
   - Trend detection and anomaly identification
   - Pattern clustering and classification

2. **Pattern Application** (Phase 3)
   - Automatic error resolution
   - Performance optimization recommendations
   - Code quality improvements

3. **Advanced Features**
   - Real-time pattern streaming
   - Distributed storage backends
   - Machine learning integration
   - Visualization dashboards

## API Reference

### PatternStorage

**Constructor**:
```python
PatternStorage(
    backend: Literal["filesystem", "sqlite"] = "filesystem",
    base_path: str = ".moai/patterns",
    compression_threshold_days: int = 30,
    retention_days: int = 90
)
```

**Methods**:
- `save(pattern: Pattern) -> bool` - Save pattern to storage
- `load(pattern_id: str) -> Optional[Pattern]` - Load pattern by ID
- `query(...)` - Query patterns with filters
- `delete_old_patterns(retention_days: int) -> int` - Delete old patterns
- `compress_old_files() -> int` - Compress old files (filesystem only)
- `close()` - Close storage backend (SQLite only)

### PatternSchema

**Static Methods**:
- `validate_pattern(pattern: Dict) -> bool` - Validate complete pattern
- `validate_task_completion(data: Dict) -> bool` - Validate task data
- `validate_error_occurrence(data: Dict) -> bool` - Validate error data
- `validate_agent_usage(data: Dict) -> bool` - Validate agent usage data
- `validate_user_correction(data: Dict) -> bool` - Validate correction data
- `validate_context(context: Dict) -> bool` - Validate pattern context

## License

Part of MoAI-ADK. See LICENSE for details.

## Changelog

### Version 1.0.0 (2025-11-29)

- Initial implementation
- Filesystem and SQLite storage backends
- Four pattern types (task completion, error occurrence, agent usage, user correction)
- Comprehensive schema validation
- 52 passing tests (31 schema + 21 storage)
- Date-based filesystem hierarchy
- Automatic compression and retention policies
- Type-safe TypedDict schemas
