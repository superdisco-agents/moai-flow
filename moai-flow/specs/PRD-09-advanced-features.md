# PRD-09: Advanced Features

> Cross-session memory, self-healing, and bottleneck analysis

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P3 (Nice-to-Have) |
| **Effort** | High (3+ months) |
| **Impact** | Low-Medium |
| **Type** | Advanced Infrastructure |

---

## Scope

This PRD covers three advanced features from MoAI-Flow:

1. **Cross-Session Memory** - Enhanced context persistence
2. **Self-Healing Workflows** - Automatic error recovery
3. **Bottleneck Analysis** - Automatic performance optimization

---

## Feature 1: Cross-Session Memory Enhancement

### Current MoAI State

MoAI has basic session state saving:

```json
{
  "session_end": {
    "work_state": {
      "enabled": true,
      "save_location": ".moai/memory/last-session-state.json"
    }
  }
}
```

### Enhancement Goals

```
CURRENT:
├── Session state saved
├── Last working directory
└── Recent files list

ENHANCED:
├── Session state saved
├── Context hints (learned preferences)
├── Project knowledge (patterns, conventions)
├── Episode history (past decisions)
└── Semantic memory (concepts learned)
```

### Implementation

**Phase 1: Context Hints**

```json
{
  "memory": {
    "context_hints": {
      "enabled": true,
      "max_hints": 100,
      "storage": ".moai/memory/context-hints.json"
    }
  }
}
```

**Context Hints Format**:

```json
{
  "hints": [
    {
      "type": "preference",
      "key": "code_style",
      "value": "explicit",
      "confidence": 0.95,
      "source": "user_correction",
      "learned_at": "2025-11-29T10:00:00Z"
    },
    {
      "type": "pattern",
      "key": "api_route_structure",
      "value": "/api/v1/{resource}",
      "confidence": 0.88,
      "source": "observed"
    }
  ]
}
```

**Phase 2: Project Knowledge**

```json
{
  "memory": {
    "project_knowledge": {
      "enabled": true,
      "auto_detect": true,
      "storage": ".moai/memory/project-knowledge.json"
    }
  }
}
```

**Project Knowledge Format**:

```json
{
  "knowledge": {
    "architecture": "layered",
    "frameworks": ["FastAPI", "React"],
    "testing": {
      "framework": "pytest",
      "coverage_target": 90
    },
    "patterns": {
      "naming": "snake_case",
      "imports": "grouped"
    }
  }
}
```

---

## Feature 2: Self-Healing Workflows

### Current MoAI State

MoAI has graceful degradation for hooks:

```json
{
  "hooks": {
    "graceful_degradation": true
  }
}
```

### Enhancement Goals

```
CURRENT:
├── Hook failure → Continue
└── Error → Report to user

ENHANCED:
├── Retry transient errors
├── Recover from known patterns
├── Checkpoint/resume
├── Automatic fix suggestions
└── Escalate only when needed
```

### Implementation

**Phase 1: Retry Logic**

```json
{
  "self_healing": {
    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "backoff_ms": [1000, 2000, 4000],
      "retryable_errors": [
        "timeout",
        "rate_limit",
        "connection_error"
      ]
    }
  }
}
```

**Phase 2: Checkpoints**

```json
{
  "self_healing": {
    "checkpoints": {
      "enabled": true,
      "auto_save": {
        "on_task_completion": true,
        "interval_minutes": 5
      },
      "storage": ".moai/checkpoints/"
    }
  }
}
```

**Checkpoint Format**:

```json
{
  "checkpoint_id": "cp-001",
  "timestamp": "2025-11-29T10:00:00Z",
  "state": {
    "current_task": "implement_api",
    "completed_steps": ["design", "scaffold"],
    "pending_steps": ["implement", "test"],
    "files_modified": ["src/api.py"],
    "context": { ... }
  }
}
```

**Phase 3: Recovery Patterns**

