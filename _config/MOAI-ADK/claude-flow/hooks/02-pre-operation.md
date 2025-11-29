# Pre-Operation Hooks

> Validation and authorization before operations

## Overview

Pre-operation hooks execute BEFORE an operation starts, providing opportunities for validation, authorization, and setup.

---

## Hook Types

### 1. PreTask Hook

Triggered before task creation.

```javascript
// Hook configuration
{
  "PreTask": {
    "enabled": true,
    "timeout_ms": 5000,
    "actions": ["validate", "authorize", "log"]
  }
}
```

**Use Cases**:
- Validate task parameters
- Check authorization
- Log task initiation
- Resource availability check

### 2. PreAgent Hook

Triggered before agent spawn.

```javascript
// Hook configuration
{
  "PreAgent": {
    "enabled": true,
    "timeout_ms": 3000,
    "actions": ["resource_check", "quota_check"]
  }
}
```

**Use Cases**:
- Check agent quota
- Verify resource availability
- Validate agent type
- Setup agent environment

### 3. PreFile Hook

Triggered before file operations.

```javascript
// Hook configuration
{
  "PreFile": {
    "enabled": true,
    "timeout_ms": 2000,
    "actions": ["path_validate", "permission_check"]
  }
}
```

**Use Cases**:
- Validate file paths
- Check permissions
- Backup before modification
- Lock file for editing

### 4. PreSwarm Hook

Triggered before swarm initialization.

```javascript
// Hook configuration
{
  "PreSwarm": {
    "enabled": true,
    "timeout_ms": 10000,
    "actions": ["env_setup", "resource_allocation"]
  }
}
```

**Use Cases**:
- Allocate resources
- Setup network topology
- Initialize shared memory
- Configure coordination

---

## Implementation Patterns

### Pattern 1: Validation Hook

```bash
#!/bin/bash
# pre-task-validate.sh

TASK_JSON="$1"

# Parse task parameters
TASK_TYPE=$(echo "$TASK_JSON" | jq -r '.type')
PRIORITY=$(echo "$TASK_JSON" | jq -r '.priority')

# Validate
if [[ -z "$TASK_TYPE" ]]; then
    echo "ERROR: Task type required"
    exit 1
fi

if [[ "$PRIORITY" == "critical" && "$USER_ROLE" != "admin" ]]; then
    echo "ERROR: Critical tasks require admin"
    exit 1
fi

echo "VALIDATED"
exit 0
```

### Pattern 2: Authorization Hook

```bash
#!/bin/bash
# pre-agent-authorize.sh

AGENT_TYPE="$1"
USER_ID="$2"

# Check agent quota
CURRENT_AGENTS=$(get_agent_count "$USER_ID")
MAX_AGENTS=10

if [[ $CURRENT_AGENTS -ge $MAX_AGENTS ]]; then
    echo "ERROR: Agent quota exceeded"
    exit 1
fi

# Check agent type permission
if ! user_can_spawn "$USER_ID" "$AGENT_TYPE"; then
    echo "ERROR: Not authorized for $AGENT_TYPE"
    exit 1
fi

exit 0
```

### Pattern 3: Resource Check Hook

```bash
#!/bin/bash
# pre-swarm-resources.sh

TOPOLOGY="$1"
MAX_AGENTS="$2"

# Check memory
AVAILABLE_MEM=$(free -m | awk '/^Mem:/{print $7}')
REQUIRED_MEM=$((MAX_AGENTS * 512))  # 512MB per agent

if [[ $AVAILABLE_MEM -lt $REQUIRED_MEM ]]; then
    echo "ERROR: Insufficient memory"
    exit 1
fi

# Check CPU
LOAD=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1)
if (( $(echo "$LOAD > 8.0" | bc -l) )); then
    echo "ERROR: System load too high"
    exit 1
fi

exit 0
```

---

## Hook Flow Diagram

```
User Request
    │
    ▼
┌─────────────────────────────────┐
│         PRE-OPERATION           │
├─────────────────────────────────┤
│                                 │
│  1. PreTask Hook                │
│     ├── Validate parameters     │
│     ├── Check authorization     │
│     └── Log initiation          │
│                                 │
│  2. PreAgent Hook (if needed)   │
│     ├── Check quota             │
│     ├── Verify resources        │
│     └── Setup environment       │
│                                 │
│  3. PreFile Hook (if needed)    │
│     ├── Validate paths          │
│     ├── Check permissions       │
│     └── Create backups          │
│                                 │
└────────────────┬────────────────┘
                 │
                 ▼
         [Execute Operation]
```

---

## Error Handling

### Hook Return Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue operation |
| 1 | Validation failed | Block operation |
| 2 | Authorization failed | Block + notify |
| 3 | Resource unavailable | Retry later |

### Graceful Degradation

```json
{
  "hooks": {
    "PreTask": {
      "enabled": true,
      "graceful_degradation": true,
      "on_timeout": "continue",
      "on_error": "log_and_continue"
    }
  }
}
```

---

## MoAI Current State

### Existing Pre-Hooks

MoAI has `PreUserPromptSubmit`:

```json
{
  "hooks": {
    "PreUserPromptSubmit": {
      "enabled": true,
      "command": "script.sh"
    }
  }
}
```

### Gap Analysis

| Pre-Hook | Claude-Flow | MoAI |
|----------|-------------|------|
| PreTask | Yes | No |
| PreAgent | Yes | No |
| PreFile | Yes | No |
| PreSwarm | Yes | No |
| PreUserPrompt | No | Yes |

---

## Recommendation

### Add to MoAI

```json
{
  "hooks": {
    "PreTask": {
      "enabled": true,
      "timeout_ms": 5000,
      "graceful_degradation": true,
      "command": ".moai/hooks/pre-task.sh"
    },
    "PreAgent": {
      "enabled": true,
      "timeout_ms": 3000,
      "graceful_degradation": true,
      "command": ".moai/hooks/pre-agent.sh"
    }
  }
}
```

### Benefits

1. **Validation**: Catch errors before execution
2. **Authorization**: Control access to operations
3. **Logging**: Track all operation attempts
4. **Resource management**: Prevent overload
