# MoAI Hooks Comparison

> Comprehensive comparison of Claude-Flow and MoAI hook systems

## Overview

This document provides a detailed comparison between Claude-Flow's and MoAI's hook systems, identifying gaps and opportunities for enhancement.

---

## Hook System Comparison

### Claude-Flow Hooks (Complete)

```
Pre-Operation Hooks:
├── PreTask          - Before task creation
├── PreAgent         - Before agent spawn
├── PreFile          - Before file operation
└── PreSwarm         - Before swarm init

Post-Operation Hooks:
├── PostTask         - After task completion
├── PostAgent        - After agent termination
├── PostFile         - After file operation
└── PostSwarm        - After swarm shutdown

Session Hooks:
├── SessionStart     - Session begins
├── SessionEnd       - Session ends
├── SessionResume    - Session continues
└── SessionPause     - Session paused

Coordination Hooks:
├── OnConsensusStart - Consensus begins
├── OnConsensusVote  - Agent votes
├── OnConsensusReached - Agreement reached
├── OnConsensusFailed - No agreement
├── OnConflictDetected - Conflict found
├── OnConflictResolved - Conflict resolved
├── OnHeartbeat      - Health check
├── OnHeartbeatMissed - Agent unresponsive
├── OnSwarmInit      - Swarm initialized
├── OnAgentJoin      - Agent joins
├── OnAgentLeave     - Agent leaves
└── OnSwarmShutdown  - Swarm terminates
```

### MoAI Hooks (Current)

```
Session Hooks:
├── SessionStart     - Session initialization
└── SessionEnd       - Session cleanup
    ├── metrics      - Save metrics
    ├── work_state   - Save state
    ├── cleanup      - Temp files
    ├── warnings     - Uncommitted changes
    └── summary      - Generate summary

User Input Hooks:
└── PreUserPromptSubmit - Before input processing

Configuration:
├── timeout_ms       - Hook timeout (2000ms)
└── graceful_degradation - Continue on failure
```

---

## Feature Matrix

| Hook Category | Feature | Claude-Flow | MoAI | Gap |
|---------------|---------|-------------|------|-----|
| **Pre-Operation** | PreTask | ✅ | ❌ | HIGH |
| | PreAgent | ✅ | ❌ | HIGH |
| | PreFile | ✅ | ❌ | MEDIUM |
| | PreSwarm | ✅ | ❌ | LOW |
| | PreUserPrompt | ❌ | ✅ | N/A |
| **Post-Operation** | PostTask | ✅ | ❌ | HIGH |
| | PostAgent | ✅ | ❌ | HIGH |
| | PostFile | ✅ | ❌ | MEDIUM |
| | PostSwarm | ✅ | ❌ | LOW |
| **Session** | SessionStart | ✅ | ✅ | NONE |
| | SessionEnd | ✅ | ✅ | NONE |
| | SessionResume | ✅ | ⚠️ | LOW |
| | SessionPause | ✅ | ❌ | LOW |
| **Coordination** | Consensus | ✅ | ❌ | HIGH |
| | Conflict | ✅ | ❌ | HIGH |
| | Heartbeat | ✅ | ❌ | MEDIUM |
| | Swarm Events | ✅ | ❌ | HIGH |

---

## Configuration Comparison

### Claude-Flow Configuration

```json
{
  "hooks": {
    "PreTask": {
      "enabled": true,
      "timeout_ms": 5000,
      "blocking": true,
      "retry": { "enabled": true, "max_attempts": 3 },
      "command": "pre-task.sh",
      "args": ["${TASK_TYPE}", "${TASK_PRIORITY}"]
    },
    "PostTask": {
      "enabled": true,
      "timeout_ms": 3000,
      "blocking": false,
      "async": true,
      "command": "post-task.sh"
    },
    "OnConsensusReached": {
      "enabled": true,
      "timeout_ms": 5000,
      "command": "consensus.sh"
    },
    "OnHeartbeat": {
      "enabled": true,
      "interval_ms": 5000,
      "threshold": 3,
      "command": "heartbeat.sh"
    }
  }
}
```

