# Self-Healing Workflows

> Automatic error recovery and resilience

## Overview

Claude-Flow implements self-healing workflows that automatically detect and recover from failures. **MoAI has basic graceful degradation** but lacks comprehensive self-healing.

---

## Self-Healing Concepts

### 1. Error Detection

Identify failures at multiple levels:

```
┌─────────────────────────────────────────────────┐
│              ERROR DETECTION                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  Level 1: Task Failure                          │
│  ├── Execution error                           │
│  ├── Timeout                                   │
│  └── Invalid output                            │
│                                                 │
│  Level 2: Agent Failure                         │
│  ├── Unresponsive agent                        │
│  ├── Agent crash                               │
│  └── Resource exhaustion                       │
│                                                 │
│  Level 3: System Failure                        │
│  ├── MCP server down                           │
│  ├── Network error                             │
│  └── Memory overflow                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2. Recovery Strategies

```
Error Detected
      │
      ▼
┌─────────────────┐
│ Analyze Error   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────┐
│Retry  │ │Alternative│
│Same   │ │Approach   │
└───┬───┘ └─────┬─────┘
    │           │
    │     ┌─────┴─────┐
    │     │           │
    │     ▼           ▼
    │ ┌───────┐ ┌──────────┐
    │ │Partial│ │Escalate  │
    │ │Result │ │to Human  │
    │ └───────┘ └──────────┘
    │
    ▼
┌───────────────┐
│Resume Workflow│
└───────────────┘
```

### 3. Resilience Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Retry | Retry failed operation | Transient errors |
| Fallback | Use alternative approach | Capability unavailable |
| Circuit Breaker | Stop calling failing service | Persistent failures |
| Bulkhead | Isolate failures | Prevent cascade |
| Checkpoint | Save progress | Long operations |

---

## Claude-Flow Self-Healing

### Error Classification

```javascript
{
  "error_classification": {
    "transient": ["timeout", "rate_limit", "network_error"],
    "recoverable": ["file_not_found", "permission_denied", "syntax_error"],
    "fatal": ["auth_failure", "quota_exceeded", "system_crash"]
  }
}
```

### Recovery Configuration

```javascript
{
  "self_healing": {
    "enabled": true,
    "strategies": {
      "transient": {
        "action": "retry",
        "max_attempts": 3,
        "backoff": "exponential",
        "initial_delay_ms": 1000
      },
      "recoverable": {
        "action": "analyze_and_fix",
        "use_neural_patterns": true,
        "max_fix_attempts": 2
      },
      "fatal": {
        "action": "escalate",
        "notify_user": true,
        "save_state": true
      }
    }
  }
}
```

### Automatic Fix Patterns

```javascript
// File not found
{
  "pattern": "file_not_found_recovery",
  "error": "FileNotFoundError",
  "steps": [
    "search_similar_files",
    "check_renamed",
    "check_different_directory",
    "create_if_missing"
  ]
}

// Syntax error
{
  "pattern": "syntax_error_recovery",
  "error": "SyntaxError",
  "steps": [
    "identify_error_location",
    "suggest_fix",
    "apply_fix",
    "validate_syntax"
  ]
}