```json
{
  "self_healing": {
    "recovery_patterns": {
      "file_not_found": {
        "action": "search_and_suggest",
        "fallback": "create_if_confirmed"
      },
      "import_error": {
        "action": "install_dependency",
        "fallback": "suggest_manual"
      },
      "syntax_error": {
        "action": "analyze_and_suggest_fix"
      }
    }
  }
}
```

---

## Feature 3: Bottleneck Analysis

### Current MoAI State

MoAI has manual token awareness:

```markdown
# Rule 4: Token Management
When Context > 180K, MUST guide user to execute /clear
```

### Enhancement Goals

```
CURRENT:
├── Manual token threshold
└── User-initiated cleanup

ENHANCED:
├── Automatic token monitoring
├── Serial execution detection
├── Agent queue monitoring
├── Auto-suggestions
└── Performance alerts
```

### Implementation

**Phase 1: Token Monitoring**

```json
{
  "bottleneck_detection": {
    "token_monitoring": {
      "enabled": true,
      "warn_threshold": 0.75,
      "critical_threshold": 0.90,
      "auto_suggest_clear": true
    }
  }
}
```

**Phase 2: Execution Analysis**

```json
{
  "bottleneck_detection": {
    "execution_analysis": {
      "enabled": true,
      "detect_serial_chains": true,
      "suggest_parallelization": true,
      "min_chain_length": 3
    }
  }
}
```

**Alert Format**:

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ BOTTLENECK DETECTED                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Type: Serial Execution                                  │
│ Location: Tasks task-001, task-002, task-003           │
│                                                         │
│ Suggestion:                                             │
│ These tasks appear independent and could run in        │
│ parallel. Consider batching in a single message.       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Combined Configuration

```json
{
  "advanced": {
    "cross_session_memory": {
      "enabled": false,
      "context_hints": true,
      "project_knowledge": true,
      "episodes": false
    },

    "self_healing": {
      "enabled": false,
      "retry": {
        "enabled": true,
        "max_attempts": 3
      },
      "checkpoints": {
        "enabled": false,
        "auto_save": true
      },
      "recovery_patterns": {
        "enabled": false
      }
    },

    "bottleneck_detection": {
      "enabled": false,
      "token_monitoring": true,
      "execution_analysis": false
    }
  }
}
```

---

## Implementation Roadmap

### Cross-Session Memory (Month 1)

```
Week 1-2: Context hints implementation
Week 3-4: Project knowledge auto-detection
```

### Self-Healing (Month 2)

```
Week 5-6: Retry logic implementation
Week 7-8: Checkpoint system
```

### Bottleneck Detection (Month 3)

```
Week 9-10: Token monitoring
Week 11-12: Execution analysis
```

---

## Acceptance Criteria

### Cross-Session Memory
- [ ] Context hints saved and loaded
- [ ] Project knowledge auto-detected
- [ ] Session resumption uses hints

### Self-Healing
- [ ] Transient errors retried
- [ ] Checkpoints created
- [ ] Recovery patterns functional

### Bottleneck Detection
- [ ] Token warnings displayed
- [ ] Serial chains detected
- [ ] Suggestions generated

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-complexity | High | High | Incremental rollout |
| Performance impact | Medium | Medium | Async processing |
| Storage growth | Medium | Low | Retention policies |
| User confusion | Low | Medium | Clear documentation |

---

## Success Metrics

| Feature | Metric | Target |
|---------|--------|--------|
| Memory | Context restoration accuracy | > 90% |
| Self-Healing | Error recovery rate | > 80% |
| Bottleneck | Token savings | > 15% |

---

## Related Documents

- [Cross-Session Memory](../advanced/03-cross-session-memory.md)
- [Self-Healing Workflows](../advanced/04-self-healing.md)
- [Bottleneck Analysis](../advanced/06-bottleneck-analysis.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Month 1: Cross-session memory
Month 2: Self-healing workflows
Month 3: Bottleneck detection

Total: 3 months
```

---

## Conclusion

These advanced features are lower priority but provide significant quality-of-life improvements. They should be implemented after P1 and P2 items are complete. Each feature can be enabled independently, allowing gradual adoption.