### MoAI Configuration

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true
  },
  "session_end": {
    "enabled": true,
    "metrics": {
      "enabled": true,
      "save_location": ".moai/logs/sessions/"
    },
    "work_state": {
      "enabled": true,
      "save_location": ".moai/memory/last-session-state.json"
    },
    "cleanup": {
      "enabled": true,
      "temp_files": true,
      "cache_files": true,
      "patterns": [".moai/temp/*", ".moai/cache/*.tmp"]
    },
    "warnings": {
      "uncommitted_changes": true
    },
    "summary": {
      "enabled": true,
      "max_lines": 5
    }
  }
}
```

---

## MoAI Strengths

### 1. Session End is Comprehensive

MoAI's SessionEnd hook is well-designed:

- **Metrics**: Saves usage statistics
- **Work State**: Preserves context
- **Cleanup**: Automatic temp file removal
- **Warnings**: Uncommitted changes alert
- **Summary**: Session summary generation

### 2. Graceful Degradation

```json
{
  "hooks": {
    "graceful_degradation": true
  }
}
```

MoAI continues operation even if hooks fail.

### 3. Document Management Integration

MoAI hooks integrate with document management:

```json
{
  "document_management": {
    "validation": {
      "on_session_end": true
    },
    "cleanup": {
      "schedule": "session_end"
    }
  }
}
```

### 4. Configuration-Driven

All hook behavior controlled via JSON config.

---

## MoAI Gaps

### 1. No Operation-Level Hooks

MoAI lacks hooks for individual operations:

```
❌ PreTask   - Cannot validate before task execution
❌ PostTask  - Cannot log/track task completion
❌ PreAgent  - Cannot control agent spawning
❌ PostAgent - Cannot cleanup after agents
```

### 2. No Coordination Hooks

No multi-agent support:

```
❌ OnConsensus - No consensus mechanism
❌ OnConflict  - No conflict resolution
❌ OnHeartbeat - No health monitoring
❌ OnSwarmInit - No swarm support
```

### 3. Limited Pre-Processing

Only `PreUserPromptSubmit` exists:

```
✅ PreUserPromptSubmit - User input validation
❌ PreFile             - No file operation control
❌ PreExecution        - No execution validation
```

---

## Recommended Enhancements

### Priority 1: Operation Hooks (P1)

Add basic operation hooks:

```json
{
  "hooks": {
    "operation": {
      "PreTask": {
        "enabled": true,
        "timeout_ms": 5000,
        "command": ".moai/hooks/pre-task.sh"
      },
      "PostTask": {
        "enabled": true,
        "timeout_ms": 3000,
        "async": true,
        "command": ".moai/hooks/post-task.sh"
      },
      "PreAgent": {
        "enabled": true,
        "timeout_ms": 3000,
        "command": ".moai/hooks/pre-agent.sh"
      },
      "PostAgent": {
        "enabled": true,
        "timeout_ms": 3000,
        "async": true,
        "command": ".moai/hooks/post-agent.sh"
      }
    }
  }
}
```

### Priority 2: File Operation Hooks (P2)

Add file operation tracking:

```json
{
  "hooks": {
    "file": {
      "PreFile": {
        "enabled": true,
        "operations": ["write", "edit", "delete"],
        "command": ".moai/hooks/pre-file.sh"
      },
      "PostFile": {
        "enabled": true,
        "operations": ["write", "edit"],
        "verify_integrity": true,
        "command": ".moai/hooks/post-file.sh"
      }
    }
  }
}
```

### Priority 3: Coordination Hooks (P3)

For future multi-agent support:

```json
{
  "hooks": {
    "coordination": {
      "enabled": false,
      "OnAgentStart": { "command": ".moai/hooks/agent-start.sh" },
      "OnAgentEnd": { "command": ".moai/hooks/agent-end.sh" },
      "OnConsensus": { "command": ".moai/hooks/consensus.sh" },
      "OnConflict": { "command": ".moai/hooks/conflict.sh" }
    }
  }
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. Add hook infrastructure to support multiple hook types
2. Implement PreTask/PostTask hooks
3. Implement PreAgent/PostAgent hooks
4. Update config schema

### Phase 2: File Hooks (Week 3-4)

1. Implement PreFile/PostFile hooks
2. Add file integrity verification
3. Integrate with document management

### Phase 3: Coordination (Month 2+)

1. Design coordination hook architecture
2. Implement basic agent lifecycle hooks
3. (Future) Add consensus/conflict hooks with swarm

---

## Migration Path

### Step 1: Preserve Existing

Keep MoAI's current hook system intact:

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true,
    "legacy": true
  }
}
```

### Step 2: Add New Hook Categories

Extend with new categories:

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true,
    "operation": { /* new */ },
    "file": { /* new */ },
    "coordination": { /* new */ }
  }
}
```

### Step 3: Gradual Rollout

Enable new hooks incrementally:

```json
{
  "hooks": {
    "operation": {
      "PreTask": { "enabled": false },
      "PostTask": { "enabled": false }
    }
  }
}
```

---

## Summary

| Aspect | Claude-Flow | MoAI | Recommendation |
|--------|-------------|------|----------------|
| Hook Types | 20+ types | 4 types | Add 8+ types |
| Pre-Operation | 4 hooks | 1 hook | Add PreTask, PreAgent |
| Post-Operation | 4 hooks | 0 hooks | Add PostTask, PostAgent |
| Session | 4 hooks | 2 hooks | Add SessionResume |
| Coordination | 12 hooks | 0 hooks | Future with swarm |
| Configuration | Complex | Simple | Keep simple, extend |
| Graceful Degradation | Yes | Yes | Already good |

MoAI's hook system is simpler but effective for current needs. Enhancements should focus on operation-level hooks first, maintaining MoAI's configuration simplicity while adding Claude-Flow's granular control.
