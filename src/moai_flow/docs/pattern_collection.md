# Pattern Collection System

**PRD-05 Phase 1: Pattern Logging Integration**

Complete implementation of automatic pattern collection via PostTask hooks.

---

## Overview

The pattern collection system automatically collects execution patterns through the Phase 7 hooks system. Patterns are collected without machine learning (ML) - this is simple data collection for future analysis.

### What It Does

- ✅ **Task Completion Patterns**: Agent usage, duration, success/failure
- ✅ **Error Occurrence Patterns**: Error types, contexts, resolutions
- ✅ **Agent Usage Patterns**: Usage statistics and performance
- ✅ **Graceful Degradation**: Pattern collection never fails the task
- ✅ **Configuration Integration**: Controlled via `.moai/config/config.json`

---

## Architecture

```
┌─────────────────────────────────────────────┐
│          Task Execution                     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Phase 7 Hook Registry                  │
├─────────────────────────────────────────────┤
│  POST Phase                                 │
│  ├─ PostTaskPatternHook (Priority: LOW)    │
│  │   └─ Collects task completion           │
│  │                                          │
│  ERROR Phase                                │
│  └─ ErrorPatternHook (Priority: LOW)       │
│      └─ Collects error occurrence          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      PatternCollector                       │
├─────────────────────────────────────────────┤
│  - Generate pattern ID                      │
│  - Store pattern to disk                    │
│  - Date-based directory hierarchy           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Storage (.moai/patterns/)              │
├─────────────────────────────────────────────┤
│  2025/                                      │
│  └── 11/                                    │
│      └── 29/                                │
│          ├── task_completion_*.json         │
│          └── error_occurrence_*.json        │
└─────────────────────────────────────────────┘
```

---

## Installation

### Step 1: Import Components

```python
from moai_flow.hooks import HookRegistry
from moai_flow.hooks.post_task_pattern import register_pattern_hooks
from moai_flow.patterns import PatternCollector
```

### Step 2: Register Hooks

```python
# Initialize hook registry
registry = HookRegistry()

# Register pattern collection hooks
register_pattern_hooks(registry)

# Hooks are now active and will collect patterns automatically
```

### Step 3: Configure (Optional)

Edit `.moai/config/config.json`:

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
  },
  "hooks": {
    "post_task": {
      "pattern_collection": {
        "enabled": true,
        "priority": "low"
      }
    },
    "on_error": {
      "pattern_collection": {
        "enabled": true,
        "priority": "low"
      }
    }
  }
}
```

---

## Usage Examples

### Example 1: Basic Pattern Collection

```python
from moai_flow.patterns import PatternCollector

# Initialize collector
collector = PatternCollector()

# Collect task completion
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

print(f"Collected pattern: {pattern_id}")
# Output: Collected pattern: pat-20251129-143000-001
```

### Example 2: Hook Integration

```python
from moai_flow.hooks import HookRegistry, HookContext, HookPhase
from moai_flow.hooks.post_task_pattern import register_pattern_hooks
import time

# Initialize and register
registry = HookRegistry()
register_pattern_hooks(registry)

# Simulate task completion
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

# Execute hooks (pattern collected automatically)
results = registry.execute_hooks("task_complete", HookPhase.POST, context)

for result in results:
    if "pattern_id" in result.metadata:
        print(f"Pattern collected: {result.metadata['pattern_id']}")
```

### Example 3: Error Pattern Collection

```python
from moai_flow.hooks import HookContext, HookPhase

# Simulate error
error_context = HookContext(
    phase=HookPhase.ERROR,
    event_type="task_failed",
    data={
        "error_type": "ValidationError",
        "error_message": "Invalid API key format",
        "resolution": "Added API key validation middleware"
    },
    metadata={"endpoint": "/api/v1/users"},
    timestamp=time.time()
)

# Execute error hooks
results = registry.execute_hooks("task_failed", HookPhase.ERROR, error_context)
```

### Example 4: Get Statistics

```python
collector = PatternCollector()

stats = collector.get_statistics()