// Import error
{
  "pattern": "import_error_recovery",
  "error": "ModuleNotFoundError",
  "steps": [
    "check_requirements",
    "suggest_install",
    "install_dependency",
    "retry_import"
  ]
}
```

---

## Checkpoint System

### Automatic Checkpoints

```javascript
{
  "checkpoints": {
    "enabled": true,
    "auto_checkpoint": {
      "interval_ms": 60000,
      "on_file_write": true,
      "on_task_completion": true
    },
    "storage": ".claude-flow/checkpoints/",
    "retention": {
      "count": 10,
      "days": 7
    }
  }
}
```

### Checkpoint Format

```json
{
  "checkpoint_id": "cp-123",
  "timestamp": "2025-11-29T10:00:00Z",
  "state": {
    "current_task": "implement_api",
    "completed_steps": ["design", "scaffold"],
    "pending_steps": ["implement", "test"],
    "files_modified": ["src/api.py"],
    "context": {
      "requirements": "...",
      "design_decisions": "..."
    }
  }
}
```

### Recovery from Checkpoint

```javascript
// Detect failure and recover
if (task_failed) {
  const checkpoint = load_latest_checkpoint();
  restore_state(checkpoint);
  resume_from_step(checkpoint.state.pending_steps[0]);
}
```

---

## MoAI Current State

### Graceful Degradation

MoAI has basic graceful degradation:

```json
{
  "hooks": {
    "graceful_degradation": true
  }
}
```

This means hooks failing won't crash the system.

### Error Handling in Agents

Agents handle errors internally but lack:
- Automatic retry
- Pattern-based recovery
- Checkpoint/resume
- Alternative strategies

### What MoAI Has

| Feature | Status |
|---------|--------|
| Graceful degradation | ✅ Yes |
| Hook error handling | ✅ Yes |
| Agent error reporting | ✅ Yes |
| Manual recovery | ✅ Yes |

### What MoAI Lacks

| Feature | Status |
|---------|--------|
| Automatic retry | ❌ No |
| Pattern-based recovery | ❌ No |
| Checkpoints | ❌ No |
| Self-healing workflows | ❌ No |
| Circuit breakers | ❌ No |
| Error classification | ❌ No |

---

## Implementation Options

### Option 1: Add Retry Configuration

```json
{
  "error_handling": {
    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "backoff": "exponential",
      "retryable_errors": [
        "TimeoutError",
        "ConnectionError",
        "RateLimitError"
      ]
    }
  }
}
```

### Option 2: Add Checkpoints

```json
{
  "checkpoints": {
    "enabled": true,
    "auto_save": {
      "on_task_completion": true,
      "interval_minutes": 5
    },
    "storage": ".moai/checkpoints/",
    "retention_days": 7
  }
}
```

### Option 3: Add Recovery Patterns

```json
{
  "recovery_patterns": {
    "file_not_found": {
      "action": "search_and_suggest",
      "fallback": "create_file"
    },
    "import_error": {
      "action": "install_dependency",
      "fallback": "suggest_manual"
    },
    "syntax_error": {
      "action": "analyze_and_fix",
      "fallback": "show_diff"
    }
  }
}
```

---

## Proposed MoAI Self-Healing

### Configuration

```json
{
  "self_healing": {
    "enabled": true,

    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "backoff_ms": [1000, 2000, 4000],
      "retryable": ["timeout", "rate_limit", "connection"]
    },

    "checkpoints": {
      "enabled": true,
      "auto_save": true,
      "storage": ".moai/checkpoints/"
    },

    "recovery": {
      "analyze_errors": true,
      "suggest_fixes": true,
      "auto_fix": false
    },

    "escalation": {
      "max_failures": 3,
      "notify_user": true,
      "save_debug_info": true
    }
  }
}
```

### Recovery Flow

```python
def execute_with_healing(task):
    checkpoint = create_checkpoint()

    for attempt in range(max_attempts):
        try:
            result = execute_task(task)
            return result
        except RetryableError as e:
            if attempt < max_attempts - 1:
                wait(backoff_ms[attempt])
                continue
            raise
        except RecoverableError as e:
            fix = analyze_and_suggest_fix(e)
            if fix and auto_fix_enabled:
                apply_fix(fix)
                continue
            raise
        except FatalError as e:
            save_debug_info(e, checkpoint)
            notify_user(e)
            raise
```

---

## Recommendation

### Priority: P2 (Medium)

Self-healing improves reliability significantly.

### Phase 1: Add Retry (Week 1)

```json
{
  "error_handling": {
    "retry": {
      "enabled": true,
      "max_attempts": 3
    }
  }
}
```

### Phase 2: Add Checkpoints (Week 2-3)

```json
{
  "checkpoints": {
    "enabled": true,
    "auto_save": true
  }
}
```

### Phase 3: Add Recovery Patterns (Month 2)

```json
{
  "recovery_patterns": {
    "enabled": true,
    "patterns": { ... }
  }
}
```

---

## Summary

Self-healing workflows make systems more resilient. MoAI has basic graceful degradation but lacks sophisticated self-healing. Adding retry logic and checkpoints would be valuable first steps. Full self-healing with pattern-based recovery is a larger undertaking but provides significant reliability improvements.
