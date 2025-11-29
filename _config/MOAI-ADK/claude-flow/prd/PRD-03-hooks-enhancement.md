# PRD-03: Hooks Enhancement

> Expand MoAI's hook system with operation-level hooks

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P1 (Critical) |
| **Effort** | Medium (3-4 weeks) |
| **Impact** | Medium |
| **Type** | Infrastructure Enhancement |

---

## Problem Statement

MoAI has basic session hooks (SessionStart, SessionEnd) but lacks fine-grained operation hooks for tasks, agents, and file operations. Claude-Flow's comprehensive hook system provides granular control at every operation level.

### Current MoAI Hooks

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true
  },
  "session_end": {
    "enabled": true,
    "metrics": { "enabled": true },
    "work_state": { "enabled": true },
    "cleanup": { "enabled": true }
  }
}
```

**Available Hooks**:
- SessionStart
- SessionEnd
- PreUserPromptSubmit

### Missing Hooks (From Claude-Flow)

```
Pre-Operation:
├── PreTask      ❌
├── PreAgent     ❌
├── PreFile      ❌
└── PreSwarm     ❌

Post-Operation:
├── PostTask     ❌
├── PostAgent    ❌
├── PostFile     ❌
└── PostSwarm    ❌

Coordination:
├── OnConsensus  ❌
├── OnConflict   ❌
└── OnHeartbeat  ❌
```

---

## Solution

### New Hook Categories

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true,

    "operation": {
      "PreTask": {
        "enabled": true,
        "command": ".moai/hooks/pre-task.sh",
        "blocking": true
      },
      "PostTask": {
        "enabled": true,
        "command": ".moai/hooks/post-task.sh",
        "blocking": false,
        "async": true
      },
      "PreAgent": {
        "enabled": true,
        "command": ".moai/hooks/pre-agent.sh"
      },
      "PostAgent": {
        "enabled": true,
        "command": ".moai/hooks/post-agent.sh"
      }
    },

    "file": {
      "PreFile": {
        "enabled": false,
        "operations": ["write", "edit", "delete"]
      },
      "PostFile": {
        "enabled": false,
        "operations": ["write", "edit"]
      }
    },

    "coordination": {
      "enabled": false,
      "OnAgentStart": { "command": ".moai/hooks/agent-start.sh" },
      "OnAgentEnd": { "command": ".moai/hooks/agent-end.sh" }
    }
  }
}
```

---

## Implementation Plan

### Phase 1: Operation Hooks (Week 1-2)

**Task 1.1**: PreTask Hook

```bash
#!/bin/bash
# .moai/hooks/pre-task.sh

TASK_TYPE="$1"
AGENT_TYPE="$2"
PROMPT="$3"

# Log task initiation
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") PRE_TASK: $AGENT_TYPE" >> .moai/logs/tasks.log

# Validate (optional)
# Return 0 to continue, non-zero to block

exit 0
```

**Task 1.2**: PostTask Hook

```bash
#!/bin/bash
# .moai/hooks/post-task.sh

TASK_ID="$1"
AGENT_TYPE="$2"
RESULT="$3"
DURATION="$4"

# Log task completion
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") POST_TASK: $AGENT_TYPE result=$RESULT duration=${DURATION}ms" >> .moai/logs/tasks.log

# Collect metrics
if [[ -f ".moai/metrics/tasks.json" ]]; then
    # Append metrics
    jq ".tasks += [{\"agent\":\"$AGENT_TYPE\",\"result\":\"$RESULT\",\"duration\":$DURATION}]" .moai/metrics/tasks.json > .moai/metrics/tasks.json.tmp
    mv .moai/metrics/tasks.json.tmp .moai/metrics/tasks.json
fi

exit 0
```

### Phase 2: Agent Hooks (Week 2-3)

**Task 2.1**: PreAgent Hook

```bash
#!/bin/bash
# .moai/hooks/pre-agent.sh

AGENT_ID="$1"
AGENT_TYPE="$2"

# Check agent quota (optional)
CURRENT=$(cat .moai/cache/active-agents.count 2>/dev/null || echo "0")
MAX_AGENTS=10

if [[ $CURRENT -ge $MAX_AGENTS ]]; then
    echo "ERROR: Agent quota exceeded"
    exit 1
fi

# Increment counter
echo $((CURRENT + 1)) > .moai/cache/active-agents.count

exit 0
```

**Task 2.2**: PostAgent Hook