print(f"Total patterns: {stats['total_patterns']}")
print(f"Task completions: {stats['by_type']['task_completion']}")
print(f"Error occurrences: {stats['by_type']['error_occurrence']}")
```

---

## Pattern Format

### Task Completion Pattern

```json
{
  "pattern_id": "pat-20251129-143000-001",
  "type": "task_completion",
  "timestamp": "2025-11-29T14:30:00.123456",
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

### Error Occurrence Pattern

```json
{
  "pattern_id": "pat-20251129-143500-002",
  "type": "error_occurrence",
  "timestamp": "2025-11-29T14:35:00.987654",
  "data": {
    "error_type": "ValidationError",
    "error_message": "Invalid API key format",
    "resolution": "Added API key validation middleware"
  },
  "context": {
    "endpoint": "/api/v1/users",
    "file": "api/auth.py",
    "function": "validate_api_key"
  }
}
```

---

## Storage Structure

```
.moai/patterns/
├── 2025/
│   └── 11/
│       └── 29/
│           ├── task_completion_20251129_100000.json
│           ├── task_completion_20251129_110000.json
│           ├── error_occurrence_20251129_120000.json
│           └── agent_usage_20251129_150000.json
└── analysis/
    ├── weekly_2025-11-24.json
    └── monthly_2025-11.json
```

### Date Hierarchy Benefits

- **Organization**: Easy to find patterns by date
- **Cleanup**: Simple to delete old patterns
- **Analysis**: Natural grouping for time-based analysis
- **Performance**: Reduces directory size for faster access

---

## Configuration Reference

### Pattern Collection Settings

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

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable pattern collection |
| `storage` | string | `.moai/patterns/` | Storage directory path |
| `collect.task_completion` | boolean | `true` | Collect task completion patterns |
| `collect.error_occurrence` | boolean | `true` | Collect error patterns |
| `collect.agent_usage` | boolean | `true` | Collect agent usage patterns |
| `collect.user_correction` | boolean | `false` | Collect user correction patterns |
| `retention_days` | number | `90` | Days to retain patterns |

### Hook Settings

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true,
    "post_task": {
      "pattern_collection": {
        "enabled": true,
        "priority": "low"
      }
    },
    "on_error": {
      "pattern_collection": {
        "enabled": true,
        "priority": "low"
      }
    }
  }
}
```

---

## Graceful Degradation

Pattern collection is designed to **never fail the task**:

```python
try:
    # Collect pattern
    pattern_id = collector.collect_task_completion(...)
    return HookResult(success=True, metadata={"pattern_id": pattern_id})
except Exception as e:
    # Log error but don't fail
    logger.warning(f"Pattern collection failed: {e}")
    return HookResult(success=False, error=e, metadata={"error": str(e)})
```

### Error Handling Strategy

1. **Hook Execution**: If pattern collection fails, hook returns `success=False` but doesn't raise exception
2. **Task Execution**: Task continues normally regardless of pattern collection status
3. **Logging**: Errors are logged for debugging
4. **Statistics**: Failed collections are tracked in hook statistics

---

## Testing

### Run Tests

```bash
cd moai_flow
pytest tests/test_post_task_pattern.py -v
```

### Test Coverage

- ✅ Hook initialization
- ✅ Hook execution (success and failure)
- ✅ Graceful degradation
- ✅ Hook registration
- ✅ Full integration tests
- ✅ Statistics collection

---

## Future Enhancements (PRD-05 Phases 2-4)

### Phase 2: Pattern Analysis (Month 2)

- Analysis scripts for pattern data
- Weekly/monthly reports
- Agent performance visibility

### Phase 3: Evaluation (Month 3)

- Evaluate collected data
- ML decision point
- Roadmap update

### Phase 4: Optional ML Integration (Month 4+)

- MoAI-Flow Neural MCP integration OR
- Custom ML model training
- Adaptive recommendations

---

## Related Documentation

- [PRD-05: Neural Training](../specs/PRD-05-neural-training.md)
- [Phase 7: Hook System](./hooks.md)
- [Pattern Collector API](./api/pattern_collector.md)

---

## API Reference

### PatternCollector

```python
class PatternCollector:
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        enabled: bool = True
    )

    def collect_task_completion(
        self,
        task_type: str,
        agent: str,
        duration_ms: float,
        success: bool,
        files_created: int = 0,
        tests_passed: int = 0,
        context: Optional[Dict[str, Any]] = None
    ) -> str

    def collect_error_occurrence(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        resolution: Optional[str] = None
    ) -> str

    def get_pattern_stats(self) -> Dict[str, Any]
```

### register_pattern_hooks

```python
def register_pattern_hooks(
    hook_registry,
    collector: Optional[PatternCollector] = None,
    enabled: bool = True
) -> None
```

Registers PostTask and Error pattern hooks with the hook registry.

---

**Status**: Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-11-29
**PRD**: PRD-05 Phase 1
