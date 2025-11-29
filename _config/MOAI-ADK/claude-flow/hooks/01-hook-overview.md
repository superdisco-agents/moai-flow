# Hook System Overview

> Claude-Flow's lifecycle event management

## Overview

Claude-Flow uses hooks to manage lifecycle events during agent operations. Hooks provide control points for validation, logging, and coordination.

---

## Hook Categories

### 1. Pre-Operation Hooks

Execute BEFORE an operation starts.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `PreTask` | Before task creation | Validate, authorize |
| `PreAgent` | Before agent spawn | Check resources |
| `PreFile` | Before file operation | Validate paths |
| `PreSwarm` | Before swarm init | Setup environment |

### 2. Post-Operation Hooks

Execute AFTER an operation completes.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `PostTask` | After task completion | Log results |
| `PostAgent` | After agent terminates | Cleanup |
| `PostFile` | After file operation | Verify changes |
| `PostSwarm` | After swarm shutdown | Metrics collection |

### 3. Session Hooks

Manage session lifecycle.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `SessionStart` | Session begins | Initialize state |
| `SessionEnd` | Session ends | Save state, cleanup |
| `SessionResume` | Session continues | Restore context |

### 4. Coordination Hooks

Manage multi-agent coordination.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `OnConsensus` | Consensus reached | Record decision |
| `OnConflict` | Conflict detected | Resolution trigger |
| `OnHeartbeat` | Agent heartbeat | Health monitoring |

---

## Hook Configuration

### Basic Structure

```json
{
  "hooks": {
    "PreTask": {
      "enabled": true,
      "timeout_ms": 5000,
      "command": "validate-task.sh"
    },
    "PostTask": {
      "enabled": true,
      "timeout_ms": 3000,
      "command": "log-task.sh"
    }
  }
}
```

### Hook Script Pattern

```bash
#!/bin/bash
# Pre-task validation hook

TASK_TYPE=$1
TASK_PRIORITY=$2

# Validate task
if [[ "$TASK_PRIORITY" == "critical" ]]; then
    echo "Critical task requires approval"
    exit 1  # Block operation
fi

exit 0  # Allow operation
```

---

## Execution Flow

```
User Request
    │
    ▼
┌─────────────────┐
│   PreTask Hook  │ ◄── Validate, authorize
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Task Execution │ ◄── Actual work
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostTask Hook  │ ◄── Log, cleanup
└─────────────────┘
```

---

## MoAI Hook Comparison

### MoAI Current Hooks

MoAI already has a hook system:

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true
  }
}
```

**MoAI Hook Events**:
- `SessionStart` - Session initialization
- `SessionEnd` - Session cleanup
- `PreUserPromptSubmit` - Before user input processing

### Gap Analysis

| Hook Type | Claude-Flow | MoAI |
|-----------|-------------|------|
| Pre-Operation | Yes | Partial |
| Post-Operation | Yes | Limited |
| Session | Yes | Yes |
| Coordination | Yes | No |
| Agent Lifecycle | Yes | No |
| Swarm Events | Yes | No |

---

## Key Differences

### Claude-Flow Approach

1. **Fine-grained control**: Hooks at every operation level
2. **Coordination hooks**: Multi-agent event handling
3. **Self-healing**: Automatic recovery via hooks
4. **Metrics collection**: Built-in performance tracking

### MoAI Approach

1. **Session-focused**: Primary focus on session lifecycle
2. **Graceful degradation**: Continues if hooks fail
3. **Simpler model**: Fewer hook points
4. **Configuration-driven**: JSON-based setup

---

## Recommendation for MoAI

### Priority 1: Add Operation Hooks

```json
{
  "hooks": {
    "PreTask": { "enabled": true },
    "PostTask": { "enabled": true },
    "PreAgent": { "enabled": true },
    "PostAgent": { "enabled": true }
  }
}
```

### Priority 2: Add Coordination Hooks

For future swarm support:

```json
{
  "hooks": {
    "OnConsensus": { "enabled": true },
    "OnConflict": { "enabled": true },
    "OnHeartbeat": { "enabled": true }
  }
}
```

---

## Summary

Claude-Flow's hook system provides comprehensive lifecycle management. MoAI has basic session hooks but lacks operation-level and coordination hooks. Adding these would enable finer control and prepare for future swarm features.