```bash
#!/bin/bash
# .moai/hooks/post-agent.sh

AGENT_ID="$1"
AGENT_TYPE="$2"
TASKS_COMPLETED="$3"

# Decrement counter
CURRENT=$(cat .moai/cache/active-agents.count 2>/dev/null || echo "1")
echo $((CURRENT - 1)) > .moai/cache/active-agents.count

# Log agent completion
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") AGENT_END: $AGENT_TYPE tasks=$TASKS_COMPLETED" >> .moai/logs/agents.log

exit 0
```

### Phase 3: Configuration Integration (Week 3-4)

**Task 3.1**: Update config.json schema

Add new hook categories to configuration schema.

**Task 3.2**: Update CLAUDE.md

Document new hooks and usage patterns.

**Task 3.3**: Create default hook scripts

Provide starter scripts in `.moai/hooks/`.

---

## Configuration Schema

### Full Hook Configuration

```json
{
  "hooks": {
    "timeout_ms": 2000,
    "graceful_degradation": true,

    "operation": {
      "PreTask": {
        "enabled": true,
        "timeout_ms": 5000,
        "blocking": true,
        "command": ".moai/hooks/pre-task.sh",
        "args": ["${TASK_TYPE}", "${AGENT_TYPE}", "${PROMPT}"]
      },
      "PostTask": {
        "enabled": true,
        "timeout_ms": 3000,
        "blocking": false,
        "async": true,
        "command": ".moai/hooks/post-task.sh",
        "args": ["${TASK_ID}", "${AGENT_TYPE}", "${RESULT}", "${DURATION}"]
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
    },

    "file": {
      "PreFile": {
        "enabled": false,
        "operations": ["write", "edit", "delete"],
        "command": ".moai/hooks/pre-file.sh"
      },
      "PostFile": {
        "enabled": false,
        "operations": ["write", "edit"],
        "command": ".moai/hooks/post-file.sh"
      }
    },

    "coordination": {
      "enabled": false,
      "OnAgentStart": { "enabled": false },
      "OnAgentEnd": { "enabled": false }
    }
  }
}
```

### Variable Substitution

| Variable | Available In | Description |
|----------|--------------|-------------|
| `${TASK_ID}` | PostTask | Unique task identifier |
| `${TASK_TYPE}` | PreTask | Type of task |
| `${AGENT_TYPE}` | Pre/PostTask, Pre/PostAgent | Agent subagent_type |
| `${PROMPT}` | PreTask | Task prompt |
| `${RESULT}` | PostTask | success/failure |
| `${DURATION}` | PostTask | Duration in ms |
| `${AGENT_ID}` | Pre/PostAgent | Agent instance ID |
| `${FILE_PATH}` | Pre/PostFile | File being operated on |
| `${OPERATION}` | Pre/PostFile | write/edit/delete |

---

## Acceptance Criteria

- [ ] PreTask hook implemented and tested
- [ ] PostTask hook implemented and tested
- [ ] PreAgent hook implemented and tested
- [ ] PostAgent hook implemented and tested
- [ ] Configuration schema updated
- [ ] Default hook scripts created
- [ ] Documentation updated
- [ ] Backward compatibility maintained

---

## Impact Assessment

### Capability Gain

| Feature | Before | After |
|---------|--------|-------|
| Task logging | None | Automatic |
| Agent tracking | None | Full lifecycle |
| Validation | None | Pre-operation checks |
| Metrics | Session only | Per-task, per-agent |

### Compatibility

All changes are additive:
- Existing hooks unchanged
- New hooks disabled by default
- Graceful degradation preserved

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance overhead | Medium | Low | Async execution, timeouts |
| Script errors | Medium | Low | Graceful degradation |
| Backward compat | Low | Medium | Default disabled |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Hook execution success | > 99% |
| Performance overhead | < 5% |
| User adoption | 25% enable hooks |

---

## Related Documents

- [Hook Overview](../hooks/01-hook-overview.md)
- [Pre-Operation Hooks](../hooks/02-pre-operation.md)
- [Post-Operation Hooks](../hooks/03-post-operation.md)
- [MoAI Hooks Comparison](../hooks/06-moai-hooks-comparison.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Week 1:   PreTask, PostTask implementation
Week 2:   PreAgent, PostAgent implementation
Week 3:   Configuration integration
Week 4:   Documentation, testing, rollout
```

Total: ~4 weeks
